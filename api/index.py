import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

os.environ.setdefault("SIH_DATA_DIR", "/tmp/data")
os.environ.setdefault("SIH_SYNC_JOBS", "1")

from backend.app.main import app
from backend.app.routes import api_router

# Mount api_router at root so both /api/* and /* (stripped path) match cleanly on Vercel
app.include_router(api_router)
