import os
import pandas as pd
import json

from datetime import datetime
import re

def parse_timestamp(text):
    try:
        return datetime.strptime(text[:15], "%b %d %H:%M:%S").replace(year=datetime.now().year).isoformat()
    except Exception:
        return None

def extract_source(text):
    match = re.search(r"([a-zA-Z0-9_-]+)\[\d+\]:", text)
    return match.group(1) if match else "unknown"


def extract_features_from_log(log_dict):
    message = log_dict.get("raw", "")
    timestamp = log_dict.get("timestamp", "")

    length = len(message)
    contains_ip = int(bool(re.search(r"\b\d{1,3}(?:\.\d{1,3}){3}\b", message)))

    hour = -1
    try:
        hour = datetime.fromisoformat(timestamp).hour
    except:
        pass

    return {
        "length": length,
        "hour": hour,
        "contains_ip": contains_ip
    }

