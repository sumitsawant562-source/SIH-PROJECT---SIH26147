from fastapi import FastAPI

app = FastAPI()

@app.get("/api/health")
@app.get("/health")
def health():
    return {"status": "ok", "version": "1.0.0", "provider": "vercel-serverless"}
