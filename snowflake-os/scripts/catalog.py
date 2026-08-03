#!/usr/bin/env python3
"""snowflake-os · catalog — the offline query engine over the Snowflake catalogue.

Pure stdlib. Reads the committed snapshot; never touches the network.

    python3 snowflake-os/scripts/catalog.py stats
    python3 snowflake-os/scripts/catalog.py find snowpark python --free
    python3 snowflake-os/scripts/catalog.py show OD-ESS-DWW
    python3 snowflake-os/scripts/catalog.py competency genai-cortex
    python3 snowflake-os/scripts/catalog.py exams

A zero-result search NEVER fails silent: it exits 2 and prints the vocabulary
that would have matched, so the caller can tell "nothing there" apart from
"you used the wrong word".
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "snapshot" / "catalog.json"
COMPETENCIES = ROOT / "snapshot" / "competencies.json"
SATELLITES = ROOT / "snapshot" / "satellites.json"

UNMEASURED = "not measured"


class Catalog:
    """The snapshot, loaded once, with the joins the engines need."""

    def __init__(self, catalog_path: Path = CATALOG, competency_path: Path = COMPETENCIES):
        self.raw = json.loads(Path(catalog_path).read_text(encoding="utf-8"))
        self.spec = json.loads(Path(competency_path).read_text(encoding="utf-8"))
        self.satellites = (
            json.loads(SATELLITES.read_text(encoding="utf-8")) if SATELLITES.exists() else {"satellites": []}
        )
        self.courses = {c["code"]: c for c in self.raw["courses"]}
        self.tracks = {t["slug"]: t for t in self.raw["tracks"]}
        self.roles_upstream = {r["slug"]: r for r in self.raw["roles"]}
        self.competencies = {c["id"]: c for c in self.spec["competencies"]}
        self.roles = self.spec["roles"]

        # One exam may have several localised pages; collapse to the exam.
        self.exams: dict[str, dict] = {}
        for page in self.raw["certifications"]:
            if page.get("kind") != "certification" or not page.get("exam_code"):
                continue
            code = page["exam_code"]
            best = self.exams.get(code)
            # Prefer the English page: it is the one with parsed objectives.
            if best is None or (page["language"] == "en" and best["language"] != "en"):
                self.exams[code] = page

    # ── lookups ──────────────────────────────────────────────────────────────

    def course(self, code: str) -> dict | None:
        return self.courses.get(code) or self.courses.get(code.upper())

    def effort(self, code: str) -> float | None:
        c = self.course(code)
        return c["effort_hours"] if c else None

    def requirement_units(self, comp_id: str) -> list[dict]:
        """A competency's requirements, with same-content alternatives collapsed.

        Returns one unit per thing you actually have to learn. A unit is either a
        single course or an `alternatives` group (any one member satisfies it),
        and a group costs its CHEAPEST member's hours. Both pathfinder and
        readiness use this, so a plan and its gate can never disagree about what
        the requirement was.
        """
        courses = {c["code"]: c for c in self.competency_courses(comp_id)}
        groups = self.spec.get("alternatives", {}).get(comp_id, [])
        units, claimed = [], set()
        for group in groups:
            members = [courses[c] for c in group if c in courses]
            if len(members) < 2:
                continue  # not an alternative if only one side is mapped here
            claimed.update(m["code"] for m in members)
            cheapest = min(members, key=lambda m: m["effort_hours"] or 0)
            units.append({
                "kind": "alternatives",
                "codes": [m["code"] for m in members],
                "hours": cheapest["effort_hours"] or 0,
                "cheapest": cheapest["code"],
                "courses": members,
            })
        for code, c in courses.items():
            if code not in claimed:
                units.append({
                    "kind": "course",
                    "codes": [code],
                    "hours": c["effort_hours"] or 0,
                    "cheapest": code,
                    "courses": [c],
                })
        return units

    def required_hours(self, comp_id: str) -> float:
        return sum(u["hours"] for u in self.requirement_units(comp_id))

    def competency_courses(self, comp_id: str) -> list[dict]:
        comp = self.competencies.get(comp_id)
        if not comp:
            return []
        out = []
        for m in comp["courses"]:
            if c := self.course(m["code"]):
                out.append({**c, "basis": m["basis"]})
        return out

    def role_competencies(self, role: str) -> dict | None:
        return self.roles.get(role)

    def search(self, terms: list[str], free_only: bool = False, on_demand: bool = False) -> list[dict]:
        """Deterministic term-overlap over title + summary. No embeddings, no engine."""
        needles = [t.lower() for t in terms]
        scored = []
        for c in self.courses.values():
            if free_only and not c["free"]:
                continue
            if on_demand and c["delivery"] != "on-demand":
                continue
            hay = f"{c['code']} {c['title']} {c.get('summary') or ''}".lower()
            hits = sum(1 for n in needles if n in hay)
            if hits:
                title_hits = sum(1 for n in needles if n in c["title"].lower())
                scored.append((hits, title_hits, -(c["effort_hours"] or 0), c))
        scored.sort(key=lambda t: (-t[0], -t[1], t[2]))
        return [c for *_, c in scored]

    def vocabulary(self, limit: int = 24) -> list[str]:
        words: dict[str, int] = {}
        for c in self.courses.values():
            for w in re.findall(r"[a-z]{4,}", c["title"].lower()):
                if w in {"training", "snowflake", "with", "course", "level", "workshop", "badge"}:
                    continue
                words[w] = words.get(w, 0) + 1
        return [w for w, _ in sorted(words.items(), key=lambda kv: -kv[1])[:limit]]


# ─────────────────────────────── formatting ──────────────────────────────────


def fmt_course(c: dict, basis: str | None = None) -> str:
    hours = f"{c['effort_hours']}h" if c["effort_hours"] is not None else UNMEASURED
    tag = f"  [{basis}]" if basis else ""
    return (
        f"  {c['code']:<14} {hours:>6}  {c['difficulty'] or UNMEASURED:<9}"
        f" {'FREE' if c['free'] else 'PAID'}  {c['title'][:56]}{tag}"
    )


# ──────────────────────────────── commands ───────────────────────────────────


def cmd_stats(cat: Catalog, args) -> int:
    c = cat.raw["counts"]
    src = cat.raw["source"]
    total = sum(x["effort_hours"] or 0 for x in cat.courses.values())
    free = sum(x["effort_hours"] or 0 for x in cat.courses.values() if x["free"])
    print(f"snowflake-os catalogue · synced {src['fetched_at']} from {src['origin']}")
    print(f"  courses            {c['courses']}  ({total:g}h total · {free:g}h of it free)")
    print(f"  distinct exams     {c['distinct_exams']}  ({c['certification_pages']} pages incl. localisations)")
    print(f"  learning tracks    {c['tracks']}  ({c['tracks_with_published_sequence']} with a published sequence)")
    print(f"  role journeys      {c['roles']}  ({c['roles_with_published_courses']} publish their course list)")
    print(f"  competencies       {len(cat.competencies)} curated · {len(cat.roles)} role maps")
    print("  UNMEASURED:")
    print(f"    course effort         {c['courses_effort_unmeasured']}")
    print(f"    exam cost             {c['exams_cost_unmeasured']}  (Specialty pricing is not published)")
    print(f"    role course lists     {c['roles'] - c['roles_with_published_courses']}  (upstream publishes none)")
    print(f"    track sequences       {c['tracks'] - c['tracks_with_published_sequence']}")
    return 0


def cmd_find(cat: Catalog, args) -> int:
    hits = cat.search(args.terms, free_only=args.free, on_demand=args.on_demand)
    if not hits:
        print(
            f"no course matches {args.terms!r}.\n"
            f"the catalogue's vocabulary is: {', '.join(cat.vocabulary())}\n"
            f"(zero results is a real answer — this exits 2 rather than printing an empty list)",
            file=sys.stderr,
        )
        return 2
    print(f"{len(hits)} match(es) for {' '.join(args.terms)}:")
    for c in hits[: args.limit]:
        print(fmt_course(c))
    return 0


def cmd_show(cat: Catalog, args) -> int:
    c = cat.course(args.code)
    if not c:
        print(f"unknown course code {args.code!r} — try `catalog.py find <term>`", file=sys.stderr)
        return 2
    print(f"{c['code']} · {c['title']}")
    print(f"  {c['delivery']} · {'free' if c['free'] else 'paid'} · "
          f"{c['effort_hours'] if c['effort_hours'] is not None else UNMEASURED}h · {c['difficulty']}")
    print(f"  {c['url']}")
    in_tracks = [t["slug"] for t in cat.tracks.values() if c["code"] in t["sequence"]]
    print(f"  tracks: {', '.join(in_tracks) or '—'}")
    comps = [cid for cid, comp in cat.competencies.items()
             if any(m["code"] == c["code"] for m in comp["courses"])]
    print(f"  competencies: {', '.join(comps) or '—'}")
    if c.get("summary"):
        print(f"\n  {c['summary'][:400]}")
    print(f"\n  provenance: {c['provenance']['url']}")
    print(f"              sha256 {c['provenance']['sha256'][:16]}… fetched {c['provenance']['fetched_at']}")
    return 0


def cmd_competency(cat: Catalog, args) -> int:
    comp = cat.competencies.get(args.id)
    if not comp:
        print(f"unknown competency {args.id!r}. known: {', '.join(sorted(cat.competencies))}", file=sys.stderr)
        return 2
    courses = cat.competency_courses(args.id)
    hours = sum(c["effort_hours"] or 0 for c in courses)
    print(f"{comp['id']} · {comp['name']}")
    print(f"  why: {comp['why']}")
    print(f"  {len(courses)} courses · {hours:g}h")
    for c in sorted(courses, key=lambda x: (x["effort_hours"] or 0)):
        print(fmt_course(c, c["basis"]))
    if comp["exams"]:
        print("  exams:")
        for e in comp["exams"]:
            ex = cat.exams.get(e["code"])
            print(f"    {e['code']:<10} [{e['basis']}]  {ex['title'][:56] if ex else UNMEASURED}")
    return 0


def cmd_exams(cat: Catalog, args) -> int:
    print(f"{len(cat.exams)} distinct SnowPro exams:")
    for code, e in sorted(cat.exams.items()):
        cost = f"${e['exam_cost_usd']}" if e["exam_cost_measured"] else UNMEASURED
        print(f"  {code:<10} {str(e['tier']):<10} {cost:<13} "
              f"{len(e['tests'])} objectives  {e['title'][:48]}")
    return 0


def cmd_satellites(cat: Catalog, args) -> int:
    sats = cat.satellites["satellites"]
    print(f"{len(sats)} registered satellites — pointers, never forks "
          f"(pinned {cat.satellites.get('pinned_at')}):")
    for s in sats:
        flag = "" if s.get("vendorable", True) else f"  ⚠ QUARANTINED ({s['caution']})"
        print(f"\n  {s['slug']}  ·  {s['repo']}  ★{s['stars']}  {s['license']}{flag}")
        print(f"    layer: {s['layer']}  ·  sha {s['sha'][:12]}…  ·  pushed {s['pushed']}")
        print(f"    why:  {' '.join(s['why_cited'].split())[:150]}")
        print(f"    not good at: {' '.join(s['not_good_at'].split())[:120]}")
    print("\n  snowflake-os occupies the BECOMING layer; every satellite above is DOING.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("stats", help="what the snapshot contains, including what it does NOT know")
    s.set_defaults(fn=cmd_stats)

    f = sub.add_parser("find", help="search courses by term")
    f.add_argument("terms", nargs="+")
    f.add_argument("--free", action="store_true")
    f.add_argument("--on-demand", action="store_true")
    f.add_argument("--limit", type=int, default=12)
    f.set_defaults(fn=cmd_find)

    sh = sub.add_parser("show", help="one course, with provenance")
    sh.add_argument("code")
    sh.set_defaults(fn=cmd_show)

    c = sub.add_parser("competency", help="courses that build one competency")
    c.add_argument("id")
    c.set_defaults(fn=cmd_competency)

    e = sub.add_parser("exams", help="the distinct certification exams")
    e.set_defaults(fn=cmd_exams)

    sa = sub.add_parser("satellites", help="external Snowflake tooling we point at, never fork")
    sa.set_defaults(fn=cmd_satellites)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.fn(Catalog(), args)


if __name__ == "__main__":
    raise SystemExit(main())
