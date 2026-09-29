import os
import sys

# Ensure base directory is in sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# Set serverless data directory to /tmp/data for Vercel Serverless environment
os.environ.setdefault("SIH_DATA_DIR", "/tmp/data")
os.environ.setdefault("SIH_SYNC_JOBS", "1")

from backend.app.main import app
