from fastapi import FastAPI, Request

app = FastAPI()

@app.post("/ingest")
async def ingest_log(request: Request):
    data = await request.json()
    print("Received log:", data)
    return {"status": "received"}

