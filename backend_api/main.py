import os, sys, tempfile
from fastapi import FastAPI, Request, UploadFile, File, WebSocket
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from elasticsearch import Elasticsearch
from datetime import datetime

from websocket_manager import manager

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
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

@app.get("/")
def root():
    return {"message": "API is working"}

@app.post("/ingest")
async def ingest_log(request: Request):
    log_data = await request.json()

    if "timestamp" not in log_data:
        log_data["timestamp"] = datetime.utcnow().isoformat()

    parsed = infer_log(log_data)
    parsed["ingested_at"] = datetime.utcnow().isoformat()
    await manager.broadcast(parsed)

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
    print("Received upload:", file.filename)
    success_count = 0

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

                if not parsed or not parsed.get("raw") or not parsed.get("timestamp"):
                    continue

                parsed["ingested_at"] = datetime.utcnow().isoformat()

                es.index(index="classified-logs", document=parsed)
                await manager.broadcast(parsed)
                success_count += 1
                print(f"Ingested from file: {parsed['prediction']} - {parsed['threat_type']}")

        return {
            "status": "success",
            "message": f"{file.filename} processed with {success_count} logs."
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        os.remove(temp_path)

@app.websocket("/ws/logs")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket)
