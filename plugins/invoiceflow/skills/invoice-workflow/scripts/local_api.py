"""Dependency-free local HTTP API. Development only; loopback by default.

The API provides health and version information, never customer data.
Do not expose to the public Internet or mistake it for the future OAuth/MCP service.
"""
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

VERSION = "0.2.0-dev"

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/healthz":
            return self.respond(200, {"status": "ok"})
        if self.path == "/version":
            return self.respond(200, {"name": "InvoiceFlow", "version": VERSION, "mode": "local-development"})
        return self.respond(404, {"error": "not found"})

    def do_POST(self):
        return self.respond(405, {"error": "mutating HTTP API disabled; use local CLI"})

    def respond(self, status, payload):
        body=json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

if __name__ == "__main__":
    port=int(os.environ.get("INVOICEFLOW_PORT","8765"))
    if not 0 < port < 65536:raise ValueError("Invalid port")
    server=ThreadingHTTPServer(("127.0.0.1",port),Handler)
    print(f"InvoiceFlow local inspection API on http://127.0.0.1:{port}",flush=True)
    server.serve_forever()
