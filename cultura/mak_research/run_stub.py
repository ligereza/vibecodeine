#!/usr/bin/env python3
"""Standalone helper that starts the local interface stub when requested."""
from __future__ import annotations

import json
import os
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HOST = "127.0.0.1"
PORT = int(os.environ.get("INTERFAZ_PORT", "8890"))


class _StubHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/status"):
            body = json.dumps({"status": "ok", "pid": os.getpid()}).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        self.send_response(404)
        self.end_headers()

    def do_POST(self):
        if self.path.startswith("/run"):
            length = int(self.headers.get("Content-Length", "0"))
            self.rfile.read(length)
            body = b"ok"
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        self.send_response(404)
        self.end_headers()

    def log_message(self, fmt, *args):
        return


if __name__ == "__main__":
    try:
        ThreadingHTTPServer((HOST, PORT), _StubHandler).serve_forever(poll_interval=0.1)
    except OSError:
        pass
