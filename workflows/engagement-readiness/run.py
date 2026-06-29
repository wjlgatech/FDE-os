#!/usr/bin/env python3
"""engagement-readiness — a dynamic workflow that composes FDE-os skills into one go/no-go gate.

The first composition tool in the toolkit: skills are building blocks; a workflow chains them. This
one answers the FDE's real shipping question — *should we build/ship this engagement?* — by running
two existing skill cores and AND-ing their gates:

  1. invisible-workflow-mapper → will it get ADOPTED? (does it fit how decisions get made)
  2. rag-eval-harness          → does it WORK? (retrieval/grounding metrics over a real eval set)

Ship only if BOTH pass. A great answer that doesn't fit the workflow never gets adopted; a
well-adopted answer that doesn't work is worse. The combined verdict is honest: if a stage is
missing, it cannot say GO (you haven't measured it).

Deterministic, offline — it just orchestrates the skills' deterministic cores (lazy-imported by
repo-relative path, the same pattern fde-mcp-server uses). No new scoring logic lives here.

Usage:
  python3 run.py examples/engagement.json
  python3 run.py engagement.json --wf-threshold 0.6 --json
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
from types import ModuleType

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def _load(rel_script: str, mod_name: str) -> ModuleType:
    path = os.path.join(_ROOT, rel_script)
    spec = importlib.util.spec_from_file_location(mod_name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def run_engagement(bundle: dict, wf_threshold: float = 0.6) -> dict:
    """Run the two stages and combine their gates. Returns a structured report."""
    wm = _load("skills/invisible-workflow-mapper/scripts/workflow_map.py", "workflow_map")
    rev = _load("skills/rag-eval-harness/scripts/rag_eval.py", "rag_eval")

    # --- stage 1: adoption fit ------------------------------------------------
    wf = bundle.get("workflow") or {}
    wf_report = wf_pass = None
    if wf.get("signals"):
        wf_report = wm.build_map(wf, threshold=wf_threshold)
        wf_pass = wf_report["gate"]["passed"]

    # --- stage 2: does it work ------------------------------------------------
    ev = bundle.get("eval") or {}
    ev_report = ev_pass = None
    ev_reasons: list = []
    if ev.get("eval_set"):
        ev_report = rev.evaluate(ev["eval_set"], k=int(ev.get("k", 5)))
        thresholds = ev.get("thresholds")
        if thresholds:
            ev_pass, ev_reasons = rev.gate(ev_report["metrics"], {k: float(v) for k, v in thresholds.items()})

    # --- combined gate: GO iff both stages were assessed AND both passed ------
    stages_present = [s for s, r in (("adoption", wf_report), ("eval", ev_report)) if r is not None]
    reasons = []
    if wf_report is None:
        reasons.append("adoption fit not assessed (no workflow signals) — can't GO without it")
    elif not wf_pass:
        reasons.append("adoption fit BLOCKED: " + "; ".join(wf_report["gate"]["reasons"]))
    if ev_report is None:
        reasons.append("eval not assessed (no eval_set) — can't GO without it")
    elif ev_pass is None:
        reasons.append("eval ran but no thresholds given — can't GO without a pass/fail bar")
    elif not ev_pass:
        reasons.append("eval BLOCKED: " + "; ".join(ev_reasons))
    go = (wf_pass is True) and (ev_pass is True)

    return {
        "go": go,
        "verdict": "GO" if go else "NO-GO",
        "stages_assessed": stages_present,
        "adoption": wf_report,
        "adoption_pass": wf_pass,
        "eval": ev_report,
        "eval_pass": ev_pass,
        "eval_reasons": ev_reasons,
        "reasons": reasons,
    }


def render_md(report: dict) -> str:
    L = ["# Engagement Readiness", "",
         f"## Verdict: {'✅ GO' if report['go'] else '⛔ NO-GO'}", ""]
    if report["reasons"]:
        for r in report["reasons"]:
            L.append(f"- {r}")
        L.append("")
    L.append("## Stage 1 — will it get adopted? (invisible-workflow-mapper)")
    a = report["adoption"]
    if a is None:
        L.append("_not assessed — no workflow signals provided._")
    else:
        L.append(f"adoption-readiness **{a['adoption_readiness']:.2f}** · "
                 + ("✅ pass" if report["adoption_pass"] else "⛔ block"))
        if a["archetypes"]:
            L.append(f"likely archetype: **{a['archetypes'][0]['name']}**")
    L += ["", "## Stage 2 — does it work? (rag-eval-harness)"]
    e = report["eval"]
    if e is None:
        L.append("_not assessed — no eval set provided._")
    else:
        verdict = "✅ pass" if report["eval_pass"] else ("⛔ block" if report["eval_pass"] is False else "◐ no bar set")
        L.append(f"{e['n']} items · " + verdict)
        for name, val in e.get("metrics", {}).items():
            L.append(f"- {name}: {'n/a' if val is None else val}")
    L += ["", "_Ship only when both stages pass: a great answer that doesn't fit the decision "
          "workflow never gets adopted; a well-adopted answer that doesn't work is worse._"]
    return "\n".join(L).rstrip() + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Compose adoption-fit + eval into one engagement go/no-go.")
    ap.add_argument("bundle", help="path to an engagement bundle JSON ({workflow:{...}, eval:{...}})")
    ap.add_argument("--wf-threshold", type=float, default=0.6, help="adoption-readiness gate threshold")
    ap.add_argument("--json", action="store_true", help="emit the raw report JSON")
    args = ap.parse_args(argv)
    with open(args.bundle, encoding="utf-8") as fh:
        bundle = json.load(fh)
    report = run_engagement(bundle, wf_threshold=args.wf_threshold)
    print(json.dumps(report, indent=2) if args.json else render_md(report))
    return 0 if report["go"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
