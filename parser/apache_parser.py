import re
from parser.base_parser import BaseParser 
from datetime import datetime 

class ApacheParser(BaseParser):
    def parse(self, line):
        regex = r'(?P<ip>\S+) \S+ \S+ \[(?P<datetime>[^\]]+)\] "(?P<method>\S+) (?P<path>\S+) \S+" (?P<status>\d+) (?P<size>\d+)'
        match = re.match(regex, line)
        if not match:
            return None
        dt = datetime.strptime(match.group("datetime").split()[0], "%d/%b/%Y:%H:%M:%S")
        return {
            "source": "apache",
            "ip": match.group("ip"),
            "timestamp": dt.isoformat(),
            "method": match.group("method"),
            "path": match.group("path"),
            "status": int(match.group("status")),
            "size": int(match.group("size")),
        }
