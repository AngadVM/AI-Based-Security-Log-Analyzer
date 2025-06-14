import re
from datetime import datetime

def parse_log_line(line):
    regex = r'(?P<timestamp>\S+ \S+) (?P<level>\w+) (?P<message>.+)'
    match = re.match(regex, line)
    if match:
        return {
            "timestamp": datetime.strptime(match.group("timestamp"), "%Y-%m-%d %H:%M:%S"),
            "level": match.group("level"),
            "message": match.group("message")
        }
    return None


if __name__ == '__main__':
    sample = "2025-06-13 18:44:12 INFO User logged in successfully"
    print(parse_log_line(sample))
