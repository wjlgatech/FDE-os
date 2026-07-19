#!/usr/bin/env python3
"""outcome-contract — score an FDE engagement against its outcome contract, offline & deterministically.

The talk-derived mechanism (the Outcome-Based Model): a client pays for the *result* — time saved,
calls answered, orders taken — not the software license. That only works if the outcomes are encoded
as DATA and gated on EVIDENCE. This is the engagement-level sibling of `true-scorer` (artifact
quality) and `rag-eval-harness` (retrieval quality): same posture — deterministic core, no network,
no evidence ⇒ No.

Contract file = JSON:
  {
    "engagement": "<slug>",
    "outcomes": [
      {
        "id": "call-answer-rate",
        "statement": "AI receptionist answers calls without human handoff",
        "metric": "answered_without_handoff_pct",
        "baseline": 0,
        "target": 60,
        "direction": ">=",            // or "<="
        "blocking": true,             // blocking outcomes decide the gate
        "evidence": {
          "kind": "measured",         // measured | claimed | none
          "value": 72.5,
          "source": "https://... or path — REQUIRED for measured"
        }
      }
    ]
  }

Honesty rules (the BRACE posture):
  - PASS requires *measured* evidence meeting the target. Nothing else passes.
  - "claimed" evidence (a number without an independent source, or kind=claimed) is reported but
    NEVER counts as a pass — prefer observed over claimed.
  - measured evidence WITHOUT a source is downgraded to claimed, loudly.
  - kind=none (or no evidence block) ⇒ NOT_MEASURED — excluded from passing, never a fake pass.
  - Gate: GO iff EVERY blocking outcome is PASS. A blocking outcome that is FAIL, CLAIMED, or
    NOT_MEASURED forces NO-GO — the gate cannot pass on unmeasured items.
  - Exit codes: 0 = GO, 2 = NO-GO, 1 = malformed contract. CI-able by construction.

Usage:
  python3 outcome_score.py score <contract.json>
  python3 outcome_score.py score <contract.json> --json
"""
from __future__ import annotations

import argparse
import json
import sys

VALID_KINDS = {"measured", "claimed", "none"}
VALID_DIRECTIONS = {">=", "<="}

PASS, FAIL, CLAIMED, NOT_MEASURED = "PASS", "FAIL", "CLAIMED", "NOT_MEASURED"


class ContractError(ValueError):
    """Raised for a malformed contract — never a silent skip."""


def _require(cond: bool, msg: str) -> None:
    if not cond:
        raise ContractError(msg)


def score_outcome(o: dict) -> dict:
    """Score one outcome. Returns {id, status, detail, blocking, delta_vs_baseline}."""
    _require(isinstance(o, dict), "outcome must be an object")
    for field in ("id", "metric", "target", "direction"):
        _require(field in o, f"outcome missing required field '{field}'")
    _require(o["direction"] in VALID_DIRECTIONS,
             f"outcome '{o['id']}': direction must be one of {sorted(VALID_DIRECTIONS)}")
    blocking = bool(o.get("blocking", True))

    ev = o.get("evidence") or {"kind": "none"}
    kind = ev.get("kind", "none")
    _require(kind in VALID_KINDS,
             f"outcome '{o['id']}': evidence.kind must be one of {sorted(VALID_KINDS)}")

    if kind == "none":
        return {"id": o["id"], "status": NOT_MEASURED, "blocking": blocking,
                "detail": "no evidence — not measured (excluded, never a fake pass)"}

    _require("value" in ev, f"outcome '{o['id']}': evidence needs a numeric 'value'")
    value = ev["value"]
    _require(isinstance(value, (int, float)) and not isinstance(value, bool),
             f"outcome '{o['id']}': evidence.value must be a number")

    # measured without a source is a claim wearing a lab coat — downgrade loudly
    if kind == "measured" and not ev.get("source"):
        kind = "claimed"
        downgraded = True
    else:
        downgraded = False

    if kind == "claimed":
        note = "downgraded: measured-without-source" if downgraded else "claimed, not independently sourced"
        return {"id": o["id"], "status": CLAIMED, "blocking": blocking, "value": value,
                "detail": f"{note} — reported but never counts as a pass"}

    target = o["target"]
    meets = value >= target if o["direction"] == ">=" else value <= target
    status = PASS if meets else FAIL
    result = {"id": o["id"], "status": status, "blocking": blocking, "value": value,
              "target": target, "direction": o["direction"],
              "detail": f"measured {value} vs target {o['direction']} {target} ({ev.get('source')})"}
    if isinstance(o.get("baseline"), (int, float)) and not isinstance(o.get("baseline"), bool):
        result["delta_vs_baseline"] = value - o["baseline"]
    return result


def score_contract(contract: dict) -> dict:
    _require(isinstance(contract, dict), "contract must be a JSON object")
    _require(bool(contract.get("engagement")), "contract needs an 'engagement' slug")
    outcomes = contract.get("outcomes")
    _require(isinstance(outcomes, list) and outcomes, "contract needs a non-empty 'outcomes' list")
    ids = [o.get("id") for o in outcomes if isinstance(o, dict)]
    _require(len(ids) == len(set(ids)), "outcome ids must be unique")

    results = [score_outcome(o) for o in outcomes]
    blocking = [r for r in results if r["blocking"]]
    _require(bool(blocking), "contract needs at least one blocking outcome")
    go = all(r["status"] == PASS for r in blocking)
    return {
        "engagement": contract["engagement"],
        "verdict": "GO" if go else "NO-GO",
        "outcomes": results,
        "counts": {s: sum(1 for r in results if r["status"] == s)
                   for s in (PASS, FAIL, CLAIMED, NOT_MEASURED)},
    }


def render(report: dict) -> str:
    lines = [f"outcome-contract: {report['engagement']} — verdict: {report['verdict']}"]
    for r in report["outcomes"]:
        mark = {"PASS": "✓", "FAIL": "✗", "CLAIMED": "~", "NOT_MEASURED": "∅"}[r["status"]]
        block = "blocking" if r["blocking"] else "advisory"
        lines.append(f"  [{mark} {r['status']}] ({block}) {r['id']}: {r['detail']}")
    c = report["counts"]
    lines.append(f"  totals: {c['PASS']} pass · {c['FAIL']} fail · {c['CLAIMED']} claimed · "
                 f"{c['NOT_MEASURED']} not measured")
    lines.append(f"VERDICT: {report['verdict']}"
                 + ("" if report["verdict"] == "GO"
                    else " (a blocking outcome is not a measured pass — the gate cannot pass on unmeasured items)"))
    return "\n".join(lines)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Score an engagement outcome contract (GO/NO-GO).")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sc = sub.add_parser("score", help="score a contract file")
    sc.add_argument("contract")
    sc.add_argument("--json", action="store_true", help="emit the JSON report instead of text")
    args = ap.parse_args(argv)

    try:
        with open(args.contract, encoding="utf-8") as f:
            contract = json.load(f)
        report = score_contract(contract)
    except (ContractError, json.JSONDecodeError, OSError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1

    print(json.dumps(report, indent=2) if args.json else render(report))
    return 0 if report["verdict"] == "GO" else 2


if __name__ == "__main__":
    raise SystemExit(main())
