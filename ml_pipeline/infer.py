import json
import sys
import pandas as pd
from joblib import load
from preprocess import extract_features_from_log


model = load("ml_pipeline/model.joblib")

def infer_log(log_json):
    feats = extract_features_from_log(log_json)
    df = pd.DataFrame([feats])
    result = model.predict(df)[0]
    return "anomaly" if result == -1 else "normal"

if __name__ == "__main__":
    log_input = json.loads(sys.stdin.read())
    print(infer_log(log_input))

