import json

VALID_LABELS = {
    "brute_force",
    "port_scan",
    "suspicious_login",
    "dos_attack",
    "malware_activity",
    "normal"
}

def test_synthetic_log_file(filename="synthetic_logs.jsonl"):
    with open(filename, "r") as f:
        lines = f.readlines()

    print(f" Validating {len(lines)} entries...\n")

    errors = 0
    for i, line in enumerate(lines):
        try:
            data = json.loads(line)
        except json.JSONDecodeError:
            print(f" Line {i+1} is not valid JSON")
            errors += 1
            continue

        if "raw" not in data or not isinstance(data["raw"], str):
            print(f" Line {i+1} missing valid 'raw' field")
            errors += 1

        if "timestamp" not in data:
            print(f" Line {i+1} missing 'timestamp'")
            errors += 1

        if "label" not in data or data["label"] not in VALID_LABELS:
            print(f" Line {i+1} has invalid or missing 'label': {data.get('label')}")
            errors += 1

    if errors == 0:
        print(" All log entries are valid.")
    else:
        print(f" Found {errors} issues.")

if __name__ == "__main__":
    test_synthetic_log_file()

