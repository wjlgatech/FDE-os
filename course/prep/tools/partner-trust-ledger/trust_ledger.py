#!/usr/bin/env python3
"""partner-trust-ledger — the anti-resume, as a gate.

A hiring partner does not stake their reputation on a resume. They stake it on
*evidence*: what you shipped that they can see, and a real person who worked with
you who will vouch. This tool makes that decision mechanical.

Four dimensions a partner actually evaluates (each an FDE trust axis):
  - technical_competence   deep, hands-on build ability (Python + agent building)
  - reliability            you show up and do what you said you would
  - learning_agility       you can learn a new tool in a day and teach it back
  - validated_reputation   a named human who worked with you attests to the above

Every claim carries an EVIDENCE TIER, not a rating you gave yourself:
  vouch    (3)  a named person who worked with you attests (the gold tier)
  artifact (2)  a verifiable shipped thing — public repo, live app, live demo
  claimed  (1)  self-report / resume only
  none     (0)  asserted with nothing behind it

A dimension's tier = the strongest evidence present for it. (One "without you we
don't run" outweighs ten claims — but two independent vouches flag a *pattern*,
because one great outcome can be an accident and a pattern cannot.)

The gate (hard, AND-style — a strong total does not rescue one weak axis):
  1. NO dimension may rest on `claimed`/`none` alone  → every axis must reach `artifact`.
  2. `validated_reputation` must carry at least one `vouch` — an artifact is not a person.
  GO only if 1 AND 2. "No evidence ⇒ No."

Deterministic, stdlib-only, offline. Same posture as true-scorer / criteria-scorer.
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field

TIERS = {"none": 0, "claimed": 1, "artifact": 2, "vouch": 3}
TIER_NAME = {v: k for k, v in TIERS.items()}

DIMENSIONS = (
    "technical_competence",
    "reliability",
    "learning_agility",
    "validated_reputation",
)

# The two floors the gate enforces.
FLOOR_ALL = TIERS["artifact"]          # every axis must clear `artifact`
FLOOR_REPUTATION = TIERS["vouch"]      # reputation must clear `vouch`


@dataclass
class DimResult:
    name: str
    tier: int
    n_claims: int
    n_vouch: int
    pattern: bool = field(init=False)

    def __post_init__(self) -> None:
        # Two+ independent vouches = a pattern, not an accident.
        self.pattern = self.n_vouch >= 2


def _tier_of(claim: dict) -> int:
    ev = str(claim.get("evidence", "none")).strip().lower()
    if ev not in TIERS:
        raise ValueError(
            f"unknown evidence tier {ev!r}; expected one of {sorted(TIERS)}"
        )
    return TIERS[ev]


def score_dimension(name: str, claims: list[dict]) -> DimResult:
    tiers = [_tier_of(c) for c in claims]
    top = max(tiers) if tiers else 0
    n_vouch = sum(1 for t in tiers if t == TIERS["vouch"])
    return DimResult(name=name, tier=top, n_claims=len(claims), n_vouch=n_vouch)


def evaluate(ledger: dict) -> dict:
    dims = ledger.get("dimensions", {})
    unknown = set(dims) - set(DIMENSIONS)
    if unknown:
        raise ValueError(f"unknown dimension(s): {sorted(unknown)}; expected {list(DIMENSIONS)}")

    results = {d: score_dimension(d, dims.get(d, [])) for d in DIMENSIONS}

    blockers: list[str] = []
    for d in DIMENSIONS:
        if results[d].tier < FLOOR_ALL:
            blockers.append(
                f"{d}: strongest evidence is `{TIER_NAME[results[d].tier]}` — "
                f"needs at least `artifact` (something a partner can see, not a claim)"
            )
    rep = results["validated_reputation"]
    if rep.tier < FLOOR_REPUTATION:
        blockers.append(
            "validated_reputation: no `vouch` — needs a named person who worked "
            "with you to attest. An artifact is not a reference."
        )

    return {"results": results, "blockers": blockers, "go": not blockers}


def render(report: dict) -> str:
    lines = ["partner-trust ledger", "=" * 20, ""]
    for d in DIMENSIONS:
        r = report["results"][d]
        pat = "  ⟳ pattern (≥2 vouches)" if r.pattern else ""
        lines.append(
            f"  {d:<22} {TIER_NAME[r.tier]:<8} "
            f"({r.n_claims} claim{'s' if r.n_claims != 1 else ''}){pat}"
        )
    lines.append("")
    if report["go"]:
        lines.append("VERDICT: ✅ GO — evidence clears every axis; a partner can stake on this.")
    else:
        lines.append("VERDICT: ⛔ NO-GO — close these before asking anyone to vouch:")
        for b in report["blockers"]:
            lines.append(f"  • {b}")
    return "\n".join(lines)


TEMPLATE = {
    "candidate": "self",
    "dimensions": {
        "technical_competence": [
            {"claim": "e.g. shipped a multi-skill agentic toolkit", "evidence": "artifact", "ref": "https://..."}
        ],
        "reliability": [
            {"claim": "e.g. delivered every milestone on the date I committed", "evidence": "claimed"}
        ],
        "learning_agility": [
            {"claim": "e.g. learned <tool> in a day and taught it back", "evidence": "artifact", "ref": "demo link"}
        ],
        "validated_reputation": [
            {"claim": "e.g. <name/role> will attest; 'without them we don't run'", "evidence": "vouch", "ref": "contact"}
        ],
    },
}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Score a candidate's trust ledger and apply the partner gate.")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_score = sub.add_parser("score", help="score a ledger.json (use - for stdin)")
    p_score.add_argument("ledger", help="path to ledger.json, or - for stdin")
    p_score.add_argument("--json", action="store_true", help="emit machine-readable JSON")

    sub.add_parser("template", help="print a blank ledger to fill in")

    args = ap.parse_args(argv)

    if args.cmd == "template":
        print(json.dumps(TEMPLATE, indent=2))
        return 0

    raw = sys.stdin.read() if args.ledger == "-" else open(args.ledger, encoding="utf-8").read()
    ledger = json.loads(raw)
    report = evaluate(ledger)

    if args.json:
        out = {
            "go": report["go"],
            "blockers": report["blockers"],
            "dimensions": {
                d: {"tier": TIER_NAME[r.tier], "n_claims": r.n_claims, "pattern": r.pattern}
                for d, r in report["results"].items()
            },
        }
        print(json.dumps(out, indent=2))
    else:
        print(render(report))

    return 0 if report["go"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
