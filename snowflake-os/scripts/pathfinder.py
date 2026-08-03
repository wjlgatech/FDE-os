#!/usr/bin/env python3
"""snowflake-os · pathfinder — a goal becomes an ordered, costed learning plan.

Pure stdlib, offline, deterministic: the same inputs always produce the same plan.

    python3 snowflake-os/scripts/pathfinder.py plan --role forward-deployed-engineer
    python3 snowflake-os/scripts/pathfinder.py plan --role ml-engineer --free-only
    python3 snowflake-os/scripts/pathfinder.py plan --exam GES-C02 --have OD-SXGA,OD-SXGA2
    python3 snowflake-os/scripts/pathfinder.py plan --competency genai-cortex,security-access-control --max-hours 20

THE QUESTION THIS ANSWERS, which learn.snowflake.com cannot:
"given where I'm going, what is the shortest ordered path through 58 courses,
how many hours is it, and what does the catalogue NOT teach me?"

ORDERING is evidence-first, not opinion:
  1. platform-foundations always leads — everything else assumes its vocabulary.
  2. core competencies before supporting ones.
  3. inside a competency, Snowflake's OWN curated track order wins where it
     published one (Badge 1 → Badge 6); only where it published nothing do we
     fall back to easiest-and-shortest-first, and the plan says which was used.

HONESTY. Every plan reports the share of its mappings that are `curated`
(our judgment) rather than `title`/`objective` (checkable upstream), so a
reader can discount it accordingly. A plan is a recommendation, never a receipt
of competence — that is what readiness.py is for.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from catalog import Catalog, UNMEASURED  # noqa: E402

DIFFICULTY_RANK = {"Easy": 0, "Moderate": 1, "Hard": 2, "Rigorous": 3}


def track_position(cat: Catalog, code: str) -> tuple[int, int]:
    """Where Snowflake itself places a course in a curated sequence."""
    for t in cat.tracks.values():
        if code in t["sequence"]:
            return (0, t["sequence"].index(code))
    return (1, 0)  # not in any published sequence


def order_courses(cat: Catalog, courses: list[dict]) -> tuple[list[dict], str]:
    in_track = [c for c in courses if track_position(cat, c["code"])[0] == 0]
    if not courses:
        basis = "—"
    elif len(in_track) == len(courses):
        basis = "Snowflake's published track order"
    elif in_track:
        basis = (f"{len(in_track)}/{len(courses)} from Snowflake's published track order, "
                 f"remainder by difficulty then effort")
    else:
        basis = "difficulty then effort (Snowflake publishes no order for these)"
    ordered = sorted(
        courses,
        key=lambda c: (
            track_position(cat, c["code"]),
            DIFFICULTY_RANK.get(c["difficulty"], 9),
            c["effort_hours"] if c["effort_hours"] is not None else 9_999,
            c["code"],
        ),
    )
    return ordered, basis


def resolve_goal(cat: Catalog, args) -> tuple[str, list[str], list[str]]:
    """→ (goal label, core competency ids, supporting competency ids)."""
    if args.role:
        spec = cat.role_competencies(args.role)
        if not spec:
            raise SystemExit(
                f"unknown role {args.role!r}.\nknown roles: {', '.join(sorted(cat.roles))}"
            )
        return f"role:{args.role}", list(spec["core"]), list(spec.get("supporting", []))

    if args.exam:
        code = args.exam.upper()
        if code not in cat.exams:
            raise SystemExit(
                f"unknown exam {code!r}.\nknown exams: {', '.join(sorted(cat.exams))}"
            )
        core = [cid for cid, c in cat.competencies.items()
                if any(e["code"] == code for e in c["exams"])]
        if not core:
            raise SystemExit(f"no competency maps to exam {code} — add one to data/competencies.yml")
        return f"exam:{code}", core, []

    ids = [c.strip() for c in args.competency.split(",") if c.strip()]
    unknown = [c for c in ids if c not in cat.competencies]
    if unknown:
        raise SystemExit(
            f"unknown competenc{'y' if len(unknown) == 1 else 'ies'}: {', '.join(unknown)}\n"
            f"known: {', '.join(sorted(cat.competencies))}"
        )
    return f"competencies:{','.join(ids)}", ids, []


def build_plan(cat: Catalog, args) -> dict:
    goal, core, supporting = resolve_goal(cat, args)
    have = {c.strip().upper() for c in (args.have or "").split(",") if c.strip()}

    # platform-foundations always leads.
    def ordered_ids(ids: list[str]) -> list[str]:
        return sorted(ids, key=lambda i: (i != "platform-foundations", ids.index(i)))

    steps, seen, skipped_paid, curated_n, total_n = [], set(have), [], 0, 0
    for tier, ids in (("core", ordered_ids(core)), ("supporting", ordered_ids(supporting))):
        if args.core_only and tier == "supporting":
            continue
        for cid in ids:
            comp = cat.competencies[cid]
            all_mapped = cat.competency_courses(cid)
            total_n += len(all_mapped)
            curated_n += sum(1 for c in all_mapped if c["basis"] == "curated")

            # Use the SAME requirement units the readiness gate scores against,
            # so a plan can never recommend a path its own gate won't credit.
            # For an alternatives group, plan the cheapest member and record the
            # substitutes so the learner knows an ILT seat would also count.
            courses, substitutes = [], {}
            for unit in cat.requirement_units(cid):
                if unit["kind"] == "course":
                    courses.append(unit["courses"][0])
                    continue
                if already := [c for c in unit["courses"] if c["code"] in seen]:
                    courses.append(already[0])
                    continue
                affordable = [c for c in unit["courses"] if c["free"]] if args.free_only else unit["courses"]
                pick = min(affordable or unit["courses"], key=lambda c: c["effort_hours"] or 0)
                courses.append(pick)
                others = [c["code"] for c in unit["courses"] if c["code"] != pick["code"]]
                if others:
                    substitutes[pick["code"]] = others

            pool, prior, priced_out = [], [], []
            for c in courses:
                if c["code"] in seen:
                    prior.append(c["code"])
                    continue
                if args.free_only and not c["free"]:
                    skipped_paid.append(c["code"])
                    priced_out.append(c["code"])
                    continue
                pool.append(c)
            ordered, order_basis = order_courses(cat, pool)
            picked = []
            for c in ordered:
                seen.add(c["code"])
                picked.append(c)
            if picked or not pool:
                steps.append({
                    "competency": cid,
                    "name": comp["name"],
                    "tier": tier,
                    "why": comp["why"],
                    "order_basis": order_basis,
                    "substitutes": {k: v for k, v in substitutes.items()
                                    if k in {c["code"] for c in picked}},
                    "covered_earlier": prior,
                    "excluded_as_paid": priced_out,
                    "courses": picked,
                    "hours": sum(c["effort_hours"] or 0 for c in picked),
                })

    # A max-hours budget truncates from the end (supporting first), and SAYS SO.
    dropped = []
    if args.max_hours:
        running, kept = 0.0, []
        for s in steps:
            if running + s["hours"] <= args.max_hours:
                kept.append(s)
                running += s["hours"]
            else:
                trimmed = []
                for c in s["courses"]:
                    h = c["effort_hours"] or 0
                    if running + h <= args.max_hours:
                        trimmed.append(c)
                        running += h
                    else:
                        dropped.append(c["code"])
                if trimmed:
                    kept.append({**s, "courses": trimmed,
                                 "hours": sum(c["effort_hours"] or 0 for c in trimmed)})
        steps = kept

    all_courses = [c for s in steps for c in s["courses"]]
    return {
        "goal": goal,
        "constraints": {
            "free_only": bool(args.free_only),
            "core_only": bool(args.core_only),
            "max_hours": args.max_hours,
            "already_completed": sorted(have),
        },
        "steps": steps,
        "totals": {
            "courses": len(all_courses),
            "hours": round(sum(c["effort_hours"] or 0 for c in all_courses), 2),
            "free_courses": sum(1 for c in all_courses if c["free"]),
            "paid_courses": sum(1 for c in all_courses if not c["free"]),
        },
        "honesty": {
            "mappings_total": total_n,
            "mappings_curated": curated_n,
            "curated_share": round(curated_n / total_n, 2) if total_n else None,
            "note": "curated mappings are snowflake-os judgment, not published by Snowflake",
            "excluded_paid": sorted(set(skipped_paid)) if args.free_only else [],
            "dropped_for_budget": dropped,
            "plan_is_not_evidence": "a plan predicts effort; only readiness.py scores completion",
        },
    }


def render(plan: dict) -> str:
    out = [f"PLAN · {plan['goal']}"]
    c = plan["constraints"]
    flags = [k for k in ("free_only", "core_only") if c[k]]
    if c["max_hours"]:
        flags.append(f"max {c['max_hours']}h")
    if c["already_completed"]:
        flags.append(f"skipping {len(c['already_completed'])} completed")
    out.append(f"  constraints: {', '.join(flags) if flags else 'none'}")
    t = plan["totals"]
    out.append(f"  {t['courses']} courses · {t['hours']:g}h · {t['free_courses']} free / {t['paid_courses']} paid")
    out.append("")
    for i, s in enumerate(plan["steps"], 1):
        out.append(f"{i}. {s['name']}  [{s['tier']}]  {s['hours']:g}h")
        out.append(f"   why: {s['why']}")
        if not s["courses"]:
            # Say WHICH kind of empty this is. "Already covered" and "you priced
            # every option out" are opposite facts and must not share a message.
            if s.get("excluded_as_paid"):
                out.append(f"   ⚠ NOT COVERED — every mapped course is paid, and --free-only "
                           f"excluded them: {', '.join(s['excluded_as_paid'])}")
            elif s.get("covered_earlier"):
                out.append(f"   (covered earlier in this plan by {', '.join(s['covered_earlier'])})")
            else:
                out.append("   ⚠ NOT COVERED — no course in the catalogue maps to this competency")
        for c in s["courses"]:
            hrs = f"{c['effort_hours']}h" if c["effort_hours"] is not None else UNMEASURED
            out.append(f"   · {c['code']:<14} {hrs:>6}  {'FREE' if c['free'] else 'PAID'}  "
                       f"{c['title'][:52]}  [{c['basis']}]")
            if alts := s.get("substitutes", {}).get(c["code"]):
                out.append(f"     (or instead: {', '.join(alts)})")
        out.append(f"   order: {s['order_basis']}")
        out.append("")
    h = plan["honesty"]
    out.append("HONEST EDGES")
    out.append(f"  · {h['mappings_curated']}/{h['mappings_total']} mappings are curated "
               f"({h['curated_share']:.0%}) — {h['note']}")
    if h["excluded_paid"]:
        out.append(f"  · --free-only excluded {len(h['excluded_paid'])} paid course(s): "
                   f"{', '.join(h['excluded_paid'])}")
    if h["dropped_for_budget"]:
        out.append(f"  · budget dropped {len(h['dropped_for_budget'])}: {', '.join(h['dropped_for_budget'])}")
    out.append(f"  · {h['plan_is_not_evidence']}")
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    q = sub.add_parser("plan", help="build an ordered learning plan")
    g = q.add_mutually_exclusive_group(required=True)
    g.add_argument("--role", help="a role slug (see catalog.py stats)")
    g.add_argument("--exam", help="a SnowPro exam code, e.g. GES-C02")
    g.add_argument("--competency", help="comma-separated competency ids")
    q.add_argument("--have", help="comma-separated course codes already completed")
    q.add_argument("--free-only", action="store_true")
    q.add_argument("--core-only", action="store_true")
    q.add_argument("--max-hours", type=float)
    q.add_argument("--json", action="store_true")

    args = p.parse_args(argv)
    plan = build_plan(Catalog(), args)
    print(json.dumps(plan, indent=2, ensure_ascii=False) if args.json else render(plan))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
