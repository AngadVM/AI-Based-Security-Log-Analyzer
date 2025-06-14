import re
from base_parser import BaseParser 

class JSONLogParser(BaseParser):
    def parse(self, line):
        try:
            data = json.loads(line)
            return {
                    "source": "json",
                    "timestamp": data.get("timestamp"),
                    "level": data.get("level"),
                    "message": data.get("msg"),
                    "extra": {k: v for k, v in data.items() if k not in ["timestamp", "level", "msg"]}
                }
        except json.JSONDecodeError:
            return None
