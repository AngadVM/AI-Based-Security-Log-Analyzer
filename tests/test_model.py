import pytest
from joblib import load
from ml_pipeline.preprocess import extract_features_from_log
import pandas as pd

model = load("ml_pipeline/model.joblib")

def predict_label(log):
    feats = extract_features_from_log(log)
    df = pd.DataFrame([feats])
    result = model.predict(df)[0]
    return "anomaly" if result == -1 else "normal"

def test_normal_log():
    log = {
        "timestamp": "2025-06-16T10:20:00",
        "message": "Connection from 192.168.1.1 established successfully"
    }
    label = predict_label(log)
    assert label == "normal"

def test_anomaly_log():
    log = {
        "timestamp": "2025-06-16T03:10:00",
        "message": "ERROR: Unauthorized access attempt from 45.33.32.156"
    }
    label = predict_label(log)
    assert label == "anomaly"

def test_junk_log():
    log = {
        "timestamp": "",
        "message": "xyz123#&!@(*&!^&@#()_+= junk data"
    }
    label = predict_label(log)
    assert label == "anomaly" or label == "normal"  # we just test no crash here

