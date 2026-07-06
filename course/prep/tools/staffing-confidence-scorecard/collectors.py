#!/usr/bin/env python3
"""collectors — the COLLECT stage of the staffing loop, as a pluggable seam.

match_engine.py needs two inputs: SUPPLY (people: skills, availability, and their
vetting evidence) and DEMAND (teams: milestones, open roles). This module builds both
from *sources*, behind one small interface — so the demo runs on CSV today and the same
match/recommend code runs on live enterprise data tomorrow, with no change downstream.

  working now  : CsvDemandCollector, CsvSupplyCollector   (Microsoft Forms / a roster export)
  v2 (stubs)   : MySchedulingCollector, WorkdayCollector   (documented contract; raise until wired)

Honesty posture (same as the gate): prefer OBSERVED evidence over CLAIMED. A person's real
MyScheduling bookings beat a self-reported "available"; a client-team reference beats a
resume skill list. The stubs below say exactly which observed field they'd read.

stdlib-only, offline. Emits JSON that pipes straight into match_engine.py.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys


def _split(cell: str) -> list[str]:
    return [s.strip() for s in str(cell or "").replace(";", ",").split(",") if s.strip()]


def _yes(v) -> bool:
    return str(v).strip().lower() in ("yes", "true", "y", "1", "available")


# ---------------- the seam ----------------

class Collector:
    """One source, one body. `collect()` returns a plain dict (SUPPLY or DEMAND shape)."""
    def collect(self) -> dict:  # pragma: no cover - interface
        raise NotImplementedError


class CsvDemandCollector(Collector):
    """DEMAND from a CSV: columns team, milestone, role_id, role_type, skills, count."""
    def __init__(self, path: str) -> None:
        self.path = path

    def collect(self) -> dict:
        teams: dict[str, dict] = {}
        with open(self.path, newline="", encoding="utf-8-sig") as f:
            for row in csv.DictReader(f):
                t = teams.setdefault(row["team"], {"team": row["team"], "milestone": row.get("milestone", ""), "open_roles": []})
                t["open_roles"].append({
                    "id": row["role_id"],
                    "role_type": (row.get("role_type") or "technical").strip(),
                    "skills": _split(row.get("skills")),
                    "count": int(row.get("count") or 1),
                })
        return {"teams": list(teams.values())}


class CsvSupplyCollector(Collector):
    """SUPPLY from a roster CSV (id, skills, available) merged with per-person vetting
    records (candidates_dir/<id>.json — the scorecard evidence from scorecard.py /
    forms_to_candidate.py). A person with no vetting record collects empty evidence, so
    the gate honestly marks them un-vetted rather than silently passing them."""
    def __init__(self, roster_csv: str, candidates_dir: str | None = None) -> None:
        self.roster_csv = roster_csv
        self.candidates_dir = candidates_dir

    def _evidence(self, pid: str) -> dict:
        if not self.candidates_dir:
            return {}
        path = os.path.join(self.candidates_dir, pid + ".json")
        if not os.path.exists(path):
            return {}
        with open(path, encoding="utf-8") as f:
            rec = json.load(f)
        return {k: rec.get(k, {}) for k in ("reliability", "technical_competence", "resourcefulness")}

    def collect(self) -> dict:
        people = []
        with open(self.roster_csv, newline="", encoding="utf-8-sig") as f:
            for row in csv.DictReader(f):
                pid = row["id"].strip()
                person = {"id": pid, "skills": _split(row.get("skills")), "available": _yes(row.get("available"))}
                person.update(self._evidence(pid))
                people.append(person)
        return {"people": people}


# ---------------- v2 enterprise connectors (documented stubs) ----------------

class MySchedulingCollector(Collector):
    """v2 — SUPPLY availability from Accenture MyScheduling (myscheduling.accenture.com).

    Contract (when wired): read per-person current assignment, roll-off date, and
    chargeability to derive `available` and a free-from date. Prefer the OBSERVED booking
    (actual scheduled hours) over any self-reported status. Needs SSO + the scheduling API
    scope; no scraping. Until then this raises so nothing fakes a data source.
    """
    def collect(self) -> dict:
        raise NotImplementedError("MySchedulingCollector is v2 — wire SSO + scheduling API, read observed bookings/roll-off.")


class WorkdayCollector(Collector):
    """v2 — SUPPLY skills + references from Workday.

    Contract (when wired): read the talent profile's validated skills and any stored
    delivery references (Workday is where references already live). Map a client-team
    reference to a `vouch`; never a self-asserted skill to a pass. Needs the Workday HCM
    API scope. Until then this raises.
    """
    def collect(self) -> dict:
        raise NotImplementedError("WorkdayCollector is v2 — wire Workday HCM API, map validated references to vouches.")


# ---------------- CLI ----------------

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Collect SUPPLY / DEMAND for the staffing brain.")
    sub = ap.add_subparsers(dest="cmd", required=True)
    d = sub.add_parser("demand", help="build demand.json from a CSV")
    d.add_argument("--csv", required=True)
    s = sub.add_parser("supply", help="build supply.json from a roster CSV (+ optional vetting records)")
    s.add_argument("--roster", required=True)
    s.add_argument("--candidates", help="dir of <id>.json vetting records")
    args = ap.parse_args(argv)

    if args.cmd == "demand":
        out = CsvDemandCollector(args.csv).collect()
    else:
        out = CsvSupplyCollector(args.roster, args.candidates).collect()
    json.dump(out, sys.stdout, indent=2)
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
