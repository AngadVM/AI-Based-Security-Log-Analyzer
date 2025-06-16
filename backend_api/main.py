from fastapi import FastAPI, Request
from joblib import load
import pandas as pd 
import json
from parser.log_parser import parse_syslog 




app = FastAPI()

@app.post("/ingest")
async def ingest_log(request: Request):
    raw_body = await request.body()
    raw_text = raw_body.decode()

    for parser in [parse_json_log, parse_apache_log, parse_syslog, parse_nginx_log]:
        parsed = parser(raw_text)
        if 'error' not in parsed:
            print("Parsed Log:", parsed)
            break
    else:
        parsed = {"raw": raw_text, "error": "No parser matched"}
        print("Failed to parse log")

    return {"status": "parsed", "data": parsed}

