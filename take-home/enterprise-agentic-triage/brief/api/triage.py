"""Vercel Python function: run ONE purchase request through the REAL triage agent.

This is not a mock — it imports the same modules that pass the repo's test suite
(vendored under api/_agent/, byte-equality-gated against the source by CI) and runs
the full graph: intake → tools → retrieve → assemble → decide → guard → human gate.

POST {"request": {...}, "priors": [{"vendor","amount_usd","date"}...]}
  → {"decision", "escalate_to", "grounded", "citations", "guard_flags",
     "guard_tripped", "context_receipt", "trace": [...], "status"}

`priors` preloads session memory as already-approved purchases — that's the lever
for the split-purchase experiment. Escalations return status "awaiting_human":
the pause IS the answer; nothing above the agent's authority resolves here.
"""
import json
import os
import sys
import tempfile
import uuid
from http.server import BaseHTTPRequestHandler

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "_agent"))

from agent import TriageAgent  # noqa: E402

CORPUS = os.path.join(_HERE, "_agent", "corpus")
DATA = os.path.join(_HERE, "_agent", "data")

ALLOWED_FIELDS = {"id", "date", "requester", "role", "vendor", "category",
                  "amount_usd", "description", "processes_pii"}


def run_triage(payload: dict) -> dict:
    raw = payload.get("request") or {}
    req = {k: v for k, v in raw.items() if k in ALLOWED_FIELDS}
    req.setdefault("id", f"R-PLAY-{uuid.uuid4().hex[:6]}")
    req.setdefault("requester", "playground.user")
    if isinstance(req.get("amount_usd"), str):
        try:
            req["amount_usd"] = float(req["amount_usd"].replace(",", "").replace("$", ""))
            if req["amount_usd"] == int(req["amount_usd"]):
                req["amount_usd"] = int(req["amount_usd"])
        except ValueError:
            pass  # leave it — the input-validation guard will reject it honestly

    agent = TriageAgent(CORPUS, DATA)
    for i, p in enumerate((payload.get("priors") or [])[:10]):
        agent.memory.record(
            {"id": f"R-PRIOR-{i+1}", "vendor": str(p.get("vendor", "")),
             "amount_usd": p.get("amount_usd", 0), "date": str(p.get("date", ""))},
            "approve")

    events = []
    cp = os.path.join(tempfile.gettempdir(), f"triage-{uuid.uuid4().hex}.jsonl")
    try:
        final = agent.process(req, cp, tracer=events.append)
    finally:
        if os.path.exists(cp):
            os.remove(cp)

    return {
        "request_as_seen": req,
        "decision": final["decision"],
        "escalate_to": final.get("escalate_to"),
        "status": final.get("status", "completed"),
        "gate_reason": final.get("gate_reason"),
        "grounded": final.get("grounded", True),
        "citations": final.get("citations", []),
        "guard_flags": final.get("guard_flags", []),
        "guard_tripped": final.get("guard_tripped", False),
        "context_receipt": final.get("context_receipt"),
        "trace": events,
    }


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            length = int(self.headers.get("content-length", 0))
            if length > 20000:
                return self._send(400, {"error": "payload too large"})
            payload = json.loads(self.rfile.read(length) or b"{}")
            result = run_triage(payload)
            return self._send(200, result)
        except Exception as e:  # honest 500 with the reason, never a fake decision
            return self._send(500, {"error": f"{type(e).__name__}: {e}"})

    def do_GET(self):
        self._send(405, {"error": "POST a {request, priors} payload"})

    def _send(self, code: int, body: dict):
        data = json.dumps(body, default=str).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)
