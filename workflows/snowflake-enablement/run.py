#!/usr/bin/env python3
"""snowflake-enablement — compose snowflake-os engines into one staffing verdict.

The question a delivery lead actually has: *can I put this person on the Snowflake
engagement next month, and if not, what is the shortest way to yes?*

Three stages, AND-ed:

  1. readiness  → is the person competent NOW, on verified evidence?      (gate)
  2. gate       → is the knowledge base we judged them against sound?     (gate)
  3. pathfinder → if not ready, the shortest costed path to ready.        (plan)

Stage 2 is the one people forget. A readiness verdict computed from a stale or
internally inconsistent catalogue is worse than no verdict, because it looks
official. So the workflow refuses to say STAFF on a knowledge base that fails
its own integrity gate — an unmeasured foundation cannot certify anyone.

Deterministic and offline: it orchestrates the engines' pure cores, adds no
scoring logic of its own, and lazy-imports by repo-relative path (the same
pattern engagement-readiness and fde-mcp-server use).

Usage:
  python3 workflows/snowflake-enablement/run.py examples/candidate.json
  python3 workflows/snowflake-enablement/run.py <bundle.json> --threshold 0.6 --json
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
from types import ModuleType

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
_SCRIPTS = os.path.join(_ROOT, "snowflake-os", "scripts")


def _load(rel_script: str, mod_name: str) -> ModuleType:
    """Lazy-import an engine script by repo-relative path."""
    if _SCRIPTS not in sys.path:
        sys.path.insert(0, _SCRIPTS)
    path = os.path.join(_ROOT, rel_script)
    spec = importlib.util.spec_from_file_location(mod_name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class _PlanArgs:
    """The pathfinder's argparse surface, as a plain object."""

    def __init__(self, role: str, have: str, free_only: bool, max_hours):
        self.role, self.exam, self.competency = role, None, None
        self.have, self.free_only, self.max_hours = have, free_only, max_hours
        self.core_only = False
        self.json = True


def run_enablement(bundle: dict, threshold: float = 0.6) -> dict:
    catalog_mod = _load("snowflake-os/scripts/catalog.py", "sfos_catalog")
    readiness = _load("snowflake-os/scripts/readiness.py", "sfos_readiness")
    pathfinder = _load("snowflake-os/scripts/pathfinder.py", "sfos_pathfinder")
    gate_mod = _load("snowflake-os/scripts/gate.py", "sfos_gate")

    cat = catalog_mod.Catalog()

    # --- stage 1: is the knowledge base itself sound? -----------------------
    kb = gate_mod.Gate().run()
    kb_pass = kb["verdict"] == "PASS"

    # --- stage 2: is the person ready, on verified evidence? ----------------
    scored = readiness.score(cat, bundle, threshold)
    ready = scored["verdict"] == "GO"

    # --- stage 3: if not, the shortest path to ready ------------------------
    plan = None
    if not ready:
        verified = [
            c["course"]
            for c in bundle.get("completions", [])
            if readiness.evidence_class(c)[0] == "verified"
        ]
        constraints = bundle.get("constraints", {})
        plan = pathfinder.build_plan(
            cat,
            _PlanArgs(
                role=bundle.get("role"),
                have=",".join(verified),
                free_only=bool(constraints.get("free_only")),
                max_hours=constraints.get("max_hours"),
            ),
        )

    verdict = "STAFF" if (kb_pass and ready) else "NOT-YET"
    return {
        "candidate": scored["candidate"],
        "role": scored["role"],
        "verdict": verdict,
        "kb_integrity": {"verdict": kb["verdict"], "passed": kb["passed"], "total": kb["total"],
                         "failed_checks": [c["check"] for c in kb["checks"] if not c["ok"]]},
        "readiness": scored,
        "remediation_plan": plan,
        "why": (
            "knowledge base sound and every core competency verified"
            if verdict == "STAFF"
            else "knowledge base failed its own integrity gate — no verdict can be trusted on it"
            if not kb_pass
            else "core competencies not covered by verified evidence"
        ),
    }


def render_md(r: dict) -> str:
    L = [f"# Snowflake enablement · {r['candidate']} → {r['role']}", ""]
    kb = r["kb_integrity"]
    L.append(f"**Stage 1 · knowledge-base integrity** — {kb['verdict']} ({kb['passed']}/{kb['total']})")
    if kb["failed_checks"]:
        L.append(f"  failed: {', '.join(kb['failed_checks'])}")
    rd = r["readiness"]
    L.append("")
    L.append(f"**Stage 2 · readiness** — {rd['verdict']} · core covered {rd['core_covered']}")
    e = rd["evidence_summary"]
    L.append(f"  evidence: {e['verified']} verified · "
             f"{e['self_reported_discounted']} self-reported and {e['planned_discounted']} planned, "
             f"both scored 0")
    if rd["blocking_gaps"]:
        L.append(f"  blocking gaps: {', '.join(rd['blocking_gaps'])}")

    if r["remediation_plan"]:
        p = r["remediation_plan"]
        t = p["totals"]
        L += ["", f"**Stage 3 · shortest path to ready** — {t['courses']} courses · {t['hours']:g}h "
                  f"({t['free_courses']} free / {t['paid_courses']} paid)"]
        for s in p["steps"]:
            if s["courses"]:
                L.append(f"  - {s['name']} ({s['hours']:g}h): "
                         f"{', '.join(c['code'] for c in s['courses'])}")
    L += ["", f"## VERDICT: {r['verdict']}", f"_{r['why']}._", "",
          "_A NOT-YET is the workflow working. It ships the remediation plan with the refusal, "
          "so the answer is never just 'no'._"]
    return "\n".join(L) + "\n"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Compose KB integrity + readiness + remediation into a staffing verdict.")
    ap.add_argument("bundle", help="path to a candidate bundle JSON (role + completions [+ constraints])")
    ap.add_argument("--threshold", type=float, default=0.6, help="per-competency coverage threshold")
    ap.add_argument("--json", action="store_true", help="emit the raw report JSON")
    args = ap.parse_args(argv)

    with open(args.bundle, encoding="utf-8") as fh:
        bundle = json.load(fh)
    report = run_enablement(bundle, threshold=args.threshold)
    print(json.dumps(report, indent=2, ensure_ascii=False) if args.json else render_md(report))
    return 0 if report["verdict"] == "STAFF" else 2


if __name__ == "__main__":
    raise SystemExit(main())
