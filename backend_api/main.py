from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from elasticsearch import Elasticsearch
from datetime import datetime
import json
import os, sys
from websocket_manager import manager
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from ml_pipeline.infer import infer_log

  
app = FastAPI()
es = Elasticsearch("http://localhost:9200")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.websocket("/ws/logs")  # ✅ NEW WebSocket route
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except Exception:
        manager.disconnect(websocket)

@app.post("/upload")
async def upload_log_file(file: UploadFile = File(...)):
    contents = await file.read()
    lines = contents.decode("utf-8").splitlines()

    for line in lines:
        if not line.strip():
            continue

        log_dict = {
            "raw": line,
            "timestamp": datetime.utcnow().isoformat()
        }

        enriched = infer_log(log_dict)
        enriched["ingested_at"] = datetime.utcnow().isoformat()

        es.index(index="classified-logs", document=enriched)
        await manager.broadcast(enriched)  # ✅ WebSocket broadcast

    return {"status": "uploaded"}

@app.post("/ingest")
async def ingest_log(request: Request):
    log_data = await request.json()

    if "timestamp" not in log_data:
        log_data["timestamp"] = datetime.utcnow().isoformat()

    parsed = infer_log(log_data)
    parsed["ingested_at"] = datetime.utcnow().isoformat()

    es.index(index="classified-logs", document=parsed)
    await manager.broadcast(parsed)  # ✅ WebSocket broadcast
    return {"status": "received", "label": parsed["prediction"], "threat_type": parsed["threat_type"]}

@app.get("/logs")
def get_logs(size: int = 100):
    try:
        res = es.search(
            index="classified-logs",
            size=size,
            sort=[{"timestamp": {"order": "desc"}}]
        )
        hits = [doc["_source"] for doc in res["hits"]["hits"]]
        return JSONResponse(content=hits)
    except Exception as e:
        return {"error": str(e)}
