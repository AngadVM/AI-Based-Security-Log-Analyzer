import json
from datetime import datetime, timedelta
from elasticsearch import Elasticsearch, helpers

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ml_pipeline.infer import infer_log

es = Elasticsearch("http://localhost:9200")

# Threat templates
THREATS = {
    "brute_force": [
        "Failed login attempt for user admin from 192.168.1.101",
        "Multiple authentication failures for root from 10.0.0.5",
        "Incorrect password entered multiple times for user guest"
    ],
    "port_scan": [
        "Port scan detected from 172.16.0.12 targeting port 22",
        "Suspicious activity: scanning multiple ports",
        "Nmap scan attempt from IP 10.10.10.10"
    ],
    "suspicious_login": [
        "Login at unusual hour from IP 192.168.0.22",
        "Unrecognized login from foreign country",
        "Login succeeded after multiple failures"
    ],
    "dos_attack": [
        "High traffic volume from single source 8.8.8.8",
        "Denial of service attempt detected on port 443",
        "Flood attack signature matched"
    ],
    "malware_activity": [
        "Suspicious binary executed: worm.py",
        "Known malware signature matched: Trojan.XYZ",
        "Unauthorized outbound connection to 185.12.1.2"
    ]
}

NORMAL_LOGS = [
    "User angadvm logged in via SSH",
    "Scheduled cron job executed at midnight",
    "System rebooted successfully",
    "Package update completed with no errors",
    "User logged out from session tty1",
    "Ping to 8.8.8.8 successful",
    "Disk usage checked by admin",
    "New USB device connected",
    "Firewall rules loaded successfully",
    "Kernel module loaded: e1000"
]

def generate_synthetic_logs(total=500, anomaly_ratio=0.3):
    logs = []
    now = datetime.utcnow()

    num_anomalies = int(total * anomaly_ratio)
    num_normal = total - num_anomalies

    # Generate normal logs
    for i in range(num_normal):
        raw = random.choice(NORMAL_LOGS)
        ts = now - timedelta(seconds=random.randint(0, 3600))
        logs.append({
            "raw": raw,
            "timestamp": ts.isoformat()
        })

    # Generate anomalous logs
    for i in range(num_anomalies):
        threat_type = random.choice(list(THREATS.keys()))
        raw = random.choice(THREATS[threat_type])
        ts = now - timedelta(seconds=random.randint(0, 3600))
        logs.append({
            "raw": raw,
            "timestamp": ts.isoformat(),
            "expected_threat": threat_type  # Optional debug info
        })

    random.shuffle(logs)
    return logs

def upload_logs_to_es(logs):
    actions = []
    count = 0

    for log in logs:
        try:
            enriched = infer_log(log)
            enriched["ingested_at"] = datetime.utcnow().isoformat()
            enriched["source"] = "synthetic"
            actions.append({
                "_index": "classified-logs",
                "_source": enriched
            })
            count += 1
        except Exception as e:
            print(f" Failed to enrich log: {e}")

    if actions:
        helpers.bulk(es, actions)
        print(f" Uploaded {count} synthetic logs to Elasticsearch")

if __name__ == "__main__":
    print(" Generating synthetic logs...")
    synthetic_logs = generate_synthetic_logs(total=500, anomaly_ratio=0.3)
    print(" Uploading logs to Elasticsearch...")
    upload_logs_to_es(synthetic_logs)
    print(" Done.")

