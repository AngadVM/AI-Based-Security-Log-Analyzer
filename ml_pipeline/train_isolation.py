# ml_pipeline/train_isolation.py
import os
import json
import re
import pandas as pd
from datetime import datetime
from sklearn.ensemble import IsolationForest
from joblib import dump

def parse_timestamp(raw_line):
    """Extracts datetime from syslog-style log string."""
    try:
        ts = datetime.strptime(raw_line[:15], "%b %d %H:%M:%S")
        return ts.replace(year=datetime.now().year)
    except Exception:
        return None

def extract_features(raw):
    """Returns a feature dictionary from a log line."""
    timestamp = parse_timestamp(raw)
    if not timestamp:
        return None

    return {
        "length": len(raw),
        "contains_ip": int(bool(re.search(r"\b\d{1,3}(?:\.\d{1,3}){3}\b", raw))),
        "hour": timestamp.hour
    }

def load_parsed_logs(folder):
    """Loads all .json logs and converts to feature dicts."""
    data = []

    for filename in os.listdir(folder):
        if filename.endswith(".json"):
            with open(os.path.join(folder, filename)) as f:
                for line in f:
                    try:
                        log = json.loads(line.strip())
                        raw = log.get("raw", "")
                        if not raw:
                            continue
                        feats = extract_features(raw)
                        if feats:
                            data.append(feats)
                    except Exception:
                        continue

    return pd.DataFrame(data)

def main():
    folder = "data/parsed_logs"
    df = load_parsed_logs(folder)

    if df.empty:
        print(" No valid log entries found to train on.")
        return

    print(f" Loaded {len(df)} valid log entries.")

    model = IsolationForest(n_estimators=100, contamination=0.05, random_state=42)
    model.fit(df)

    model_path = "ml_pipeline/isolation_forest.joblib"
    dump(model, model_path)
    print(f" Isolation Forest model saved to {model_path}")

if __name__ == "__main__":
    main()

