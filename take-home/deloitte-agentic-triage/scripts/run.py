#!/usr/bin/env python3
"""run — batch the request stream through the agent, emit every artifact.

    python3 scripts/run.py --out runs/latest

Produces, per run directory:
    decisions.json     one structured record per request (the agent's answers)
    traces.jsonl       every step, tool call, retrieval, context receipt, guard
    checkpoints/<id>.jsonl   durable graph state per request (resumable)

Requests are processed in order through ONE session (shared memory) — that is
the point: R-006 is only catchable because R-001 happened first.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
sys.path.insert(0, _HERE)

from agent import TriageAgent  # noqa: E402


def load_requests(path: str) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Run the triage agent over a request stream.")
    ap.add_argument("--requests", default=os.path.join(_ROOT, "data", "requests.jsonl"))
    ap.add_argument("--corpus", default=os.path.join(_ROOT, "corpus"))
    ap.add_argument("--data", default=os.path.join(_ROOT, "data"))
    ap.add_argument("--out", default=os.path.join(_ROOT, "runs", "latest"))
    ap.add_argument("--budget-tokens", type=int, default=350)
    args = ap.parse_args(argv)

    os.makedirs(os.path.join(args.out, "checkpoints"), exist_ok=True)
    agent = TriageAgent(args.corpus, args.data, budget_tokens=args.budget_tokens)

    decisions: dict[str, dict] = {}
    trace_path = os.path.join(args.out, "traces.jsonl")
    with open(trace_path, "w", encoding="utf-8") as tf:
        for req in load_requests(args.requests):
            def tracer(event, _id=req["id"]):
                tf.write(json.dumps({"request_id": _id, **event}, default=str) + "\n")

            cp = os.path.join(args.out, "checkpoints", f"{req['id']}.jsonl")
            if os.path.exists(cp):
                os.remove(cp)  # a fresh batch run owns its checkpoint stream
            final = agent.process(req, cp, tracer=tracer)
            decisions[req["id"]] = final
            gate = (f" → gate: {final['gate_reason']}"
                    if final.get("status") == "awaiting_human" else "")
            print(f"{req['id']}  {final['decision']:<9}"
                  f"{(final.get('escalate_to') or ''):<24}{gate}")

    with open(os.path.join(args.out, "decisions.json"), "w", encoding="utf-8") as f:
        json.dump(decisions, f, indent=2, sort_keys=True)
    print(f"\nwrote {args.out}/decisions.json, traces.jsonl, checkpoints/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
