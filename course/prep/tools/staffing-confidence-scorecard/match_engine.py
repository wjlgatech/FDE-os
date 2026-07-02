#!/usr/bin/env python3
"""match_engine — the staffing brain: connect demand ↔ supply, eval-gate the match,
and recommend the next best step for each person AND each team.

The scorecard (scorecard.py) is the *eval function* inside a larger loop:

    COLLECT supply (people: skills, availability, reliability/technical/resourcefulness evidence)
          + demand (teams: milestones, open roles with role_type + needed skills)
      ─▶ MATCH   for each open role, keep only people who PASS the gate for that role_type
                 AND share a skill; rank by fit
      ─▶ RECOMMEND
                 person → their single next best step (confirm a match / close a gap / upskill)
                 team   → their next best step to hit the milestone (staff whom / where they're short)
      ─▶ human-in-the-loop confirms (nothing here auto-staffs; it advises)

Deterministic, stdlib-only, offline. The gate is imported, not re-implemented, so the
match can never disagree with the vetting decision.
"""
from __future__ import annotations

import argparse
import json
import sys

import scorecard as sc


# ---------- helpers ----------

def _skills(x):
    return {s.strip().lower() for s in (x or []) if str(s).strip()}


def _overlap(a, b):
    return len(_skills(a) & _skills(b))


def _person_as_candidate(person, role_type):
    """A person carries evidence blocks but no fixed role — the demand's role_type drives the gate."""
    return {
        "candidate": person.get("id", "anon"),
        "role_type": role_type,
        "reliability": person.get("reliability", {}),
        "technical_competence": person.get("technical_competence", {}),
        "resourcefulness": person.get("resourcefulness", {}),
    }


def _rank_key(m):
    # best fit first: more shared skills, then a passed pattern (repeat vouches), then tech headroom
    tech = next((a for a in m["_axes"] if a.name == "technical_competence"), None)
    rel = next((a for a in m["_axes"] if a.name == "reliability"), None)
    return (m["overlap"], 1 if (rel and rel.pattern) else 0, tech.tier if tech else "")


# ---------- core ----------

def match(supply, demand):
    """For every open role, return eligible (GO + skill-matched) people ranked by fit,
    plus the conditional pool (skill-matched but gate-blocked, with their blockers)."""
    people = supply.get("people", [])
    board = []
    for team in demand.get("teams", []):
        for role in team.get("open_roles", []):
            rt = role.get("role_type", "technical")
            eligible, conditional = [], []
            for p in people:
                if not p.get("available", True):
                    continue
                ov = _overlap(p.get("skills"), role.get("skills"))
                if ov == 0:
                    continue
                rep = sc.evaluate(_person_as_candidate(p, rt))
                entry = {"id": p.get("id"), "overlap": ov, "go": rep["go"], "_axes": rep["axes"]}
                if rep["go"]:
                    eligible.append(entry)
                else:
                    entry["blockers"] = [b.name for b in rep["blockers"]]
                    conditional.append(entry)
            eligible.sort(key=_rank_key, reverse=True)
            board.append({
                "team": team.get("team"), "milestone": team.get("milestone"),
                "role_id": role.get("id"), "role_type": rt, "count": role.get("count", 1),
                "skills": role.get("skills", []),
                "eligible": eligible, "conditional": conditional, "assigned": [],
            })
    assign(board)
    return board


def assign(board):
    """Greedy global assignment: each person fills at most ONE role, each role up to its
    count, best-fit first. Prevents double-booking one person across roles (which would
    make coverage look better than it is). Returns the set of assigned person ids."""
    pairs = []  # (overlap, board_index, person_id) — higher overlap wins
    for bi, b in enumerate(board):
        for e in b["eligible"]:
            pairs.append((e["overlap"], bi, e["id"]))
    pairs.sort(key=lambda x: -x[0])
    taken = set()
    for _ov, bi, pid in pairs:
        b = board[bi]
        if pid in taken or len(b["assigned"]) >= b["count"]:
            continue
        b["assigned"].append(pid)
        taken.add(pid)
    return taken


def person_next_steps(supply, demand, board):
    steps = []
    for p in supply.get("people", []):
        pid = p.get("id")
        assigned_to = next((b for b in board if pid in b["assigned"]), None)
        as_eligible = [b for b in board if any(e["id"] == pid for e in b["eligible"])]
        as_cond = [b for b in board if any(c["id"] == pid for c in b["conditional"])]
        if not p.get("available", True):
            status, step = "UNAVAILABLE", "On another engagement — free them up or plan around it before this milestone needs them."
        elif assigned_to:
            status = "ASSIGN"
            step = f"Confirm staffing to “{assigned_to['role_id']}” on {assigned_to['team']} — clears the gate and fits the milestone."
        elif as_eligible:
            status = "BACKUP"
            roles = ", ".join(f"“{b['role_id']}”" for b in as_eligible)
            step = f"Backup-eligible for {roles} (a stronger fit was assigned). Hold as cover, or take the next incoming demand."
        elif as_cond:
            gaps = sorted({g for b in as_cond for g in next(c["blockers"] for c in b["conditional"] if c["id"] == pid)})
            fix = "; ".join("close " + g.replace("_", " ") for g in gaps)
            step = f"One step from staffable for {len(as_cond)} matched role(s): {fix}."
            status = "CONDITIONAL"
        else:
            needed = sorted({s.lower() for t in demand.get("teams", []) for r in t.get("open_roles", []) for s in r.get("skills", [])})
            miss = [s for s in needed if s not in _skills(p.get("skills"))][:3]
            step = ("No open role matches your skills yet. Nearest demand wants: " + ", ".join(miss) + ".") if miss else "No open demand matches right now."
            status = "UNMATCHED"
        steps.append({"id": pid, "status": status, "next_best_step": step})
    return steps


def team_next_steps(board):
    # group roles back under teams
    teams = {}
    for b in board:
        teams.setdefault(b["team"], {"milestone": b["milestone"], "roles": []})["roles"].append(b)
    out = []
    for team, info in teams.items():
        role_lines = []
        milestone_at_risk = False
        for b in info["roles"]:
            need = b["count"]
            got = b["assigned"]
            if len(got) >= need:
                role_lines.append(f"“{b['role_id']}”: staff {', '.join(got)} → covered ({len(got)}/{need}).")
            else:
                milestone_at_risk = True
                gap = need - len(got)
                staffed = ", ".join(got) or "nobody yet"
                if b["conditional"]:
                    cond = "; ".join(f"{c['id']} (if they " + " & ".join("fix " + x.replace("_", " ") for x in c["blockers"]) + ")" for c in b["conditional"][:3])
                    role_lines.append(f"“{b['role_id']}”: short {gap} (have {staffed}). Fastest close: {cond}.")
                else:
                    role_lines.append(f"“{b['role_id']}”: short {gap} (have {staffed}). No one in the pool matches — source externally or rescope the milestone.")
        out.append({
            "team": team, "milestone": info["milestone"],
            "milestone_at_risk": milestone_at_risk,
            "next_best_step": " ".join(role_lines),
        })
    return out


def plan(supply, demand):
    board = match(supply, demand)
    return {"board": board,
            "person_next_steps": person_next_steps(supply, demand, board),
            "team_next_steps": team_next_steps(board)}


def render(p):
    L = ["STAFFING BRAIN — demand ↔ supply plan", "=" * 38, ""]
    L.append("OPEN ROLES")
    for b in p["board"]:
        flag = "✅" if len(b["assigned"]) >= b["count"] else "⛔"
        L.append(f"  {flag} {b['team']} · {b['role_id']} ({b['role_type']}, need {b['count']}) — assigned {len(b['assigned'])}/{b['count']}")
        for e in b["eligible"]:
            tag = "▶ assign" if e["id"] in b["assigned"] else "· backup"
            L.append(f"       {tag} {e['id']}  (skill overlap {e['overlap']})")
        for c in b["conditional"]:
            L.append(f"       ~ {c['id']}  blocked on: {', '.join(c['blockers'])}")
    L.append("")
    L.append("EACH PERSON → NEXT BEST STEP")
    for s in p["person_next_steps"]:
        L.append(f"  [{s['status']}] {s['id']}: {s['next_best_step']}")
    L.append("")
    L.append("EACH TEAM → NEXT BEST STEP (to hit milestone)")
    for t in p["team_next_steps"]:
        flag = "⚠️ at risk" if t["milestone_at_risk"] else "on track"
        L.append(f"  {t['team']} — {t['milestone']} [{flag}]")
        L.append(f"       {t['next_best_step']}")
    return "\n".join(L)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Match demand↔supply and recommend next best steps.")
    sub = ap.add_subparsers(dest="cmd", required=True)
    pl = sub.add_parser("plan", help="produce the staffing plan from supply.json + demand.json")
    pl.add_argument("--supply", required=True)
    pl.add_argument("--demand", required=True)
    pl.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    supply = json.load(open(args.supply, encoding="utf-8"))
    demand = json.load(open(args.demand, encoding="utf-8"))
    result = plan(supply, demand)
    if args.json:
        # strip the internal axis objects for a clean machine payload
        for b in result["board"]:
            for e in b["eligible"] + b["conditional"]:
                e.pop("_axes", None)
        print(json.dumps(result, indent=2))
    else:
        print(render(result))
    # exit non-zero if any milestone is at risk → CI/alerting can gate on it
    at_risk = any(t["milestone_at_risk"] for t in result["team_next_steps"])
    return 1 if at_risk else 0


if __name__ == "__main__":
    raise SystemExit(main())
