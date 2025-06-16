
from pathlib import Path
import sys
import os
import json

# Add root project path to imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from parser.log_parser import parse_log_file

DATA_DIR = Path("data")
OUTPUT_DIR = DATA_DIR / "parsed_logs"

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

SUPPORTED_FORMATS = {
    "apache": "apache",
    "access": "apache",
    "nginx": "nginx",
    "syslog": "syslog",
    "linux": "syslog",
    "auth": "syslog",
    "openssh": "syslog",
    "ssh": "syslog",
    "json": "json",
    "log.json": "json"
}

def detect_log_type(filename: str) -> str:
    fname = filename.lower()
    for keyword, log_type in SUPPORTED_FORMATS.items():
        if keyword in fname:
            return log_type
    return "unknown"

def main():
    log_files = list(DATA_DIR.glob("*.log"))

    if not log_files:
        print("No log files found in 'data/' folder.")
        return

    for file in log_files:
        log_type = detect_log_type(file.name)
        print(f"\n Parsing '{file.name}' as type: {log_type.upper()}")

        if log_type == "unknown":
            print("Skipping unknown log type.\n")
            continue

        try:
            parsed_logs = parse_log_file(file, log_type)

            if not parsed_logs:
                print("No logs parsed from this file.")
                continue

            # Write parsed logs to JSONL file
            out_path = OUTPUT_DIR / (file.stem + ".json")
            with open(out_path, "w") as f:
                for entry in parsed_logs:
                    json.dump(entry, f)
                    f.write("\n")

            print(f"Saved {len(parsed_logs)} logs to {out_path}")
        except Exception as e:
            print(f"Error parsing {file.name}: {e}")

if __name__ == "__main__":
    main()

