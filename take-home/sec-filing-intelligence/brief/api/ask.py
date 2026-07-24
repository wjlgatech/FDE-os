"""Vercel Python function: ask the REAL SEC filing QA pipeline one question.

Not a mock — the vendored modules under api/_agent/ are byte-equality-gated
against the source by CI (test_brief_sync.py), and the corpus is the same
page-anchored, SHA-pinned extraction the eval gates run on.

POST {"question": "..."} → the full answer object: text, calc steps, verbatim
citations with page anchors + SEC URLs, caveats (incl. near-miss disclosures),
confidence — or a refusal with reasons. Nothing is generated: numbers come
from parsed table coordinates, arithmetic from Decimal.
"""
import json
import os
import sys
from http.server import BaseHTTPRequestHandler

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "_agent"))

from qa import ask  # noqa: E402


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            length = int(self.headers.get("content-length", 0))
            if length > 4000:
                return self._send(400, {"error": "question too large"})
            payload = json.loads(self.rfile.read(length) or b"{}")
            q = payload.get("question")
            if not q or not isinstance(q, str):
                return self._send(400, {"error": "POST {question: string}"})
            return self._send(200, ask(q))
        except Exception as e:  # honest 500, never a fabricated answer
            return self._send(500, {"error": f"{type(e).__name__}: {e}"})

    def do_GET(self):
        self._send(405, {"error": "POST a {question} payload"})

    def _send(self, code: int, body: dict):
        data = json.dumps(body, default=str).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)
