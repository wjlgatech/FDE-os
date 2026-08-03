#!/usr/bin/env python3
"""fde-mcp-server — a minimal, dependency-free Model Context Protocol (MCP) server over stdio.

It exposes FDE-os's own skills as MCP tools, so an MCP client (Claude Desktop, Claude Code, any
MCP host) can call them. The seven request→result skills are exposed: `true_score`, `rag_eval`,
`criteria_score`, `eval_loop`, `invisible_workflow_map`, `jd_compile`, `doc_gate`. (The two artifact-builders
that mutate the filesystem — `knowledgefy` and `field-kit-generator` — stay CLI by design; a stdio
tool should return a result, not write files into the host's tree.) This both (a) satisfies the
common JD requirement "1+ Claude MCP integrations" with a real, runnable example, and (b) dogfoods
the repo — the skills become callable tools.

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
    """Score text against the TRUE rubric and apply the ship gate."""
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
    """Run the RAG retrieval eval and optionally gate on thresholds."""
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


def _tool_criteria_score(args: dict) -> str:
    """Score text against explicit criteria and gate on a threshold."""
    cs = _load("skills/criteria-scorer/scripts/criteria_score.py", "criteria_score")
    text = args.get("text")
    criteria = args.get("criteria")
    if not text:
        raise ValueError("provide 'text'")
    if not isinstance(criteria, list):
        raise ValueError("provide 'criteria' (a JSON list of {type, value, question})")
    report = cs.score_artifact(text, criteria)
    threshold = float(args.get("threshold", 1.0))
    passed, reasons = cs.gate(report["score"], threshold, report.get("results"))
    n_pass = sum(1 for r in report["results"] if r["passed"])
    head = f"criteria score: {report['score']:.2f} ({n_pass}/{report['n']} passed)"
    return head + "\nVERDICT: " + ("PASS" if passed else "BLOCK — " + "; ".join(reasons))


def _tool_eval_loop(args: dict) -> str:
    """Pick the winning round (and best single gain) from scored iterations."""
    el = _load("skills/eval-loop/scripts/eval_loop.py", "eval_loop")
    rounds = args.get("rounds")
    if not isinstance(rounds, list) or not rounds:
        raise ValueError("provide 'rounds' (a non-empty JSON list of {label, change, score})")
    result = el.decide(rounds)
    gain = result.get("best_gain")
    gain_s = f"{gain[0]} (+{gain[1]})" if gain else "none"
    return (f"eval-loop: winner '{result['winner_label']}' @ {result['winner_score']} "
            f"over {len(rounds)} round(s); best gain {gain_s}")


def _tool_invisible_workflow_map(args: dict) -> str:
    """Reconstruct the org's decision workflow from observed signals."""
    wm = _load("skills/invisible-workflow-mapper/scripts/workflow_map.py", "workflow_map")
    data = args.get("data") or {"context": args.get("context", {}), "signals": args.get("signals", [])}
    if not data.get("signals"):
        raise ValueError("provide 'signals' (or a 'data' object with signals)")
    threshold = float(args.get("threshold", 0.6))
    report = wm.build_map(data, threshold=threshold)
    return wm.render_md(report, data.get("context"))


def _tool_jd_compile(args: dict) -> str:
    """Compile a job description into a structured competency profile."""
    jc = _load("skills/jd-compiler/scripts/jd_compile.py", "jd_compile")
    text = args.get("text")
    if text is None and args.get("jd_path"):
        with open(os.path.join(_ROOT, args["jd_path"]), encoding="utf-8") as fh:
            text = fh.read()
    if not text:
        raise ValueError("provide 'text' or 'jd_path'")
    jd = jc.compile_jd(text, args.get("name", "jd"))
    return jc.to_note(jd, source=args.get("name", ""))


def _tool_doc_gate(args: dict) -> str:
    """Parse an enterprise doc (docx/xlsx/md/csv) and run the parse-quality gate."""
    du = _load("skills/doc-understanding/scripts/doc_understand.py", "doc_understand")
    path = args.get("path")
    if not path:
        raise ValueError("provide 'path' (repo-relative path to a .docx/.xlsx/.md/.csv)")
    rep = du.parse(os.path.join(_ROOT, path))
    ok, reasons = du.gate(rep, float(args.get("threshold", 0.7)))
    q = rep["quality"]
    head = (f"parse-quality: overall {q['overall']} (coverage {q['coverage']}, "
            f"structure {q['structure']}, fidelity {q['fidelity']})")
    return head + "\nVERDICT: " + ("GO" if ok else "NO-GO — " + "; ".join(reasons))


def _sfos(mod_name: str) -> ModuleType:
    """Load a snowflake-os engine. Its modules import each other by sys.path."""
    scripts = os.path.join(_ROOT, "snowflake-os", "scripts")
    if scripts not in sys.path:
        sys.path.insert(0, scripts)
    return _load(f"snowflake-os/scripts/{mod_name}.py", f"sfos_{mod_name}")


def _tool_snowflake_plan(args: dict) -> str:
    """Ordered, costed Snowflake learning path for a role, exam, or competency set."""
    pathfinder = _sfos("pathfinder")
    cat = _sfos("catalog").Catalog()

    class _A:
        role = args.get("role")
        exam = args.get("exam")
        competency = args.get("competency")
        have = args.get("have", "")
        free_only = bool(args.get("free_only"))
        core_only = bool(args.get("core_only"))
        max_hours = args.get("max_hours")
        json = False

    if not (_A.role or _A.exam or _A.competency):
        raise ValueError("provide one of 'role', 'exam' or 'competency'")
    return pathfinder.render(pathfinder.build_plan(cat, _A))


def _tool_snowflake_readiness(args: dict) -> str:
    """GO/NO-GO on a candidate's Snowflake readiness. Claimed completions score zero."""
    readiness = _sfos("readiness")
    cat = _sfos("catalog").Catalog()
    contract = args.get("contract")
    if isinstance(contract, str):
        contract = json.loads(contract)
    if not isinstance(contract, dict):
        raise ValueError("provide 'contract' as a JSON object with 'role' and 'completions'")
    return readiness.render(readiness.score(cat, contract, float(args.get("threshold", 0.6))))


def _tool_snowflake_catalog(args: dict) -> str:
    """Search the 58-course Snowflake catalogue, or show one course with provenance."""
    catalog = _sfos("catalog")
    cat = catalog.Catalog()
    if code := args.get("code"):
        c = cat.course(code)
        if not c:
            raise ValueError(f"unknown course code {code!r}")
        hrs = c["effort_hours"] if c["effort_hours"] is not None else catalog.UNMEASURED
        return (f"{c['code']} · {c['title']}\n{c['delivery']} · "
                f"{'free' if c['free'] else 'paid'} · {hrs}h · {c['difficulty']}\n"
                f"{c['url']}\n\n{c.get('summary') or ''}")
    terms = args.get("query", "").split()
    if not terms:
        raise ValueError("provide 'query' (search terms) or 'code' (a course code)")
    hits = cat.search(terms, free_only=bool(args.get("free_only")))
    if not hits:
        return (f"no course matches {' '.join(terms)!r}. "
                f"catalogue vocabulary: {', '.join(cat.vocabulary())}")
    return "\n".join(catalog.fmt_course(c) for c in hits[: int(args.get("top", 10))])


def _tool_hub_find(args: dict) -> str:
    """Query the hub's compiled external toolsets (top-rated cited repos) for a capability."""
    hq = _load("skills/repo-compiler/scripts/hub_query.py", "hub_query")
    need = args.get("need")
    if not need:
        raise ValueError("provide 'need' (what capability you're looking for)")
    skills = hq.load_registry()
    results = hq.find(need, skills, top=int(args.get("top", 3)))
    if not results:
        return hq.diagnose(skills)
    return "\n\n".join(hq.render_skill(s, score) for score, s in results)


TOOLS = {
    "snowflake_plan": {
        "description": "Build an ordered, costed Snowflake learning path from the real "
                       "learn.snowflake.com catalogue (58 courses, 12 exams). Give a role, an exam "
                       "code, or competency ids. Returns the sequence, total hours, free/paid split, "
                       "and what share of the mapping is curated judgment rather than published fact.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "role": {"type": "string", "description": "role slug, e.g. 'forward-deployed-engineer'"},
                "exam": {"type": "string", "description": "SnowPro exam code, e.g. 'GES-C02'"},
                "competency": {"type": "string", "description": "comma-separated competency ids"},
                "have": {"type": "string", "description": "comma-separated course codes already done"},
                "free_only": {"type": "boolean", "description": "exclude paid courses"},
                "core_only": {"type": "boolean", "description": "core competencies only"},
                "max_hours": {"type": "number", "description": "budget in hours"},
            },
        },
        "handler": _tool_snowflake_plan,
    },
    "snowflake_readiness": {
        "description": "GO/NO-GO on whether someone is ready for a Snowflake role, scored on "
                       "EVIDENCE: a completion counts only with a badge_url, completion_id or "
                       "verifier. Self-reported and planned completions are reported but score zero.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "contract": {"type": "object",
                             "description": "{role, completions:[{course, badge_url|completion_id|verifier|status}]}"},
                "threshold": {"type": "number", "description": "coverage threshold per competency (default 0.6)"},
            },
            "required": ["contract"],
        },
        "handler": _tool_snowflake_readiness,
    },
    "snowflake_catalog": {
        "description": "Search or inspect the offline snapshot of learn.snowflake.com: 58 courses "
                       "with effort hours, difficulty, free/paid, and the source URL each was "
                       "parsed from. Zero results returns the catalogue's vocabulary, never silence.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "search terms, e.g. 'snowpark python'"},
                "code": {"type": "string", "description": "a course code for full detail, e.g. 'OD-ESS-DWW'"},
                "free_only": {"type": "boolean"},
                "top": {"type": "integer", "description": "max results (default 10)"},
            },
        },
        "handler": _tool_snowflake_catalog,
    },
    "hub_find": {
        "description": "Find which external toolset (compiled from the hub's top-rated cited repos) "
                       "covers a capability — returns the integration recipe (skill/plugin/workflow), "
                       "the honest notGoodAt edges, and the SHA-pinned source. Query this BEFORE "
                       "adopting any external tool.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "need": {"type": "string", "description": "the capability you need, e.g. 'LLM observability evals'"},
                "top": {"type": "integer", "description": "max results (default 3)"},
            },
            "required": ["need"],
        },
        "handler": _tool_hub_find,
    },
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
    "criteria_score": {
        "description": "Score any text artifact against a list of binary, mechanically-checkable "
                       "criteria (min_words, must_match regex, must_contain_number, must_cite, …) → "
                       "0–1 + a gate naming each failed criterion.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "the artifact to score"},
                "criteria": {"type": "array", "description": "list of {type, value, question} criteria"},
                "threshold": {"type": "number", "description": "pass threshold 0–1 (default 1.0 = all must pass)"},
            },
        },
        "handler": _tool_criteria_score,
    },
    "eval_loop": {
        "description": "Given an ordered list of scored artifact versions, return the kept winner + "
                       "the largest accepted gain (keep-on-improvement, revert-on-regression).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "rounds": {"type": "array", "description": "ordered [{label, change, score}, …]; round 0 = baseline"},
            },
        },
        "handler": _tool_eval_loop,
    },
    "invisible_workflow_map": {
        "description": "Reconstruct an org's decision workflow from signals: adoption-readiness score, "
                       "inferred workflow archetype + its adoption traps, the probes to ask next, and a gate.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "signals": {"type": "array", "description": "[{dimension, observation, confidence, source}, …]"},
                "context": {"type": "object", "description": "optional {org, industry, size, tools, notes}"},
                "threshold": {"type": "number", "description": "adoption-readiness gate threshold (default 0.6)"},
            },
        },
        "handler": _tool_invisible_workflow_map,
    },
    "jd_compile": {
        "description": "Compile a Forward-Deployed-Engineer job description into a structured competency "
                       "profile — which FDE clusters it requires, the specific tools it names, its level.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "the JD text"},
                "jd_path": {"type": "string", "description": "repo-relative path to a JD .md (alternative to text)"},
                "name": {"type": "string", "description": "a label for the role (optional)"},
            },
        },
        "handler": _tool_jd_compile,
    },
    "doc_gate": {
        "description": "Parse a messy enterprise document (docx/xlsx/md/csv) into a canonical structured "
                       "representation and run the parse-quality gate (coverage/structure/fidelity) — "
                       "NO-GO on empty parses or unresolved track-changes.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "repo-relative path to the document"},
                "threshold": {"type": "number", "description": "gate threshold on overall quality (default 0.7)"},
            },
            "required": ["path"],
        },
        "handler": _tool_doc_gate,
    },
}


# ----------------------------------------------------------------- JSON-RPC dispatch

def _result(req_id: object, result: object) -> dict:
    """Wrap a payload as a JSON-RPC success response."""
    return {"jsonrpc": "2.0", "id": req_id, "result": result}


def _error(req_id: object, code: int, message: str) -> dict:
    """Wrap a code+message as a JSON-RPC error response."""
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
    """Blocking stdio loop: one JSON-RPC message per line."""
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
