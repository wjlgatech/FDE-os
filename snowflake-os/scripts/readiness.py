#!/usr/bin/env python3
"""snowflake-os · readiness — is this person actually ready? GO / NO-GO, on evidence.

Pure stdlib, offline, deterministic. Exit 0 = GO, 2 = NO-GO, 1 = bad input.

    python3 snowflake-os/scripts/readiness.py score snowflake-os/examples/fde-readiness.json
    python3 snowflake-os/scripts/readiness.py score <contract.json> --json

THE RULE THAT MAKES THIS WORTH RUNNING — inherited from FDE-os's outcome-contract
discipline: **claimed never counts.** A completion is credited only when it
carries verifiable evidence. Everything else is reported in full and scored zero.

  verified   badge_url | completion_id | verifier — a third party can check it.  COUNTS
  self       "I did it", a date, a screenshot the tool cannot follow.           reported, scores 0
  planned    intends to do it.                                                  reported, scores 0

So an engineer who has *done* nothing but *claims* everything scores 0.0 and gets
NO-GO. That is the feature. A learning plan that cannot fail is a brochure.

A competency is COVERED when the verified hours against it reach the threshold
share of the hours snowflake-os maps to it. Core competencies gate the verdict;
supporting ones are reported but cannot block.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from catalog import Catalog  # noqa: E402

VERIFIED_FIELDS = ("badge_url", "completion_id", "verifier")
DEFAULT_THRESHOLD = 0.6


def evidence_class(entry: dict) -> tuple[str, str]:
    """→ (class, why). The only place evidence strength is decided."""
    if entry.get("status") == "planned":
        return "planned", "not attempted yet"
    for f in VERIFIED_FIELDS:
        if entry.get(f):
            return "verified", f"{f}={entry[f]}"
    return "self", "self-reported: no badge_url, completion_id or verifier"


def score(cat: Catalog, contract: dict, threshold: float) -> dict:
    role = contract.get("role")
    spec = cat.role_competencies(role) if role else None
    if not spec:
        raise SystemExit(
            f"contract needs a known `role`. got {role!r}; "
            f"known: {', '.join(sorted(cat.roles))}"
        )

    graded, unknown = {}, []
    for entry in contract.get("completions", []):
        code = str(entry.get("course", "")).upper()
        course = cat.course(code)
        if not course:
            unknown.append(code)
            continue
        cls, why = evidence_class(entry)
        graded[code] = {
            "code": code,
            "title": course["title"],
            "hours": course["effort_hours"] or 0,
            "evidence": cls,
            "why": why,
        }

    results, blocking_gaps = [], []
    for tier in ("core", "supporting"):
        for cid in spec.get(tier, []):
            comp = cat.competencies[cid]
            units = cat.requirement_units(cid)
            codes = {c["code"] for c in cat.competency_courses(cid)}
            verified_codes = {g["code"] for g in graded.values()
                              if g["code"] in codes and g["evidence"] == "verified"}
            discounted = [g for g in graded.values()
                          if g["code"] in codes and g["evidence"] != "verified"]

            # Credit a unit when ANY of its alternatives is verified; credit the
            # unit's (cheapest-member) hours, so satisfying a requirement twice
            # cannot inflate coverage past what the requirement was worth.
            required_hours = sum(u["hours"] for u in units)
            earned_hours = sum(u["hours"] for u in units if verified_codes & set(u["codes"]))
            unmet = [u for u in units if not (verified_codes & set(u["codes"]))]
            cov = (earned_hours / required_hours) if required_hours else 0.0
            covered = cov >= threshold
            results.append({
                "competency": cid,
                "name": comp["name"],
                "tier": tier,
                "required_hours": round(required_hours, 2),
                "verified_hours": round(earned_hours, 2),
                "coverage": round(cov, 3),
                "covered": covered,
                "verified_courses": sorted(verified_codes),
                "discounted_courses": [
                    {"code": g["code"], "evidence": g["evidence"], "why": g["why"]} for g in discounted
                ],
                "missing_requirements": [
                    (u["codes"][0] if u["kind"] == "course" else " | ".join(u["codes"]))
                    for u in unmet
                ],
            })
            if tier == "core" and not covered:
                blocking_gaps.append(cid)

    core = [r for r in results if r["tier"] == "core"]
    verdict = "GO" if core and not blocking_gaps else "NO-GO"
    all_discounted = [d for r in results for d in r["discounted_courses"]]
    return {
        "candidate": contract.get("candidate", "unnamed"),
        "role": role,
        "threshold": threshold,
        "verdict": verdict,
        "blocking_gaps": blocking_gaps,
        "core_covered": f"{sum(1 for r in core if r['covered'])}/{len(core)}",
        "competencies": results,
        "evidence_summary": {
            "verified": sum(1 for g in graded.values() if g["evidence"] == "verified"),
            "self_reported_discounted": sum(1 for g in graded.values() if g["evidence"] == "self"),
            "planned_discounted": sum(1 for g in graded.values() if g["evidence"] == "planned"),
            "unknown_course_codes": unknown,
        },
        "discounted_detail": all_discounted,
    }


def render(r: dict) -> str:
    out = [
        f"READINESS · {r['candidate']} → {r['role']}",
        f"  threshold {r['threshold']:.0%} of required hours (alternatives collapsed), verified evidence only",
        "",
    ]
    for c in r["competencies"]:
        mark = "✓" if c["covered"] else ("✗" if c["tier"] == "core" else "·")
        out.append(
            f"  {mark} {c['name'][:42]:<42} [{c['tier']:<10}] "
            f"{c['verified_hours']:>5g}/{c['required_hours']:<6g}h  {c['coverage']:.0%}"
        )
        for d in c["discounted_courses"]:
            out.append(f"       ↳ {d['code']} NOT counted — {d['why']}")
        if not c["covered"] and c["tier"] == "core":
            out.append(f"       ↳ still needed: {', '.join(c['missing_requirements']) or '—'}")
    e = r["evidence_summary"]
    out += [
        "",
        f"  evidence: {e['verified']} verified · {e['self_reported_discounted']} self-reported (scored 0) "
        f"· {e['planned_discounted']} planned (scored 0)",
    ]
    if e["unknown_course_codes"]:
        out.append(f"  unknown course codes ignored: {', '.join(e['unknown_course_codes'])}")
    out += ["", f"  core competencies covered: {r['core_covered']}"]
    if r["blocking_gaps"]:
        out.append(f"  blocking gaps: {', '.join(r['blocking_gaps'])}")
    out.append("")
    out.append(f"VERDICT: {r['verdict']}")
    if r["verdict"] == "NO-GO":
        out.append("  (a NO-GO is a working gate, not an error — close the gaps and re-run)")
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("score", help="score a readiness contract")
    s.add_argument("contract")
    s.add_argument("--threshold", type=float, default=DEFAULT_THRESHOLD)
    s.add_argument("--json", action="store_true")
    args = p.parse_args(argv)

    path = Path(args.contract)
    if not path.exists():
        print(f"no such contract: {path}", file=sys.stderr)
        return 1
    try:
        contract = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"contract is not valid JSON: {e}", file=sys.stderr)
        return 1

    result = score(Catalog(), contract, args.threshold)
    print(json.dumps(result, indent=2, ensure_ascii=False) if args.json else render(result))
    return 0 if result["verdict"] == "GO" else 2


if __name__ == "__main__":
    raise SystemExit(main())
