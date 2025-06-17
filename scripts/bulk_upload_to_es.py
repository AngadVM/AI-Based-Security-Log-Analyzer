import os
import json
import time 
from datetime import datetime
from elasticsearch import Elasticsearch

es = Elasticsearch("http://localhost:9200")


def parse_timestamp(ts):
    try:
        # Try parsing formats like 'Jun 15 04:06:20'
        parsed = datetime.strptime(ts, "%b %d %H:%M:%S")
        # Assign today's year or fallback to UTC now
        parsed = parsed.replace(year=datetime.utcnow().year)
        return parsed.isoformat()
    except Exception:
        # fallback to current UTC
        return datetime.utcnow().isoformat()


def upload_logs(folder="data/parsed_logs"):
    for filename in os.listdir(folder):
        if filename.endswith(".json"):
            path = os.path.join(folder, filename)
            with open(path, "r") as f:
                for line in f:
                    try:
                        log = json.loads(line.strip())
                        log["timestamp"] = parse_timestamp(log.get("timestamp")) if log.get("timestamp") else datetime.utcnow().isoformat()
                        log["prediction"] = str(log.get("prediction", "normal")).strip().lower()
                        log["raw"] = log.get("raw", str(log))
                        es.index(index="classified-logs", document=log)
                    except json.JSONDecodeError as e:
                        print(f"Skipping invalid JSON line in {filename}: {e}")


if __name__ == "__main__":
    upload_logs()
    print("Done uploading.")

