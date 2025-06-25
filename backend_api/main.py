import os, tempfile
import shutil
from fastapi import FastAPI, Request, WebSocket
from fastapi import UploadFile, File 
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from elasticsearch import Elasticsearch
from datetime import datetime
from backend_api.websocket_manager import manager
from ml_pipeline.infer import infer_log

# Connect to Elasticsearch
es = Elasticsearch("http://localhost:9200")
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/ingest")
async def ingest_log(request: Request):
    log_data = await request.json()

    # Add fallback timestamp if missing
    if "timestamp" not in log_data:
        log_data["timestamp"] = datetime.utcnow().isoformat()

    # Inference using Isolation Forest + RandomForestClassification 
    parsed = infer_log(log_data)
    parsed["ingested_at"] = datetime.utcnow().isoformat()
    await manager.broadcast(parsed)

    # Store in Elasticsearch
    es.index(index="classified-logs", document=parsed)

    print(f"Stored log | Prediction: {parsed['prediction']} | Threat: {parsed['threat_type']}")
    return {"status": "received", "label": parsed["prediction"], "threat_type": parsed["threat_type"]}

@app.get("/logs")
def get_logs(size: int = 100):
    try:
        res = es.search(
            index="classified-logs",
            size=size,
            sort=[{"ingested_at": {"order": "desc"}}]
        )
        hits = [doc["_source"] for doc in res["hits"]["hits"]]
        return JSONResponse(content=hits)
    except Exception as e:
        return {"error": str(e)}

@app.post("/upload")
async def upload_log_file(file: UploadFile = File(...)):
    # Create a temp file
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        content = await file.read()
        tmp.write(content)
        temp_path = tmp.name

    try:
        with open(temp_path, "r") as f:
            for line in f:
                raw = line.strip()
                if not raw:
                    continue

                log_obj = {
                    "raw": raw,
                    "timestamp": parse_timestamp(raw)
                }

                parsed = infer_log(log_obj)
                parsed["ingested_at"] = datetime.utcnow().isoformat()
                await manager.broadcast(parsed)

                es.index(index="classified-logs", document=parsed)
                print(f"Ingested from file: {parsed['prediction']} - {parsed['threat_type']}")

        return {"status": "success", "message": f"{file.filename} processed."}

    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        os.remove(temp_path)

def parse_timestamp(raw_line):
    try:
        ts = datetime.strptime(raw_line[:15], "%b %d %H:%M:%S")
        return ts.replace(year=datetime.now().year).isoformat()
    except Exception:
        return datetime.utcnow().isoformat()

@app.websocket("/ws/logs")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
            
    except:
        manager.disconnect(websocket)


