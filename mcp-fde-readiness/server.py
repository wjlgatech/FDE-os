#!/usr/bin/env python3
"""mcp-fde-readiness — a tiny, dependency-free Model Context Protocol (MCP) server over stdio.

This is Anthropic's *exact* FDE deliverable — an MCP server — as a fresh, self-contained portfolio
piece. It exposes the FDE readiness rubric as callable tools, so any MCP host (Claude Desktop,
Claude Code, Cursor, …) can score a candidate's readiness for an Anthropic/OpenAI FDE role and get
the specific gaps to close. Same rubric (readiness-rubric.json) that powers the human self-assessment
at /readiness.html — one source of truth, two surfaces (agent + human).

Tools:
  - readiness_rubric()               → the rubric (dimensions + items)
  - readiness_score(answers)         → per-dimension + overall + GATE (go-to-apply) + gaps + next step
  - evidence_tier(text)              → classify a piece of evidence: claimed | observed | attested

Transport: newline-delimited JSON-RPC 2.0 over stdin/stdout (MCP stdio). `handle_request` is a pure
function (req dict → response dict or None) so it is unit-testable without real stdio.

Run (for an MCP host to spawn):  python3 mcp-fde-readiness/server.py
"""
from __future__ import annotations

import json
import os
import sys

PROTOCOL_VERSION = "2025-06-18"
SERVER_INFO = {"name": "fde-readiness", "version": "0.1.0"}
ERR_METHOD_NOT_FOUND = -32601
ERR_INVALID_PARAMS = -32602

_HERE = os.path.dirname(os.path.abspath(__file__))
_RUBRIC_PATH = os.path.join(_HERE, "..", "readiness-rubric.json")


def load_rubric() -> dict:
    with open(_RUBRIC_PATH, encoding="utf-8") as f:
        return json.load(f)


# ----------------------------------------------------------------- scoring (pure)

def score(rubric: dict, answers: dict) -> dict:
    """answers: {item_id: bool}. Returns per-dimension fractions, overall, gate + gaps."""
    dims_out, checked_flags = [], set()
    frac_sum = 0.0
    for d in rubric["dimensions"]:
        got = sum(it["w"] for it in d["items"] if answers.get(it["id"]))
        tot = sum(it["w"] for it in d["items"])
        frac = (got / tot) if tot else 0.0
        frac_sum += frac
        for it in d["items"]:
            if it.get("flag") and answers.get(it["id"]):
                checked_flags.add(it["flag"])
        dims_out.append({"key": d["key"], "label": d["label"], "fraction": round(frac, 2),
                         "gap": None if frac >= 0.67 else d["gap"]})
    overall = round(frac_sum / len(rubric["dimensions"]), 2) if rubric["dimensions"] else 0.0

    gate = rubric.get("gate", {})
    need_flags = set(gate.get("must_flags", []))
    missing_flags = sorted(need_flags - checked_flags)
    go = overall >= gate.get("min_overall", 0.7) and not missing_flags

    if go:
        verdict = f"READY TO APPLY — overall {overall:.0%}, and the non-self-issuable rungs are covered."
    else:
        bits = []
        if overall < gate.get("min_overall", 0.7):
            bits.append(f"overall {overall:.0%} < {gate.get('min_overall',0.7):.0%}")
        if "ship" in missing_flags:
            bits.append("no shipped-to-production system (the observed rung)")
        if "vouch" in missing_flags:
            bits.append("no third-party vouch — the one rung you can't self-issue")
        verdict = "NOT YET — " + "; ".join(bits) + "."
    return {"overall": overall, "go": go, "verdict": verdict,
            "dimensions": dims_out, "missing_flags": missing_flags}


_TIER_HINT = {
    "attested": ["vouch", "reference", "attest", "signed", "recommend", "worked with me", "would staff"],
    "observed": ["shipped", "deployed", "live", "url", "in production", "passes", "ci", "demo", "repo"],
}
def evidence_tier(text: str) -> dict:
    low = (text or "").lower()
    for tier in ("attested", "observed"):
        if any(kw in low for kw in _TIER_HINT[tier]):
            return {"tier": tier}
    return {"tier": "claimed"}


# ----------------------------------------------------------------- MCP wiring

def _render_score(r: dict) -> str:
    lines = [("✅ " if r["go"] else "⛔ ") + r["verdict"], "", f"overall readiness: {r['overall']:.0%}"]
    for d in r["dimensions"]:
        mark = "✓" if d["fraction"] >= 0.67 else "•"
        lines.append(f"  {mark} {d['label']}: {d['fraction']:.0%}" + (f"  → {d['gap']}" if d["gap"] else ""))
    return "\n".join(lines)

TOOLS = [
    {"name": "readiness_rubric", "description": "Return the FDE readiness rubric (dimensions + items).",
     "inputSchema": {"type": "object", "properties": {}}},
    {"name": "readiness_score",
     "description": "Score readiness for an Anthropic/OpenAI FDE role. Pass answers as {item_id: true/false}. Returns per-dimension %, overall, a go-to-apply gate, and the gaps to close.",
     "inputSchema": {"type": "object", "properties": {"answers": {"type": "object"}}, "required": ["answers"]}},
    {"name": "evidence_tier",
     "description": "Classify a piece of evidence text as claimed | observed | attested.",
     "inputSchema": {"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]}},
]


def _call_tool(name: str, args: dict) -> str:
    rubric = load_rubric()
    if name == "readiness_rubric":
        return json.dumps(rubric, indent=2)
    if name == "readiness_score":
        answers = args.get("answers")
        if not isinstance(answers, dict):
            raise ValueError("provide 'answers' as an object of {item_id: true/false}")
        return _render_score(score(rubric, answers))
    if name == "evidence_tier":
        if not args.get("text"):
            raise ValueError("provide 'text'")
        return "tier: " + evidence_tier(args["text"])["tier"]
    raise KeyError(name)


def handle_request(req: dict):
    method = req.get("method")
    req_id = req.get("id")
    if method == "initialize":
        params = req.get("params") or {}
        return {"jsonrpc": "2.0", "id": req_id, "result": {
            "protocolVersion": params.get("protocolVersion", PROTOCOL_VERSION),
            "capabilities": {"tools": {}}, "serverInfo": SERVER_INFO}}
    if method == "notifications/initialized":
        return None
    if method == "ping":
        return {"jsonrpc": "2.0", "id": req_id, "result": {}}
    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": req_id, "result": {"tools": TOOLS}}
    if method == "tools/call":
        params = req.get("params") or {}
        name = params.get("name")
        args = params.get("arguments") or {}
        try:
            text = _call_tool(name, args)
            return {"jsonrpc": "2.0", "id": req_id, "result": {"content": [{"type": "text", "text": text}]}}
        except KeyError:
            return {"jsonrpc": "2.0", "id": req_id, "error": {"code": ERR_METHOD_NOT_FOUND, "message": f"unknown tool: {name}"}}
        except Exception as e:
            return {"jsonrpc": "2.0", "id": req_id, "result": {"isError": True, "content": [{"type": "text", "text": str(e)}]}}
    return {"jsonrpc": "2.0", "id": req_id, "error": {"code": ERR_METHOD_NOT_FOUND, "message": f"unknown method: {method}"}}


def main() -> int:  # pragma: no cover - stdio loop
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except json.JSONDecodeError:
            continue
        resp = handle_request(req)
        if resp is not None:
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
