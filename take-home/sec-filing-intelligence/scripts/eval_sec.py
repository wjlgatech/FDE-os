#!/usr/bin/env python3
"""eval_sec — grade the QA agent against the hand-verified golden set.

"Correct" here means (the assignment asks us to define it): exact string
match on value + unit + period in a deterministic pipeline — a tolerance band
would only paper over extraction bugs. Refusal behavior is graded BOTH ways:
  * refusal_recall — every must-refuse case refuses (gated at 1.0: one
    hallucinated answer on an unanswerable question is how trust died here)
  * refusal_precision — no answerable case refuses (gated at 1.0)
Citation validity re-verifies every cited quote verbatim against the
extracted corpus. Exit 0 pass / 2 gate failure / 1 malformed.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
from qa import ask  # noqa: E402

GOLDEN = os.path.join(os.path.dirname(_HERE), "data", "golden", "golden-qa.json")
EXTRACTED = os.path.join(os.path.dirname(_HERE), "corpus", "extracted")

GATES = {"answer_accuracy": 1.0, "refusal_recall": 1.0, "refusal_precision": 1.0,
         "citation_validity": 1.0}


def _quote_in_corpus(cite: dict) -> bool:
    path = os.path.join(EXTRACTED, f"{cite['doc_id']}.json")
    if not os.path.exists(path):
        return False
    doc = json.load(open(path))
    page = doc["pages"][cite["page"] - 1]
    hay = " ".join(" ".join(l.split()) for l in page["lines"])
    needle = " ".join(str(cite["quote"]).split())[:120]
    return needle in hay


def evaluate() -> dict:
    golden = json.load(open(GOLDEN))["cases"]
    per, mism = {}, []
    n_ok = 0
    refuse_needed = refuse_fired = 0
    answerable = answered = 0
    quotes_total = quotes_ok = 0
    tag_stats: dict[str, list[int]] = {}
    for case in golden:
        a = ask(case["q"])
        ok = (a["type"] == case["type"])
        for needle in case.get("must", []):
            ok = ok and needle in a["answer"]
        for needle in case.get("must_reason", []):
            ok = ok and any(needle in r for r in a.get("reasons", []))
        if case["type"] == "refusal":
            refuse_needed += 1
            refuse_fired += a["type"] == "refusal"
        else:
            answerable += 1
            answered += a["type"] != "refusal"
        for c in a.get("citations", []):
            quotes_total += 1
            quotes_ok += _quote_in_corpus(c)
        n_ok += ok
        per[case["id"]] = ok
        if not ok:
            mism.append(f"{case['id']}: expected {case['type']} with "
                        f"{case.get('must') or case.get('must_reason')}; got "
                        f"{a['type']}: {a['answer'][:120]}")
        for t in case.get("tags", []):
            tag_stats.setdefault(t, [0, 0])
            tag_stats[t][1] += 1
            tag_stats[t][0] += ok
    n = len(golden)
    metrics = {
        "answer_accuracy": round(n_ok / n, 4),
        "refusal_recall": round(refuse_fired / refuse_needed, 4) if refuse_needed else 1.0,
        "refusal_precision": round(answered / answerable, 4) if answerable else 1.0,
        "citation_validity": round(quotes_ok / quotes_total, 4) if quotes_total else 0.0,
    }
    fails = [f"{k} {metrics[k]} < {v}" for k, v in GATES.items() if metrics[k] < v]
    return {"metrics": metrics, "gate_failures": fails, "mismatches": mism,
            "by_tag": {t: f"{v[0]}/{v[1]}" for t, v in sorted(tag_stats.items())},
            "cases": n, "verdict": "PASS" if not fails else "FAIL"}


def main() -> int:
    try:
        rep = evaluate()
    except (OSError, json.JSONDecodeError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    print(json.dumps(rep["metrics"], indent=2))
    print("by tag:", json.dumps(rep["by_tag"]))
    for m in rep["mismatches"]:
        print("  ✗", m)
    print(f"cases: {rep['cases']} · VERDICT: {rep['verdict']}")
    return 0 if rep["verdict"] == "PASS" else 2


if __name__ == "__main__":
    sys.exit(main())
