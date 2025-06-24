
import re
import pandas as pd
from datetime import datetime
from joblib import load

# Load trained classifier
model = load("ml_pipeline/classic_classifier.joblib")

def parse_timestamp(raw):
    try:
        ts = datetime.strptime(raw[:15], "%b %d %H:%M:%S")
        return ts.replace(year=datetime.now().year).isoformat()
    except Exception:
        return datetime.utcnow().isoformat()

def extract_features_from_raw(raw, timestamp):
    try:
        ts = datetime.fromisoformat(timestamp)
    except Exception:
        ts = datetime.utcnow()

    def has_keyword(text, keyword):
        return int(keyword in text.lower())

    features = {
        "length": len(raw),
        "contains_ip": int(bool(re.search(r"\b\d{1,3}(?:\.\d{1,3}){3}\b", raw))),
        "hour": ts.hour,
        "failed": has_keyword(raw, "failed"),
        "connection": has_keyword(raw, "connection"),
        "invalid": has_keyword(raw, "invalid"),
        "malicious": has_keyword(raw, "malicious"),
        "scan": has_keyword(raw, "scan"),
    }
    return features

def infer_log(log_dict):
    raw = log_dict.get("raw", "")
    timestamp = log_dict.get("timestamp", parse_timestamp(raw))

    features = extract_features_from_raw(raw, timestamp)
    df = pd.DataFrame([features])

    pred = model.predict(df)[0]

    return {
        "raw": raw,
        "timestamp": timestamp,
        "prediction": "anomaly" if pred != "normal" else "normal",
        "threat_type": pred
    }

