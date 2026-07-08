#!/usr/bin/env python3
"""jd_to_deepen.py — JD → a portfolio "deepen" artifact (kgfy graph + skillfy skills).

Turns a job description into the exact artifact the agentic-portfolio node ingests
(POST /api/ingest-knowledge) and renders interactively at /graph/<id>: a knowledge graph
(role → competency clusters → named tools) plus skills with HONEST limits. Reuses jd_compile
for the extraction (clusters + tools), so this is the "skillfy/kgfy" bridge for a JD.

Contract (packages/core deepen-types): source.url MUST be http(s) (the node refuses ungrounded
knowledge), every skill needs a non-empty notGoodAt, edges may not dangle, id = slug.

    python3 jd_to_deepen.py <jd.md> --title "..." --url "https://..." [--kind job-description] [--id slug]

Prints the artifact JSON on stdout — commit it into content/deepen.json (files) or POST it to
/api/ingest-knowledge (KV). Deterministic, stdlib.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_JD_COMPILE = os.path.join(_HERE, "jd_compile.py")


def slug(s: str) -> str:
    return re.sub(r"^-+|-+$", "", re.sub(r"[^a-z0-9]+", "-", s.lower()))[:60]


# honest, reusable framing per competency cluster (oneLine + the limit + is-it-proven-in-this-repo)
CLUSTER_META = {
    "production_swe":   ("Ship production backend/services in Python (and a second language).", ["greenfield research with no delivery pressure"], True),
    "enterprise_deploy":("Deploy inside the customer's environment under real access/security constraints.", ["pure SaaS with no on-prem / VPC reality"], False),
    "modern_ai_stack":  ("Prompt, evaluate, and deploy LLMs at scale.", ["classical ML / heavy feature engineering"], True),
    "agentic_design":   ("Build tool-using agents, sub-agents, MCP servers, and agent skills.", ["low-latency non-agentic services"], True),
    "fde_craft":        ("Own ambiguity: embed with the customer, scope the smallest win, codify patterns.", ["fully-specced ticket work handed to you in pieces"], True),
    "leadership":       ("Represent at the highest level; sequence delivery; codify playbooks.", ["deep IC-only crunch with no stakeholder surface"], False),
    "post_training":    ("Fine-tune / post-train models.", ["teams that only consume hosted models"], False),
}


def compile_jd(jd_path: str) -> dict:
    out = subprocess.run([sys.executable, _JD_COMPILE, "compile", jd_path, "--json"],
                         capture_output=True, text=True, check=True).stdout
    return json.loads(out)


def build_artifact(comp: dict, title: str, url: str, kind: str, aid: str | None) -> dict:
    present = [(k, v) for k, v in comp.get("clusters", {}).items() if v.get("present")]
    tools = list(comp.get("tools", {}).keys()) if isinstance(comp.get("tools"), dict) else list(comp.get("tools") or [])

    nodes = [{"id": "role", "type": "role", "name": title, "summary": f"{comp.get('years_max') or ''}"+(" yrs" if comp.get('years_max') else "")+" · "+", ".join(comp.get("levels") or []) or "the role"}]
    edges = []
    for key, v in present:
        nodes.append({"id": key, "type": "competency", "name": v.get("label", key),
                      "summary": "signals: " + ", ".join(v.get("matched", [])[:6])})
        edges.append({"source": "role", "target": key, "type": "requires"})
    anchor = "agentic_design" if any(k == "agentic_design" for k, _ in present) else (present[0][0] if present else "role")
    for t in tools:
        nid = "tool-" + slug(t)
        nodes.append({"id": nid, "type": "tool", "name": t, "summary": "named in the JD"})
        edges.append({"source": anchor, "target": nid, "type": "uses"})

    node_ids = {n["id"] for n in nodes}
    edges = [e for e in edges if e["source"] in node_ids and e["target"] in node_ids]   # never dangle

    skills = []
    for key, v in present:
        one, not_good, verified = CLUSTER_META.get(key, (v.get("label", key), ["out-of-scope work"], False))
        skills.append({
            "id": "skill-" + key, "name": v.get("label", key), "kind": "competency",
            "oneLine": one, "notGoodAt": not_good, "verified": verified,
            "useWhen": ["this JD lists it as required" if key in comp.get("required_clusters", []) else "this JD lists it"],
        })

    digest = (f"What this role actually demands, distilled: {len(present)} of 7 FDE competency clusters"
              + (f", {comp.get('years_max')}+ yrs" if comp.get("years_max") else "")
              + (f" ({', '.join(comp.get('levels'))})" if comp.get("levels") else "")
              + ". The graph maps role → clusters → the named tools; the skills carry honest limits "
              + "(what each is NOT good at) so the evidence stays trustworthy.")

    return {
        "id": aid or slug(comp.get("name") or title),
        "producedBy": "jd-to-deepen",
        "generatedAt": "",
        "source": {"title": title, "kind": kind, "url": url, "discoveredVia": ""},
        "digest": digest,
        "graph": {"title": title, "graphUrl": "", "nodes": nodes, "edges": edges},
        "skills": skills,
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="JD → deepen artifact (kg + skills).")
    ap.add_argument("jd")
    ap.add_argument("--title", required=True)
    ap.add_argument("--url", required=True, help="a real http(s) source URL (public posting) — required to be grounded")
    ap.add_argument("--kind", default="job-description")
    ap.add_argument("--id", default=None)
    args = ap.parse_args(argv)
    if not re.match(r"^https?://", args.url):
        print("error: --url must be http(s) (the node refuses ungrounded artifacts)", file=sys.stderr)
        return 2
    art = build_artifact(compile_jd(args.jd), args.title, args.url, args.kind, args.id)
    json.dump(art, sys.stdout, indent=2)
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
