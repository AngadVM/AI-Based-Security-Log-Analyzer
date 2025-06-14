import sys
import os

# Add the root project directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from parser.log_router import LogRouter

def parse_file(file_path):
    router = LogRouter()
    with open(file_path, "r") as f:
        for line in f:
            parsed = router.parse_line(line.strip())
            print(parsed)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Parse a log file.")
    parser.add_argument("file", help="Path to the log file")
    args = parser.parse_args()
    parse_file(args.file)

