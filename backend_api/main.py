from fastapi import FastAPI, Request
from joblib import load
import pandas as pd 
import json
from parser.log_parser import parse_syslog 
from ml_pipeline.preprocess import extract_features_from_log


app = FastAPI()

# Load model at startup
model = load("ml_pipeline/model.joblib")

@app.post("/ingest")
async def ingest_log(request: Request):
    raw_body = await request.body()
    raw_text = raw_body.decode()

    # Using a parser (syslog)
    parsed = parse_syslog(raw_text)

    # Adding timestamp if missing
    if 'timestamp' not in parsed:
        parsed['timestamp'] = "2025-06-16T00:00:00"


    # Extract features + run inference
    feats = extract_features_from_log(parsed)
    df = pd.DataFrame([feats])
    prediction = model.predict(df)[0]
    label = "anomaly" if prediction == -1 else "normal"

    # Combine parsed + label
    parsed["prediction"] = label 

    print(f"Log received | Predicted: {label} | Data: {parsed}")
    return {"status": "received", "label": label}

   
