import re
from parser.base_parser import BaseParser 
from datetime import datetime 

class SyslogParser(BaseParser):
    def parse(self, line):
        regex = r'(?P<month>\w{3})\s+(?P<day>\d{1,2}) (?P<time>\d{2}:\d{2}:\d{2}) (?P<host>\S+) (?P<process>[\w\-]+)(?:\[\d+\])?: (?P<message>.+)' 
        match = re.match(regex, line)
        if not match:
            return None
        
        now = datetime.now()
        ts_str = f"{now.year} {match.group('month')} {match.group('day')} {match.group('time')}"
        ts = datetime.strptime(ts_str, "%Y %b %d %H:%M:%S")
        return {
            "source": "syslog",
            "timestamp": ts.isoformat(),
            "host": match.group("host"),
            "process": match.group("process"),
            "message": match.group("message"),

        }

