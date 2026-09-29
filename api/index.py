import os
import sys
import traceback

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

os.environ.setdefault("SIH_DATA_DIR", "/tmp/data")
os.environ.setdefault("SIH_SYNC_JOBS", "1")

try:
    from backend.app.main import app
except Exception as e:
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse
    app = FastAPI()
    err_tb = traceback.format_exc()
    @app.api_route("/{full_path:path}", methods=["GET", "POST", "PUT", "DELETE"])
    def catch_all(full_path: str):
        return JSONResponse(status_code=500, content={"error": str(e), "traceback": err_tb})
