#!/usr/bin/env python3
"""criteria-scorer — score an artifact against binary pass/fail criteria, offline & deterministically.

The simplest, most general artifact eval (the third gate alongside `true-scorer` and
`rag-eval-harness`). Each criterion is a *typed, mechanically-checkable predicate* — not a free-form
LLM judgment — so the core is reproducible and needs no network. This covers most real criteria
(length caps, required elements, forbidden buzzwords, "contains a concrete number" — the single
biggest win in the source article). Subjective criteria ("is the tone right?") are an opt-in
LLM-judge hook, NOT part of this deterministic core (same posture as rag-eval-harness).

Criteria file = a JSON list; each criterion:
  {"question": "...", "type": "<type>", "value": <as needed>}
Types:
  min_words           value:int   — artifact has at least value words
  max_words           value:int   — artifact has at most value words
  must_match          value:regex — artifact matches the regex (re.search, case-insensitive)
  must_not_match      value:[str|regex] OR str — artifact matches NONE of these (e.g. a buzzword list)
  must_contain_number value:(none) — artifact contains a digit
  must_cite           value:(none) — artifact contains a [bracket] or http(s) citation

Score = mean of pass(1)/fail(0) over criteria, 0.00–1.00. gate(score, threshold) -> (passed, reasons).

Usage:
  python3 criteria_score.py score <artifact.md|-> <criteria.json> --threshold 0.8
"""
from __future__ import annotations

import argparse
import json
import re
import sys

WORD_RE = re.compile(r"\S+")
NUMBER_RE = re.compile(r"\d")
CITE_RE = re.compile(r"\[[^\]]+\]|https?://\S+")


class CriterionError(ValueError):
    """Raised for an unknown criterion type or malformed criterion — never a silent skip."""


def _words(text: str) -> int:
    return len(WORD_RE.findall(text))


def evaluate_criterion(text: str, crit: dict) -> bool:
    """Return True (pass) / False (fail) for one criterion. Raises CriterionError on unknown type."""
    ctype = crit.get("type")
    val = crit.get("value")
    low = text.lower()
    if ctype == "min_words":
        return _words(text) >= int(val)
    if ctype == "max_words":
        return _words(text) <= int(val)
    if ctype == "must_match":
        return re.search(str(val), text, re.IGNORECASE) is not None
    if ctype == "must_not_match":
        patterns = val if isinstance(val, list) else [val]
        return not any(re.search(str(p), text, re.IGNORECASE) for p in patterns)
    if ctype == "must_contain_number":
        return NUMBER_RE.search(text) is not None
    if ctype == "must_cite":
        return CITE_RE.search(text) is not None
    raise CriterionError(f"unknown criterion type: {ctype!r}")


def score_artifact(text: str, criteria: list[dict]) -> dict:
    """Return {score, n, results:[{question,type,passed}]}. Deterministic."""
    results = []
    for crit in criteria:
        passed = evaluate_criterion(text, crit)
        results.append({
            "question": crit.get("question", crit.get("type", "?")),
            "type": crit.get("type"),
            "passed": passed,
        })
    n = len(results)
    score = (sum(1 for r in results if r["passed"]) / n) if n else 0.0
    return {"score": round(score, 4), "n": n, "results": results}


def gate(score: float, threshold: float, results: list[dict] | None = None) -> tuple[bool, list[str]]:
    """Pass iff score >= threshold. Reasons name each failed criterion."""
    reasons: list[str] = []
    if results:
        for r in results:
            if not r["passed"]:
                reasons.append(f"FAIL: {r['question']}")
    passed = score >= threshold
    if not passed and not reasons:
        reasons.append(f"score {score} < threshold {threshold}")
    return passed, reasons


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("score")
    s.add_argument("artifact", help="path to the artifact, or '-' for stdin")
    s.add_argument("criteria", help="path to a JSON criteria list")
    s.add_argument("--threshold", type=float, default=0.8)
    args = ap.parse_args()

    text = sys.stdin.read() if args.artifact == "-" else open(args.artifact, encoding="utf-8").read()
    try:
        with open(args.criteria, encoding="utf-8") as fh:
            criteria = json.load(fh)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"error: cannot read criteria: {exc}", file=sys.stderr)
        return 2
    if not isinstance(criteria, list):
        print("error: criteria file must be a JSON list", file=sys.stderr)
        return 2

    try:
        report = score_artifact(text, criteria)
    except CriterionError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    print(f"criteria score: {report['score']} ({sum(1 for r in report['results'] if r['passed'])}/{report['n']} passed)")
    for r in report["results"]:
        print(f"  [{'PASS' if r['passed'] else 'FAIL'}] {r['question']}")
    passed, reasons = gate(report["score"], args.threshold, report["results"])
    if passed:
        print(f"VERDICT: PASS (>= {args.threshold})")
        return 0
    print("VERDICT: BLOCK — " + "; ".join(reasons))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
