#!/usr/bin/env python3
"""forms_to_candidate — turn the three Microsoft Forms exports into one candidate.json.

The bulk path for a 100-person center: no hand-editing JSON. Export each Form to CSV
(Forms → Open in Excel → Save As .csv), then:

    python3 forms_to_candidate.py merge \\
        --refs reference.csv --tech worksample.csv --teach teachback.csv \\
        --id anon-0042 --role technical  | python3 scorecard.py score -

Columns are matched by keyword against the question wording in ../instruments/*, NOT by
position — so re-ordering questions in Forms won't silently break it. A missing required
column is a hard error (fail loud), never a silent wrong answer. stdlib only, offline.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys


def _find_col(header: list[str], *keywords: str) -> str:
    """Return the first column whose lowercased name contains ALL keywords."""
    for col in header:
        low = col.lower()
        if all(k in low for k in keywords):
            return col
    raise KeyError(f"no column matching {keywords!r} in: {header}")


def _rows(path: str) -> tuple[list[str], list[dict]]:
    with open(path, newline="", encoding="utf-8-sig") as f:
        r = csv.DictReader(f)
        return (r.fieldnames or []), list(r)


def _id_col(header: list[str]) -> str:
    # Forms exports vary; accept an explicit id column or a "candidate" question.
    for kw in (("candidate", "id"), ("candidate",), ("id",)):
        try:
            return _find_col(header, *kw)
        except KeyError:
            continue
    raise KeyError(f"no candidate-id column in: {header}")


def _yes(v: str) -> bool:
    return str(v).strip().lower() in ("yes", "true", "y", "1")


def build_reliability(path: str, cid: str) -> dict:
    header, rows = _rows(path)
    idc = _id_col(header)
    rel = _find_col(header, "relationship")
    again = _find_col(header, "staff")            # "...staff them ... again?"
    slip = _find_col(header, "slipped")           # proactive / late / went dark
    nosh = _find_col(header, "no-show")           # never / once / repeatedly
    refs = []
    for row in rows:
        if str(row.get(idc, "")).strip() != cid:
            continue
        relv = str(row.get(rel, "")).lower()
        slipv = str(row.get(slip, "")).lower()
        noshv = str(row.get(nosh, "")).lower()
        refs.append({
            "source": "client_team" if "client" in relv else "internal_team",
            "worked_with": "other" not in relv and relv.strip() != "",
            "would_staff_again": _yes(row.get(again, "")),
            "went_dark_or_noshow": ("went dark" in slipv) or (noshv in ("once", "repeatedly")),
        })
    return {"references": refs}


def build_technical(path: str, cid: str) -> dict:
    header, rows = _rows(path)
    idc = _id_col(header)
    obs = _find_col(header, "observe")
    # the five 0-3 rubric items, matched by distinctive keyword sets.
    # NB: multi-keyword on purpose — "eval" alone also matches "Retrieval", so require "eval"+"gate".
    item_kw = [("calls", "tool"), ("retrieval",), ("eval", "gate"), ("legible",), ("trade",)]
    cols = [_find_col(header, *kw) for kw in item_kw]
    thr_col = None
    for c in header:
        if "bar" in c.lower() or "threshold" in c.lower():
            thr_col = c
    for row in rows:
        if str(row.get(idc, "")).strip() != cid:
            continue
        scores = [int(float(row[c])) for c in cols]
        score = round(sum(scores) / (len(cols) * 3), 2)
        thr = float(row[thr_col]) if thr_col and row.get(thr_col) else 0.70
        return {"work_sample": {"observed": _yes(row.get(obs, "")), "score": score, "threshold": thr}}
    raise KeyError(f"no technical row for id {cid!r} in {path}")


def build_resourcefulness(path: str, cid: str) -> dict:
    header, rows = _rows(path)
    idc = _id_col(header)
    ran = _find_col(header, "run")            # "...actually run?"
    rep = _find_col(header, "repeat")         # non-engineer could repeat
    uns = _find_col(header, "unstuck")
    for row in rows:
        if str(row.get(idc, "")).strip() != cid:
            continue
        return {"teach_back": {
            "artifact_worked": _yes(row.get(ran, "")),
            "teachback_clear": _yes(row.get(rep, "")),
            "got_unstuck": str(row.get(uns, "")).lower().startswith("self"),
        }}
    raise KeyError(f"no teach-back row for id {cid!r} in {path}")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    m = sub.add_parser("merge", help="merge three Forms CSVs into candidate.json (stdout)")
    m.add_argument("--refs", required=True)
    m.add_argument("--tech", required=True)
    m.add_argument("--teach", required=True)
    m.add_argument("--id", required=True, dest="cid")
    m.add_argument("--role", default="technical", choices=["technical", "non_technical"])
    args = ap.parse_args(argv)

    candidate = {
        "candidate": args.cid,
        "role_type": args.role,
        "reliability": build_reliability(args.refs, args.cid),
        "technical_competence": build_technical(args.tech, args.cid),
        "resourcefulness": build_resourcefulness(args.teach, args.cid),
    }
    json.dump(candidate, sys.stdout, indent=2)
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
