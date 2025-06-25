import os
import sys
import json
import random
from datetime import datetime
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ml_pipeline.infer import infer_log


def random_ip():
    return ".".join(str(random.randint(1, 255)) for _ in range(4))


def random_user():
    return random.choice(["alice", "bob", "charlie", "admin", "root"])


def generate_logs(n=1000, anomaly_ratio=0.3):
    anomaly_templates = {
        "brute_force": "Failed password for invalid user {user} from {ip} port {port} ssh2",
        "dos_attack": "Too many connections from {ip}",
        "port_scan": "Suspicious port scan detected from {ip}",
        "suspicious_login": "Login attempt from unusual location {ip}",
        "malware_activity": "Malicious activity detected in process {pid}"
    }

    normal_templates = [
        "Accepted password for user {user} from {ip} port {port} ssh2",
        "Connection closed by {ip} port {port}",
        "User {user} logged in successfully",
        "Ping received from {ip}",
    ]

    logs = []
    n_anomalies = int(n * anomaly_ratio)
    n_normals = n - n_anomalies

    # Generate normal logs
    for _ in range(n_normals):
        msg = random.choice(normal_templates).format(
            user=random_user(), ip=random_ip(), port=random.randint(1000, 65000)
        )
        logs.append({"raw": msg})

    # Generate anomaly logs evenly across types
    per_type = max(1, n_anomalies // len(anomaly_templates))
    for threat, template in anomaly_templates.items():
        for _ in range(per_type):
            msg = template.format(
                user=random_user(), ip=random_ip(), port=random.randint(1000, 65000), pid=random.randint(100, 9999)
            )
            logs.append({"raw": msg})

    random.shuffle(logs)
    return logs


def upload_to_es(logs, es_url="http://localhost:9200", index_name="classified-logs"):
    es = Elasticsearch(es_url)
    actions = []

    for log in logs:
        try:
            enriched = infer_log(log)
            enriched["ingested_at"] = datetime.utcnow().isoformat()
            actions.append({"_index": index_name, "_source": enriched})
        except Exception as e:
            print(f" Error processing log: {log['raw']}\n{e}")

    if actions:
        bulk(es, actions)
        print(f" Uploaded {len(actions)} logs to index '{index_name}'")
    else:
        print(" No logs uploaded.")


if __name__ == "__main__":
    print("🔧 Generating synthetic logs...")
    synthetic_logs = generate_logs(n=1000, anomaly_ratio=0.3)
    print(" Uploading to Elasticsearch...")
    upload_to_es(synthetic_logs)

