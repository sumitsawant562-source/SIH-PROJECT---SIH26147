import os
import sys
import asyncio
from http.server import BaseHTTPRequestHandler

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

os.environ.setdefault("SIH_DATA_DIR", "/tmp/data")
os.environ.setdefault("SIH_SYNC_JOBS", "1")

from backend.app.main import app

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self._handle()

    def do_POST(self):
        self._handle()

    def do_PUT(self):
        self._handle()

    def do_DELETE(self):
        self._handle()

    def do_OPTIONS(self):
        self._handle()

    def _handle(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length) if content_length > 0 else b""
        
        path = self.path
        if not path.startswith("/api"):
            path = "/api" + (path if path.startswith("/") else "/" + path)
            
        scope = {
            "type": "http",
            "asgi": {"version": "3.0", "spec_version": "2.0"},
            "http_version": "1.1",
            "method": self.command,
            "scheme": "https",
            "path": path,
            "raw_path": path.encode("utf-8"),
            "query_string": b"",
            "headers": [(k.lower().encode("utf-8"), v.encode("utf-8")) for k, v in self.headers.items()],
            "client": self.client_address,
            "server": ("127.0.0.1", 80),
        }
        
        response_status = 200
        response_headers = []
        response_body = bytearray()
        
        async def receive():
            return {"type": "http.request", "body": body, "more_body": False}

        async def send(message):
            nonlocal response_status, response_headers, response_body
            if message["type"] == "http.response.start":
                response_status = message["status"]
                response_headers = message.get("headers", [])
            elif message["type"] == "http.response.body":
                response_body.extend(message.get("body", b""))

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(app(scope, receive, send))
        finally:
            loop.close()

        self.send_response(response_status)
        for k, v in response_headers:
            self.send_header(k.decode("utf-8"), v.decode("utf-8"))
        self.end_headers()
        self.wfile.write(bytes(response_body))
