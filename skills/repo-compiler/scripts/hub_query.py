#!/usr/bin/env python3
"""hub_query — progressive disclosure for the hub's compiled toolsets.

The hub compiles every top-rated cited repo into knowledge + tooling (see repo_compile.py).
This is the RETRIEVAL side: an agent working in FDE-os shouldn't carry 7 repos' worth of context
(backbone bloat) — it should ask, on trigger:

    python3 skills/repo-compiler/scripts/hub_query.py find observability evals
    python3 skills/repo-compiler/scripts/hub_query.py recipe langfuse
    python3 skills/repo-compiler/scripts/hub_query.py list

Deterministic term-overlap ranking over hub-skills.json (name/kind/oneLine/useWhen/integration).
Zero matches returns a diagnostic (what vocabulary exists), never a silent empty. Also exposed as
the `hub_find` MCP tool (fde-mcp-server), so Claude/Codex/Hermes get the same disclosure path.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.abspath(os.path.join(_HERE, "..", "..", ".."))
DEFAULT_REGISTRY = os.path.join(_ROOT, "knowledge", "hub", "hub-skills.json")

_WORD_RE = re.compile(r"[a-z0-9][a-z0-9+-]*")


def _terms(text: str) -> set[str]:
    return set(_WORD_RE.findall(text.lower()))


def _haystack(skill: dict) -> set[str]:
    parts = [skill.get("name", ""), skill.get("kind", ""), skill.get("oneLine", ""),
             skill.get("integration", {}).get("as", ""),
             skill.get("integration", {}).get("how", "")]
    parts += skill.get("useWhen", [])
    return _terms(" ".join(parts))


def load_registry(path: str = DEFAULT_REGISTRY) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        return json.load(f)["skills"]


def find(query: str, skills: list[dict], top: int = 3) -> list[tuple[float, dict]]:
    """Rank skills by term overlap with the query. Deterministic; score = |q ∩ hay| / |q|."""
    q = _terms(query)
    if not q:
        return []
    scored = []
    for s in skills:
        hit = len(q & _haystack(s))
        if hit:
            scored.append((round(hit / len(q), 3), s))
    scored.sort(key=lambda t: (-t[0], -t[1].get("stars", 0), t[1]["name"]))
    return scored[:top]


def render_skill(s: dict, score: float | None = None) -> str:
    head = f"{s['name']} (⭐{s.get('stars', '?')}, {s['kind']}"
    head += f", match {score}" if score is not None else ""
    head += ")"
    lines = [head,
             f"  {s['oneLine']}",
             f"  integrate as: {s['integration']['as']} — {s['integration']['how']}",
             f"  not good at: {'; '.join(s['notGoodAt'])}",
             f"  source: {s['source']['url']} @ {s['source']['sha'][:8]}"]
    if s.get("useWhen"):
        lines.insert(2, f"  use when: {'; '.join(s['useWhen'][:3])}")
    return "\n".join(lines)


def diagnose(skills: list[dict]) -> str:
    kinds = sorted({s["kind"] for s in skills})
    names = ", ".join(s["name"] for s in skills)
    return ("no match in the hub registry.\n"
            f"  kinds available: {', '.join(kinds)}\n"
            f"  repos compiled: {names}\n"
            "  (if the capability should exist, add the repo to knowledge/hub/repos.yml and "
            "run repo_compile.py all)")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Query the hub's compiled toolsets.")
    ap.add_argument("--registry", default=DEFAULT_REGISTRY)
    sub = ap.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("find", help="rank toolsets against a need")
    f.add_argument("need", nargs="+")
    f.add_argument("--top", type=int, default=3)
    r = sub.add_parser("recipe", help="full entry for one repo (by name fragment or slug)")
    r.add_argument("repo")
    sub.add_parser("list", help="one line per compiled toolset")
    args = ap.parse_args(argv)

    try:
        skills = load_registry(args.registry)
    except (OSError, json.JSONDecodeError, KeyError) as e:
        print(f"error: hub registry unreadable ({e}) — run repo_compile.py all first",
              file=sys.stderr)
        return 1

    if args.cmd == "list":
        for s in skills:
            print(f"{s['name']:42s} {s['kind']:18s} → {s['integration']['as']}")
        return 0
    if args.cmd == "recipe":
        frag = args.repo.lower()
        hits = [s for s in skills if frag in s["name"].lower() or frag in s["id"]]
        if not hits:
            print(diagnose(skills))
            return 2
        for s in hits:
            print(render_skill(s))
        return 0
    results = find(" ".join(args.need), skills, top=args.top)
    if not results:
        print(diagnose(skills))
        return 2
    for score, s in results:
        print(render_skill(s, score))
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
