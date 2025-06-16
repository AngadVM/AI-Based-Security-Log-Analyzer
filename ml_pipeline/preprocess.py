import os
import pandas as pd 
import json 
import re
from datetime import datetime 

def extract_features_from_log(log_dict):
    message = log_dict.get("message","")
    timestamp = log_dict.get("timestamp","")

    try:
        ts = datetime.fromisoformat(timestamp)
        hour = ts.hour 
    except ValueError:
        try:
            ts = datetime.strptime(timestamp, "%b %d %H:%M:%S")
            hour = ts.hour
        except ValueError:
            hour = -1

    # Basic Features 
    features = {
        "length": len(message),
        "num_digits": sum(c.isdigit() for c in message),
        "num_upper": sum(c.isupper() for c in message),
        "contains_error": int("error" in message.lower()),
        "contains_failed": int("fail" in message.lower()),
        "hour": hour
    }
    return features

def preprocess_logs(input_dir="data/parsed_logs"):
    all_features = []

    for filename in os.listdir(input_dir):
        if filename.endswith(".json"):
            with open(os.path.join(input_dir, filename)) as f:
                for line in f:
                    try:
                        log = json.loads(line)
                        feats = extract_features_from_log(log)
                        all_features.append(feats)
                    except Exception:
                        continue

    return pd.DataFrame(all_features)

