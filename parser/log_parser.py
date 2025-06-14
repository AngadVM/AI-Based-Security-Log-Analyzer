import re
import json
from datetime import datetime

def parse_apache_log(log):
    pattern = r'(?P<ip>\S+) - - \[(?P<datetime>[^\]]+)\] "(?P<method>\S+) (?P<path>\S+) \S+" (?P<status>\d{3}) (?P<size>\d+)'
    match = re.match(pattern, log)
    if match:
        return match.groupdict()
    return {"raw": log, "error": "Apache parse failed"}

def parse_syslog(log):
    pattern = r'(?P<month>\w{3}) (?P<day>\d{1,2}) (?P<time>\d{2}:\d{2}:\d{2}) (?P<host>\S+) (?P<process>\S+): (?P<message>.*)'
    match = re.match(pattern, log)
    if match:
        return match.groupdict()
    return {"raw": log, "error": "Syslog parse failed"}

def parse_json_log(log):
    try:
        return json.loads(log)
    except json.JSONDecodeError:
        return {"raw": log, "error": "JSON parse failed"}

def parse_nginx_log(log):
    pattern = r'(?P<ip>\S+) - (?P<user>\S+) \[(?P<time>[^\]]+)\] "(?P<request>[^"]+)" (?P<status>\d{3}) (?P<size>\d+)'
    match = re.match(pattern, log)
    if match:
        return match.groupdict()
    return {"raw": log, "error": "Nginx parse failed"}

