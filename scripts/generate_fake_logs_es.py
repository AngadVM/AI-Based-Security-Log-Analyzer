import random
import time
from datetime import datetime, timedelta
from elasticsearch import Elasticsearch

es = Elasticsearch("http://localhost:9200")

normal_msgs = [
    "Accepted password for user angad from 192.168.1.10 port 22 ssh2",
    "Connection closed by 192.168.1.15 port 22",
    "User angad logged in successfully",
    "Scheduled task completed at midnight",
    "System health check passed"
]

anomaly_msgs = [
    "Failed password for invalid user root from 192.168.1.100 port 22 ssh2",
    "Multiple failed login attempts detected",
    "User not found in database: hacker",
    "Permission denied while accessing /etc/shadow",
    "Segfault in kernel module"
]

def generate_log():
    # Shift log timestamp within last 10 minutes
    timestamp = datetime.utcnow() - timedelta(seconds=random.randint(0, 600))
    iso_timestamp = timestamp.isoformat()

    is_anomaly = random.random() < 0.3
    raw = random.choice(anomaly_msgs if is_anomaly else normal_msgs)
    prediction = "anomaly" if is_anomaly else "normal"

    return {
        "timestamp": iso_timestamp,
        "raw": raw,
        "prediction": prediction
    }

def send_logs(n=20):
    for i in range(n):
        log = generate_log()
        es.index(index="classified-logs", document=log)
        print(f"[{i+1}] Indexed: {log['prediction'].upper()} @ {log['timestamp']}")
        time.sleep(0.1)

if __name__ == "__main__":
    send_logs(20)
    print("Done indexing logs into Elasticsearch.")

