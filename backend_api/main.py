from fastapi import FastAPI 
from pydantic import BaseModel
from parser.parser import parse_log_line
from ml_models.log_classifier import LogClassifier 

app = FastAPI()
classifier = LogClassifier()

class LogInput(BaseModel):
    line: str

@app.post("/analyze")
def analyze_log(log: LogInput):
    parsed = parse_log_line(log.line)
    if parsed:
        label, score = classifier.classify(parsed["message"])
        return {
            "parsed": parsed,
            "classification": {
                "label": label,
                "score": score
            }
        }
    return {"error": "Invalid log format"}
