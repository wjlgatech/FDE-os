#!/usr/bin/env python3
"""invisible-workflow-mapper — reconstruct an organization's *decision workflow* from partial,
indirect signals, score adoption-readiness, infer the likely workflow archetype + its known
adoption traps, and emit the oblique probes to surface what the client can't yet articulate.

The thesis (from a reader of the Delta long-form): *the biggest deployment failures aren't model
failures — they're workflow failures.* A great answer that doesn't fit how decisions actually get
made never gets adopted. Clients can rarely describe their own decision workflow, so an FDE has to
reconstruct it — ideally **before** they spell it out. This tool turns that reconstruction into a
deterministic, offline gate (the true-scorer / criteria-scorer pattern): signals in → a structured
Invisible Workflow Map + an adoption-readiness score + the next probes, out.

It DEEPENS the `delta-discovery-protocol` field kit (whose Pass 2 maps the workflow and Pass 4 the
political terrain) into the specific axis that decides adoption: *how a yes actually happens.*

Deterministic core, no network. Subjective interpretation (e.g. reading a transcript into signals)
is an opt-in LLM step the FDE/agent does first — not part of this core.

Usage:
  python3 workflow_map.py map signals.json
  python3 workflow_map.py map signals.json --threshold 0.6 --json
"""
from __future__ import annotations

import argparse
import json
import re
import sys

# ---------------------------------------------------------------- the anatomy of a decision workflow
# Each dimension: human label, why it matters, weight, and whether it is load-bearing for adoption.
# You cannot predict adoption without the four load-bearing dimensions.
DIMENSIONS = {
    "trigger":        {"label": "Trigger",         "weight": 1, "load_bearing": False,
                       "why": "the event that starts the decision — the moment the AI output must arrive in"},
    "decider":        {"label": "Decider",         "weight": 2, "load_bearing": True,
                       "why": "who actually says yes (not who is in the room)"},
    "approval_chain": {"label": "Approval chain",  "weight": 2, "load_bearing": True,
                       "why": "the real sign-off path and the quiet vetoes that can kill it"},
    "evidence_ritual":{"label": "Evidence ritual", "weight": 2, "load_bearing": True,
                       "why": "the artifact / format / forum a decision is actually made on"},
    "cadence":        {"label": "Cadence",         "weight": 1, "load_bearing": False,
                       "why": "the rhythm decisions happen on (standing review vs ad-hoc fire)"},
    "incumbent":      {"label": "Incumbent process","weight": 1, "load_bearing": False,
                       "why": "how it is done today — what the AI must augment or replace"},
    "adoption_owner": {"label": "Adoption owner",  "weight": 2, "load_bearing": True,
                       "why": "whose daily behavior must change for the AI to actually get used"},
    "kill_points":    {"label": "Kill points",     "weight": 1, "load_bearing": False,
                       "why": "where a good answer dies — compliance, trust, format, politics"},
}

# Oblique probes — surface a dimension WITHOUT asking "what's your workflow?" (people can't answer that).
PROBES = {
    "trigger":        ["Walk me through the last time this decision actually got made — what kicked it off?",
                       "Is this a scheduled thing, or does it only come up when something breaks?"],
    "decider":        ["If this stalled, whose single email would unstick it?",
                       "Who signed off on the last three things like this?"],
    "approval_chain": ["Who else has to nod before it's real — even informally?",
                       "Who has quietly killed a project like this before?"],
    "evidence_ritual":["Can you show me the actual artifact the last decision was made on?",
                       "Where does this get decided — a meeting, a doc, a dashboard, a Slack thread?"],
    "cadence":        ["When does this normally come up — a standing meeting, or only on a fire?",
                       "What's the slowest step between 'we should' and 'it's done'?"],
    "incumbent":      ["Walk me through how this gets done today, including the annoying manual parts.",
                       "What do people do outside the official system — the spreadsheet, the 'we just text Maria'?"],
    "adoption_owner": ["Whose day has to change for this to get used? What are they rewarded for today?",
                       "Who loses something — status, headcount, control — if this works?"],
    "kill_points":    ["What's the most likely reason a genuinely good solution here never gets used?",
                       "What would legal / security / compliance need before they'd let this touch real data?"],
}

# Decision-workflow archetypes — the "before they tell you" inference. Each carries the TELLS that
# hint at it (matched against observations + context) and the canonical ADOPTION TRAPS it brings.
ARCHETYPES = [
    {"name": "single-strong-owner",
     "tells": ["founder", "ceo", "vp", "owner", "her call", "his call", "just decides", "gut", "boss"],
     "traps": ["Bus-factor: win the owner or nothing ships — a perfect answer they didn't ask for stalls.",
               "The AI must make the OWNER faster, not bypass or second-guess them."]},
    {"name": "consensus-committee",
     "tells": ["committee", "steering", "stakeholders", "alignment", "consensus", "working group", "we discuss", "buy-in"],
     "traps": ["Death by meeting: one quiet veto kills it; map every seat, not just the loudest.",
               "Output must arrive pre-digested into the committee's format, or it won't be read in the room."]},
    {"name": "regulated-signoff",
     "tells": ["compliance", "audit", "legal", "regulated", "soc2", "hipaa", "validation", "risk", "governance", "policy"],
     "traps": ["Provenance is mandatory: no citations / audit trail = dead on arrival, however good the answer.",
               "Speed is irrelevant if it can't be signed off; design for the reviewer, not the operator."]},
    {"name": "shadow-bottom-up",
     "tells": ["spreadsheet", "workaround", "we just text", "shadow", "unofficial", "side channel", "excel", "manual"],
     "traps": ["The official rollout threatens whoever owns the workaround — co-opt them, don't replace them.",
               "Adoption comes from making the shadow process official, not from a top-down mandate."]},
    {"name": "procurement-gated",
     "tells": ["procurement", "purchase order", "po ", "budget", "vendor", "security review", "questionnaire", "legal review", "msa"],
     "traps": ["The technical win is necessary but not sufficient — the real gate is procurement + security review timing.",
               "Start the security questionnaire / data-handling doc on day one; it is the long pole."]},
    {"name": "metrics-ritual",
     "tells": ["weekly review", "qbr", "dashboard", "kpi", "the number", "scorecard", "standup", "report out", "metrics"],
     "traps": ["The AI must feed THE existing ritual/number/format at the right cadence; outside it, it's invisible.",
               "Don't introduce a new dashboard — land inside the one they already stare at."]},
]

_WORD = re.compile(r"[a-z0-9]+")


def _text_of(data: dict) -> str:
    """Flatten observations + context into one lowercase blob for archetype tell-matching."""
    parts = []
    for s in data.get("signals", []):
        parts.append(str(s.get("observation", "")))
    ctx = data.get("context", {}) or {}
    for k in ("org", "industry", "size", "notes"):
        if ctx.get(k):
            parts.append(str(ctx[k]))
    for t in ctx.get("tools", []) or []:
        parts.append(str(t))
    return " ".join(parts).lower()


def _status(conf: float) -> str:
    """Confidence bucket for one dimension: mapped / tentative / unknown."""
    if conf >= 0.66:
        return "known"
    if conf >= 0.33:
        return "partial"
    return "unknown"


def coverage(data: dict) -> dict:
    """Per-dimension best-known confidence + status. Unknown dimension in a signal is an error."""
    best: dict = {d: 0.0 for d in DIMENSIONS}
    for s in data.get("signals", []):
        dim = s.get("dimension")
        if dim not in DIMENSIONS:
            raise ValueError(f"unknown dimension {dim!r} (expected one of {', '.join(DIMENSIONS)})")
        conf = float(s.get("confidence", 0.5))
        best[dim] = max(best[dim], max(0.0, min(1.0, conf)))
    return {d: {"confidence": round(best[d], 3), "status": _status(best[d])} for d in DIMENSIONS}


def adoption_readiness(cov: dict) -> float:
    """Weighted average confidence over the four LOAD-BEARING dimensions (the adoption predictors)."""
    num = den = 0.0
    for d, meta in DIMENSIONS.items():
        if meta["load_bearing"]:
            w = meta["weight"]
            num += w * cov[d]["confidence"]
            den += w
    return round(num / den, 3) if den else 0.0


def completeness(cov: dict) -> float:
    """Weighted average confidence over ALL dimensions — how complete the map is overall."""
    num = sum(DIMENSIONS[d]["weight"] * cov[d]["confidence"] for d in DIMENSIONS)
    den = sum(DIMENSIONS[d]["weight"] for d in DIMENSIONS)
    return round(num / den, 3) if den else 0.0


def match_archetypes(data: dict) -> list:
    """Infer likely decision-workflow archetype(s) from tells in observations + context."""
    blob = _text_of(data)
    out = []
    for a in ARCHETYPES:
        hits = [t for t in a["tells"] if t in blob]
        if hits:
            out.append({"name": a["name"], "score": len(hits), "matched": hits, "traps": a["traps"]})
    out.sort(key=lambda x: x["score"], reverse=True)
    return out


def probes_for_gaps(cov: dict) -> dict:
    """For every unknown/partial dimension, the oblique probes to surface it next."""
    gaps = {}
    for d in DIMENSIONS:
        if cov[d]["status"] != "known":
            gaps[d] = PROBES[d]
    return gaps


def gate(cov: dict, readiness: float, threshold: float) -> tuple:
    """PASS when readiness >= threshold AND no load-bearing dimension is fully unknown."""
    reasons = []
    for d, meta in DIMENSIONS.items():
        if meta["load_bearing"] and cov[d]["status"] == "unknown":
            reasons.append(f"load-bearing dimension '{DIMENSIONS[d]['label']}' is unknown — {meta['why']}")
    if readiness < threshold:
        reasons.append(f"adoption-readiness {readiness:.2f} < threshold {threshold:.2f}")
    return (len(reasons) == 0, reasons)


def build_map(data: dict, threshold: float = 0.6) -> dict:
    """Signals -> per-dimension map + archetype match + coverage + gate verdict."""
    cov = coverage(data)
    readiness = adoption_readiness(cov)
    archetypes = match_archetypes(data)
    passed, reasons = gate(cov, readiness, threshold)
    return {
        "coverage": cov,
        "adoption_readiness": readiness,
        "map_completeness": completeness(cov),
        "archetypes": archetypes,
        "probes": probes_for_gaps(cov),
        "gate": {"passed": passed, "threshold": threshold, "reasons": reasons},
    }


def render_md(report: dict, context: dict | None = None) -> str:
    """Human-readable markdown view of a workflow map report."""
    cov = report["coverage"]
    L = ["# Invisible Workflow Map", ""]
    if context:
        bits = [context.get(k) for k in ("org", "industry", "size") if context.get(k)]
        if bits:
            L.append("**Context:** " + " · ".join(str(b) for b in bits))
            L.append("")
    L += [f"**Adoption-readiness: {report['adoption_readiness']:.2f}**  ·  map completeness "
          f"{report['map_completeness']:.2f}  ·  gate: "
          + ("✅ PASS" if report["gate"]["passed"] else "⛔ BLOCK"), ""]

    L += ["## The decision workflow", "", "| Dimension | Status | What it answers |", "|---|---|---|"]
    mark = {"known": "✅ known", "partial": "◐ partial", "unknown": "○ unknown"}
    for d, meta in DIMENSIONS.items():
        star = " **(load-bearing)**" if meta["load_bearing"] else ""
        L.append(f"| {meta['label']}{star} | {mark[cov[d]['status']]} | {meta['why']} |")
    L.append("")

    if report["archetypes"]:
        L += ["## Likely archetype (inferred before they told you)", ""]
        for a in report["archetypes"][:2]:
            L.append(f"### {a['name']}  ·  signal strength {a['score']}")
            L.append(f"_tells matched: {', '.join(a['matched'])}_")
            for trap in a["traps"]:
                L.append(f"- ⚠️ {trap}")
            L.append("")
    else:
        L += ["## Likely archetype", "", "_Not enough signal yet to infer an archetype — run the probes below._", ""]

    if report["probes"]:
        L += ["## Probe next (surface what they can't articulate)", ""]
        for d, qs in report["probes"].items():
            L.append(f"**{DIMENSIONS[d]['label']}**")
            for q in qs:
                L.append(f"- {q}")
            L.append("")

    if not report["gate"]["passed"]:
        L += ["## Why the gate blocks", ""]
        for r in report["gate"]["reasons"]:
            L.append(f"- {r}")
        L.append("")
        L.append("_Don't build the integration until the load-bearing dimensions are known — a great "
                 "answer that doesn't fit the decision workflow never gets adopted._")
    return "\n".join(L).rstrip() + "\n"


def main(argv: list[str] | None = None) -> int:
    """CLI entry point: map | probes | gate."""
    ap = argparse.ArgumentParser(description="Reconstruct an org's decision workflow from signals.")
    sub = ap.add_subparsers(dest="cmd", required=True)
    m = sub.add_parser("map", help="build the Invisible Workflow Map from a signals JSON")
    m.add_argument("signals", help="path to a signals JSON ({context, signals:[{dimension,observation,confidence}]})")
    m.add_argument("--threshold", type=float, default=0.6, help="adoption-readiness gate threshold (default 0.6)")
    m.add_argument("--json", action="store_true", help="emit the raw report JSON instead of markdown")
    args = ap.parse_args(argv)

    with open(args.signals, encoding="utf-8") as fh:
        data = json.load(fh)
    try:
        report = build_map(data, threshold=args.threshold)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(render_md(report, data.get("context")))
    return 0 if report["gate"]["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
