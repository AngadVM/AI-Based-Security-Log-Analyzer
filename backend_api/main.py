from fastapi import FastAPI 
from pydantic import BaseModel
from parser.log_router import LogRouter 
from ml_models.log_classifier import LogClassifier 

app = FastAPI()
router = LogRouter()
classifier = LogClassifier()

class LogInput(BaseModel):
    line: str

@app.get("/")
def root():
    return {"status": "Backend is up and running!"}


@app.post("/analyze")
def analyze_log(log: LogInput):
    parsed = parse_log_line(log.line)
    if "error" not in parsed:
        text_to_classify = parsed.get("message") or parsed.get("path") or "" 
        label, score = classifier.classify(text_to_classify)
        return {
            "parsed": parsed,
            "classification": {
                "label": label,
                "score": score
            }
        }
    return parsed
