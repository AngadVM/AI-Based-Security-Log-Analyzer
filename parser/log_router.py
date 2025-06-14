from parser.apache_parser import ApacheParser 
from parser.syslog_parser import SyslogParser
from parser.nginx_parser import NginxParser 
from parser.json_parser import JSONLogParser


class LogRouter:
    def __init__(self):
        self.parsers = [
            ApacheParser(), 
            SyslogParser(),
            NginxParser(),
            JSONLogParser(),
        ]

    def parse_line(self, line: str):
        for parser in self.parsers:
            result = parser.parse(line)
            if result:
                return result

        return {"error": "Unrecognized format"}

