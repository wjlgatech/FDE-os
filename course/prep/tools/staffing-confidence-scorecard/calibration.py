#!/usr/bin/env python3
"""calibration — validate the gate against ground truth, and recalibrate.

The move that makes this more than a form: a GO is a *prediction*. The only way to trust
it is to check it against what actually happened — the exact discipline behind evidence-
based trait inference (infer from evidence, then validate the inferred scores against a
ground-truth criterion; e.g. the Auburn-led multi-university validation of AI-inferred
personality scores). Here the ground truth is the delivery outcome.

Feed it decisions with known outcomes:
    {"id": "...", "predicted_go": true, "role_type": "technical", "outcome": "delivered"}
outcomes: delivered | went_dark | underperformed | rolled_off | pending

It reports whether the gate is actually predictive:
  - GO precision      = delivered / (GO decisions with a performance outcome)
  - false-GO rate     = (went_dark + underperformed) / same denominator   ← the reputation-damaging error
  - coverage          = decisions with a KNOWN outcome / all decisions     ← honesty: pending is excluded, never a fake pass
`rolled_off` is neutral (left for reasons unrelated to performance) → excluded from precision.

Gate: the rubric is "validated" only if false-GO rate ≤ max_false_go AND enough outcomes
exist to measure it. Unmeasured ⇒ NOT validated (never a pass on no evidence). Exits
non-zero when not validated, so CI/monitoring catches a gate that has drifted out of
calibration and needs its bar raised.

Deterministic, stdlib-only, offline.
"""
from __future__ import annotations

import argparse
import json
import sys

PERF_OUTCOMES = ("delivered", "went_dark", "underperformed")   # count toward precision
KNOWN = PERF_OUTCOMES + ("rolled_off",)                        # known, but rolled_off is neutral
MIN_OUTCOMES = 5                                               # below this we can't claim validation


def calibrate(records: list[dict], max_false_go: float = 0.10, min_outcomes: int = MIN_OUTCOMES) -> dict:
    total = len(records)
    known = [r for r in records if r.get("outcome") in KNOWN]
    go_scored = [r for r in known if r.get("predicted_go") and r.get("outcome") in PERF_OUTCOMES]
    delivered = [r for r in go_scored if r["outcome"] == "delivered"]
    false_go = [r for r in go_scored if r["outcome"] in ("went_dark", "underperformed")]

    n = len(go_scored)
    precision = (len(delivered) / n) if n else None
    false_go_rate = (len(false_go) / n) if n else None
    coverage = (len(known) / total) if total else 0.0

    measurable = n >= min_outcomes
    validated = bool(measurable and false_go_rate is not None and false_go_rate <= max_false_go)

    if not measurable:
        verdict = f"NOT VALIDATED — only {n} GO decision(s) with a performance outcome (need {min_outcomes}). Not measured ≠ passed."
    elif validated:
        verdict = f"VALIDATED — false-GO rate {false_go_rate:.0%} ≤ {max_false_go:.0%}. The gate predicts delivery."
    else:
        verdict = (f"NOT VALIDATED — false-GO rate {false_go_rate:.0%} > {max_false_go:.0%}. "
                   "Recalibrate: raise the work-sample bar or tighten the reference gate before recommending on it.")

    return {
        "validated": validated, "measurable": measurable,
        "go_precision": precision, "false_go_rate": false_go_rate,
        "coverage": coverage, "n_go_scored": n, "n_total": total,
        "verdict": verdict,
    }


def render(r: dict) -> str:
    def pct(x): return "n/a" if x is None else f"{x:.0%}"
    L = ["gate calibration (predicted GO vs actual outcome)", "=" * 48, ""]
    L.append(f"  GO precision   : {pct(r['go_precision'])}   (delivered / scored GO decisions)")
    L.append(f"  false-GO rate  : {pct(r['false_go_rate'])}   (went-dark or underperformed — the costly error)")
    L.append(f"  coverage       : {pct(r['coverage'])}   ({r['n_go_scored']} scored GO of {r['n_total']} decisions; pending excluded)")
    L.append("")
    L.append(("✅ " if r["validated"] else "⛔ ") + r["verdict"])
    return "\n".join(L)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Validate the staffing gate against real outcomes.")
    ap.add_argument("records", help="path to decisions JSON (list), or - for stdin")
    ap.add_argument("--max-false-go", type=float, default=0.10)
    ap.add_argument("--min-outcomes", type=int, default=MIN_OUTCOMES)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    raw = sys.stdin.read() if args.records == "-" else open(args.records, encoding="utf-8").read()
    report = calibrate(json.loads(raw), args.max_false_go, args.min_outcomes)
    print(json.dumps(report, indent=2) if args.json else render(report))
    return 0 if report["validated"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
