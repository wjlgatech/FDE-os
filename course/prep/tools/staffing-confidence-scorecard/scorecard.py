#!/usr/bin/env python3
"""staffing-confidence-scorecard — vet a candidate on the three criteria that
actually predict whether staffing them will damage or build your credibility.

The problem this solves (from a real AI-delivery lead who got burned): you
recommend someone who looks great on paper, they no-show / go dark / don't
deliver, and the blast radius is your whole team's ability to ever recommend
anyone again. Resumes and "will you be a reference?" don't catch this. The
hiring-science record is blunt about why: **work samples and _structured_
references are the highest-validity predictors; unstructured reference checks
are near-noise.** (Schmidt & Hunter, 1998.) Structure is the multiplier.

Three criteria, each scored by its highest-validity instrument:

  reliability          → Structured Reference Protocol   (did they show up & deliver, per people who worked with them)
  technical_competence → Work Sample (observed, graded)  (what THEY built, fresh, on one rubric)
  resourcefulness      → Learn-and-Teach-Back            (learn an unfamiliar tool in a day, make it work, teach it)

Evidence, not assertion. Reliability requires a real vouch from someone who
worked with them (client team OR internal team both count); technical requires
an *observed* work sample above the role's bar; resourcefulness requires a
*working* artifact plus a teach-back a non-engineer can follow (outcome over
method — using AI or asking for help is fine, it's noted, never penalized).

The gate is role-aware and AND-style — a strong score on one axis never rescues
a weak one:
  - reliability is a HARD gate for every role (this is the axis that burns you).
  - technical_competence is a hard gate for technical roles.
  - resourcefulness is a hard gate for every role (the work is constant tool-learning).
  A single "went dark / no-showed" flag from any reference is an automatic NO-GO.

Deterministic, stdlib-only, offline. Same posture as coding-drill-kit /
partner-trust-ledger / true-scorer. No candidate PII belongs in this repo — feed
it anonymized ids.
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field

ROLE_TYPES = ("technical", "non_technical")


@dataclass
class AxisResult:
    name: str
    passed: bool
    required: bool
    detail: str
    tier: str = "none"           # none | claimed | vouch | observed
    pattern: bool = False        # >=2 independent positive signals


# ---------- reliability ----------

def score_reliability(block: dict) -> AxisResult:
    refs = block.get("references", []) if block else []
    worked_with = [r for r in refs if r.get("worked_with")]
    dark_flags = [r for r in refs if r.get("went_dark_or_noshow")]
    staff_again = [r for r in worked_with if r.get("would_staff_again")]

    # A single credible "went dark / no-show" is disqualifying — it is the exact
    # failure mode that damages the recommender. It is never averaged away.
    if dark_flags:
        return AxisResult(
            "reliability", passed=False, required=True, tier="vouch",
            detail="a reference reported a no-show / went-dark event — automatic NO-GO",
        )
    if not worked_with:
        return AxisResult(
            "reliability", passed=False, required=True, tier="none",
            detail="no reference from anyone who actually worked with them — the exact gap that burns a recommendation",
        )
    if not staff_again:
        return AxisResult(
            "reliability", passed=False, required=True, tier="vouch",
            detail="someone worked with them but none would staff them on a client-facing role again",
        )
    return AxisResult(
        "reliability", passed=True, required=True, tier="vouch",
        pattern=len(staff_again) >= 2,
        detail=f"{len(staff_again)} would-staff-again vouch(es) from people who worked with them, zero dark flags",
    )


# ---------- technical competence ----------

def score_technical(block: dict, role_type: str) -> AxisResult:
    required = role_type == "technical"
    ws = (block or {}).get("work_sample")
    if not ws:
        return AxisResult(
            "technical_competence", passed=False, required=required, tier="none",
            detail="no work sample on record — a resume/claim is not evidence of build ability",
        )
    if not ws.get("observed"):
        return AxisResult(
            "technical_competence", passed=False, required=required, tier="claimed",
            detail="work sample was not observed fresh — cannot attribute the work to the candidate",
        )
    score = float(ws.get("score", 0.0))
    threshold = float(ws.get("threshold", 0.7))
    ok = score >= threshold
    return AxisResult(
        "technical_competence", passed=ok, required=required, tier="observed",
        detail=f"observed work sample scored {score:.2f} (bar {threshold:.2f}) → {'clears' if ok else 'below'} the bar",
    )


# ---------- resourcefulness / learning agility ----------

def score_resourcefulness(block: dict) -> AxisResult:
    tb = (block or {}).get("teach_back")
    if not tb:
        return AxisResult(
            "resourcefulness", passed=False, required=True, tier="none",
            detail="no learn-and-teach-back on record — learning agility unproven",
        )
    worked = bool(tb.get("artifact_worked"))
    clear = bool(tb.get("teachback_clear"))
    ok = worked and clear
    unstuck = " (self-directed unblocking observed)" if tb.get("got_unstuck") else ""
    if not worked:
        detail = "built nothing that runs from the unfamiliar tool — outcome bar not met"
    elif not clear:
        detail = "made it work but could not teach it back clearly — half the job (they must teach citizen developers)"
    else:
        detail = "learned an unfamiliar tool in the window, shipped a working artifact, taught it back clearly" + unstuck
    return AxisResult(
        "resourcefulness", passed=ok, required=True, tier="observed", detail=detail,
    )


def evaluate(candidate: dict) -> dict:
    role_type = candidate.get("role_type", "technical")
    if role_type not in ROLE_TYPES:
        raise ValueError(f"role_type must be one of {ROLE_TYPES}, got {role_type!r}")

    axes = [
        score_reliability(candidate.get("reliability", {})),
        score_technical(candidate.get("technical_competence", {}), role_type),
        score_resourcefulness(candidate.get("resourcefulness", {})),
    ]
    blockers = [a for a in axes if a.required and not a.passed]
    go = not blockers
    return {"role_type": role_type, "axes": axes, "blockers": blockers, "go": go}


def render(report: dict) -> str:
    lines = ["staffing-confidence scorecard", "=" * 29, f"role type: {report['role_type']}", ""]
    for a in report["axes"]:
        mark = "✅" if a.passed else ("⛔" if a.required else "◽")
        req = "" if a.required else "  (informational for this role)"
        pat = "  ⟳ pattern" if a.pattern else ""
        lines.append(f"  {mark} {a.name:<22}{req}{pat}")
        lines.append(f"       {a.detail}")
    lines.append("")
    if report["go"]:
        lines.append("VERDICT: ✅ GO — evidence clears every required axis. Safe to stake a recommendation.")
    else:
        lines.append("VERDICT: ⛔ NO-GO — do not recommend yet. Close these first:")
        for b in report["blockers"]:
            lines.append(f"  • {b.name}: {b.detail}")
    return "\n".join(lines)


TEMPLATE = {
    "candidate": "anon-0001",
    "role_type": "technical",
    "reliability": {
        "references": [
            {"source": "client_team", "worked_with": True, "would_staff_again": True,
             "went_dark_or_noshow": False, "communicated_proactively": True, "delivered_end_to_end": True}
        ]
    },
    "technical_competence": {"work_sample": {"observed": True, "score": 0.0, "threshold": 0.7}},
    "resourcefulness": {"teach_back": {"artifact_worked": False, "teachback_clear": False, "got_unstuck": False}},
}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Score a candidate against the three staffing-confidence criteria.")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("score", help="score a candidate.json (use - for stdin)")
    p.add_argument("candidate")
    p.add_argument("--json", action="store_true")
    sub.add_parser("template", help="print a blank candidate record")

    args = ap.parse_args(argv)
    if args.cmd == "template":
        print(json.dumps(TEMPLATE, indent=2))
        return 0

    raw = sys.stdin.read() if args.candidate == "-" else open(args.candidate, encoding="utf-8").read()
    report = evaluate(json.loads(raw))
    if args.json:
        print(json.dumps({
            "go": report["go"],
            "role_type": report["role_type"],
            "axes": [{"name": a.name, "passed": a.passed, "required": a.required,
                      "tier": a.tier, "pattern": a.pattern, "detail": a.detail} for a in report["axes"]],
        }, indent=2))
    else:
        print(render(report))
    return 0 if report["go"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
