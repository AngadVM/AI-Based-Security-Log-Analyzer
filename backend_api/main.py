from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from joblib import load
import pandas as pd 
import json
from parser.log_parser import parse_syslog 
from ml_pipeline.preprocess import extract_features_from_log
from elasticsearch import Elasticsearch 
from datetime import datetime 
from fastapi.middleware.cors import CORSMiddleware


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

# Load model at startup
model = load("ml_pipeline/model.joblib")

@app.post("/ingest")
async def ingest_log(request: Request):
    raw_body = await request.body()
    raw_text = raw_body.decode()

    parsed = parse_syslog(raw_text)

    # Adding timestamp if missing
    if 'timestamp' not in parsed:
        parsed['timestamp'] = datetime.utcnow().isoformat()

    # Inference
    feats = extract_features_from_log(parsed)
    df = pd.DataFrame([feats])
    prediction = model.predict(df)[0]
    label = "anomaly" if prediction == -1 else "normal"

    
    parsed["prediction"] = label
    parsed["ingested_at"] = datetime.utcnow().isoformat()
    parsed["raw"] = raw_text 

    # Store in Elasticsearch
    es.index(index="classified-logs", document=parsed)

    print(f"Stored log | Predicted: {label} | Raw: {raw_text}")
    return {"status": "received", "label": label}



@app.get("/logs")
def get_logs(size: int = 100):
    try:
        res = es.search(
            index="classified-logs",
            size=100,
            sort=[{"timestamp": {"order": "desc"}}]
        )
        hits = [doc["_source"] for doc in res["hits"]["hits"]]
        return JSONResponse(content=hits)
    except Exception as e:
        return {"error": str(e)}

