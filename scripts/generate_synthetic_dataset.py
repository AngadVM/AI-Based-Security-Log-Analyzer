import random
import csv
from datetime import datetime, timedelta

def generate_balanced_logs(n=1000):
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
    anomalies_per_type = (n * 0.3) // len(anomaly_templates)
    normals = int(n * 0.7)

    # Add normal logs
    for _ in range(normals):
        msg = random.choice(normal_templates).format(user=random_user(), ip=random_ip(), port=random.randint(1000, 65535))
        logs.append({
            "timestamp": datetime.utcnow().strftime("%b %d %H:%M:%S"),
            "raw": msg,
            "label": "normal"
        })

    # Add anomalies
    for threat, template in anomaly_templates.items():
        for _ in range(int(anomalies_per_type)):
            msg = template.format(user=random_user(), ip=random_ip(), port=random.randint(1000, 65535), pid=random.randint(100, 9999))
            logs.append({
                "timestamp": datetime.utcnow().strftime("%b %d %H:%M:%S"),
                "raw": msg,
                "label": threat
            })

    random.shuffle(logs)
    return logs

