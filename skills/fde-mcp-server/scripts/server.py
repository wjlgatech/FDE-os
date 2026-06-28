#!/usr/bin/env python3
"""fde-mcp-server — a minimal, dependency-free Model Context Protocol (MCP) server over stdio.

It exposes FDE-os's own skills as MCP tools, so an MCP client (Claude Desktop, Claude Code, any
MCP host) can call them: score a draft against the TRUE rubric, or evaluate a RAG set. This both
(a) satisfies the common JD requirement "1+ Claude MCP integrations" with a real, runnable example,
and (b) dogfoods the repo — the skills become callable tools.

Transport: newline-delimited JSON-RPC 2.0 over stdin/stdout (the MCP stdio transport). One JSON
message per line; messages never contain embedded newlines.

Implemented methods: `initialize`, `notifications/initialized` (notification), `ping`,
`tools/list`, `tools/call`. `handle_request` is a pure function (req dict → response dict or None)
so it is unit-testable without real stdio.

Run (for an MCP host to spawn):
  python3 skills/fde-mcp-server/scripts/server.py
"""
from __future__ import annotations

import importlib.util
import json
import os
import sys
from types import ModuleType
from typing import Optional, TextIO

PROTOCOL_VERSION = "2025-06-18"
SERVER_INFO = {"name": "fde-os", "version": "0.1.0"}
_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))

# Method-not-found / invalid-params JSON-RPC error codes
ERR_METHOD_NOT_FOUND = -32601
ERR_INVALID_PARAMS = -32602


def _load(rel_script: str, mod_name: str) -> ModuleType:
    """Lazy-import a sibling skill script by repo-relative path."""
    path = os.path.join(_ROOT, rel_script)
    spec = importlib.util.spec_from_file_location(mod_name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ----------------------------------------------------------------- tool implementations

def _tool_true_score(args: dict) -> str:
    sc = _load("skills/true-scorer/scripts/score.py", "score")
    text = args.get("text")
    if text is None and args.get("draft_path"):
        with open(os.path.join(_ROOT, args["draft_path"]), encoding="utf-8") as fh:
            text = fh.read()
    if not text:
        raise ValueError("provide 'text' or 'draft_path'")
    scores, notes = sc.heuristic_scores(text)
    passed, reasons = sc.gate(scores)
    lines = [f"{k}={scores[k]}" for k in ("T", "R", "U", "E")]
    verdict = "PASS" if passed else "BLOCK — " + "; ".join(reasons)
    return f"TRUE score: {', '.join(lines)} (total {sum(scores.values())}/12)\nVERDICT: {verdict}"


def _tool_rag_eval(args: dict) -> str:
    rev = _load("skills/rag-eval-harness/scripts/rag_eval.py", "rag_eval")
    eval_set = args.get("eval_set")
    if eval_set is None and args.get("eval_set_path"):
        with open(os.path.join(_ROOT, args["eval_set_path"]), encoding="utf-8") as fh:
            eval_set = json.load(fh)
    if not isinstance(eval_set, list):
        raise ValueError("provide 'eval_set' (a JSON list) or 'eval_set_path'")
    k = int(args.get("k", 5))
    report = rev.evaluate(eval_set, k=k)
    out = [f"RAG eval — {report['n']} items, k={report.get('k')}:"]
    for name, val in report.get("metrics", {}).items():
        out.append(f"  {name}: {'n/a' if val is None else val}")
    thresholds = args.get("thresholds")
    if thresholds:
        passed, reasons = rev.gate(report["metrics"], {k2: float(v) for k2, v in thresholds.items()})
        out.append("VERDICT: " + ("PASS" if passed else "BLOCK — " + "; ".join(reasons)))
    return "\n".join(out)


TOOLS = {
    "true_score": {
        "description": "Score a Delta Field Manual draft against the TRUE rubric (T/R/U/E, 0-3 each) "
                       "and apply the ship gate (total >= 10 AND every letter >= 2).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "the draft text to score"},
                "draft_path": {"type": "string", "description": "repo-relative path to a draft .md (alternative to text)"},
            },
        },
        "handler": _tool_true_score,
    },
    "rag_eval": {
        "description": "Evaluate a RAG/agent eval set: retrieval metrics (precision@k, recall@k, MRR, "
                       "hit-rate) + grounding/hallucination proxy + citation coverage, with an optional gate.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "eval_set": {"type": "array", "description": "list of eval items (see rag-eval-harness schema)"},
                "eval_set_path": {"type": "string", "description": "repo-relative path to a JSON eval set"},
                "k": {"type": "integer", "description": "cutoff for @k metrics (default 5)"},
                "thresholds": {"type": "object", "description": "metric floors, e.g. {\"recall@k\": 0.7}"},
            },
        },
        "handler": _tool_rag_eval,
    },
}


# ----------------------------------------------------------------- JSON-RPC dispatch

def _result(req_id: object, result: object) -> dict:
    return {"jsonrpc": "2.0", "id": req_id, "result": result}


def _error(req_id: object, code: int, message: str) -> dict:
    return {"jsonrpc": "2.0", "id": req_id, "error": {"code": code, "message": message}}


def handle_request(req: dict) -> Optional[dict]:
    """Pure dispatch. Returns a JSON-RPC response dict, or None for notifications."""
    method = req.get("method")
    req_id = req.get("id")
    is_notification = "id" not in req

    if method == "notifications/initialized" or is_notification:
        return None  # notifications get no response

    if method == "initialize":
        client_version = (req.get("params") or {}).get("protocolVersion")
        return _result(req_id, {
            "protocolVersion": client_version or PROTOCOL_VERSION,
            "capabilities": {"tools": {}},
            "serverInfo": SERVER_INFO,
        })

    if method == "ping":
        return _result(req_id, {})

    if method == "tools/list":
        return _result(req_id, {"tools": [
            {"name": name, "description": t["description"], "inputSchema": t["inputSchema"]}
            for name, t in TOOLS.items()
        ]})

    if method == "tools/call":
        params = req.get("params") or {}
        name = params.get("name")
        tool = TOOLS.get(name)
        if tool is None:
            # tool-execution-level error → isError result, so the model sees it
            return _result(req_id, {"content": [{"type": "text", "text": f"unknown tool: {name}"}],
                                    "isError": True})
        try:
            text = tool["handler"](params.get("arguments") or {})
            return _result(req_id, {"content": [{"type": "text", "text": text}]})
        except Exception as exc:  # tool failures are results, not protocol errors
            return _result(req_id, {"content": [{"type": "text", "text": f"error: {exc}"}],
                                    "isError": True})

    return _error(req_id, ERR_METHOD_NOT_FOUND, f"method not found: {method}")


def run(stdin: Optional[TextIO] = None, stdout: Optional[TextIO] = None) -> None:  # pragma: no cover - thin stdio loop
    stdin = stdin or sys.stdin
    stdout = stdout or sys.stdout
    for line in stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except json.JSONDecodeError:
            stdout.write(json.dumps(_error(None, -32700, "parse error")) + "\n")
            stdout.flush()
            continue
        resp = handle_request(req)
        if resp is not None:
            stdout.write(json.dumps(resp) + "\n")
            stdout.flush()


if __name__ == "__main__":
    run()
