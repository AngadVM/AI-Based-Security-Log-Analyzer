import re
import json
from pathlib import Path
from typing import List


def parse_log_file(file_path: Path, log_type: str) -> List[dict]:
    with open(file_path, "r") as f:
        lines = f.readlines()

    if log_type == "apache" or log_type == "nginx":
        return [parse_apache_log(line) for line in lines if line.strip()]
    elif log_type == "syslog":
        return [parse_syslog(line) for line in lines if line.strip()]
    elif log_type == "json":
        return [parse_json_log(line) for line in lines if line.strip()]
    else:
        raise ValueError(f"Unsupported log type: {log_type}")


def parse_apache_log(line: str) -> dict:
    pattern = r'(\S+) (\S+) (\S+) \[(.*?)\] "(.*?)" (\d{3}) (\d+)'
    match = re.match(pattern, line)
    if match:
        return {
            "ip": match.group(1),
            "user": match.group(3),
            "timestamp": match.group(4),
            "request": match.group(5),
            "status": int(match.group(6)),
            "size": int(match.group(7)),
        }
    return {"raw": line.strip()}


def parse_syslog(line: str) -> dict:
    pattern = r'^(\w{3}\s+\d+\s[\d:]+)\s([\w.-]+)\s([\w\/\-\[\]]+):\s?(.*)'
    match = re.match(pattern, line)
    if match:
        return {
            "timestamp": match.group(1),
            "hostname": match.group(2),
            "service": match.group(3),
            "message": match.group(4),
        }
    return {"raw": line.strip()}


def parse_json_log(line: str) -> dict:
    try:
        return json.loads(line)
    except json.JSONDecodeError:
        return {"raw": line.strip()}

