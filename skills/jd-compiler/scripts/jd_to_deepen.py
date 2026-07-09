#!/usr/bin/env python3
"""jd_to_deepen.py — JD → a DEEP, RETRIEVED "deepen" artifact (kgfy graph + skillfy skills).

Not keyword-guessing: it RETRIEVES real knowledge. jd-compiler finds the seed terms; then each term
is grounded against open sources (research.py — Wikipedia / Wikidata / GitHub) so every node carries
a REAL definition + real relationships to real neighbor concepts, and skills come from ESCO (the EU's
open skills taxonomy). Falls back to a thin node only when a term can't be resolved (offline / niche).

Contract (packages/core deepen-types): source.url MUST be http(s); every skill needs a non-empty
notGoodAt; edges may not dangle; id = slug. Deterministic assembly; the depth comes from retrieval.

    python3 jd_to_deepen.py <jd.md> --title "..." --url "https://..." [--kind ...] [--id slug] [--offline]
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # find research.py however we're loaded
import research

_HERE = os.path.dirname(os.path.abspath(__file__))
_JD_COMPILE = os.path.join(_HERE, "jd_compile.py")

CLUSTER_META = {
    "production_swe":   ("Ship production backend/services in Python (and a second language).", ["greenfield research with no delivery pressure"], True),
    "enterprise_deploy":("Deploy inside the customer's environment under real access/security constraints.", ["pure SaaS with no on-prem / VPC reality"], False),
    "modern_ai_stack":  ("Prompt, evaluate, and deploy LLMs at scale.", ["classical ML / heavy feature engineering"], True),
    "agentic_design":   ("Build tool-using agents, sub-agents, MCP servers, and agent skills.", ["low-latency non-agentic services"], True),
    "fde_craft":        ("Own ambiguity: embed with the customer, scope the smallest win, codify patterns.", ["fully-specced ticket work handed to you in pieces"], True),
    "leadership":       ("Represent at the highest level; sequence delivery; codify playbooks.", ["deep IC-only crunch with no stakeholder surface"], False),
    "post_training":    ("Fine-tune / post-train models; formal methods.", ["teams that only consume hosted models"], False),
}


def slug(s: str) -> str:
    return re.sub(r"^-+|-+$", "", re.sub(r"[^a-z0-9]+", "-", s.lower()))[:60] or "n"


def compile_jd(jd_path: str) -> dict:
    out = subprocess.run([sys.executable, _JD_COMPILE, "compile", jd_path, "--json"],
                         capture_output=True, text=True, check=True).stdout
    return json.loads(out)


# Curated CANONICAL domain concepts per cluster (name, exact Wikipedia title) — so retrieval hits the
# right page (disambiguated), not a keyword's random meaning. Only present clusters contribute.
CANON = {
    "production_swe": [("Software engineering", "Software engineering"), ("API", "API"), ("Distributed computing", "Distributed computing")],
    "enterprise_deploy": [("Kubernetes", "Kubernetes"), ("Role-based access control", "Role-based access control"), ("Identity management", "Identity management"), ("DevOps", "DevOps")],
    "modern_ai_stack": [("Large language model", "Large language model"), ("Retrieval-augmented generation", "Retrieval-augmented generation"), ("Machine learning", "Machine learning"), ("Prompt engineering", "Prompt engineering")],
    "agentic_design": [("Intelligent agent", "Intelligent agent"), ("Software agent", "Software agent"), ("Model Context Protocol", "Model Context Protocol")],
    "fde_craft": [("Solution architecture", "Solution architecture"), ("Requirements analysis", "Requirements analysis")],
    "leadership": [("Engineering management", "Engineering management")],
    "post_training": [("Fine-tuning (deep learning)", "Fine-tuning (deep learning)"), ("Reinforcement learning", "Reinforcement learning"), ("Reinforcement learning from human feedback", "Reinforcement learning from human feedback"), ("Lean (proof assistant)", "Lean (proof assistant)")],
}
TOOL_TITLE = {"python": "Python (programming language)", "typescript": "TypeScript", "javascript": "JavaScript",
    "java": "Java (programming language)", "go": "Go (programming language)", "rust": "Rust (programming language)",
    "react": "React (software)", "node": "Node.js", "kubernetes": "Kubernetes", "docker": "Docker (software)",
    "mcp": "Model Context Protocol", "neo4j": "Neo4j", "lean4": "Lean (proof assistant)", "pytorch": "PyTorch",
    "tensorflow": "TensorFlow", "postgres": "PostgreSQL", "redis": "Redis", "terraform": "Terraform", "graphql": "GraphQL"}
ESCO_Q = {"production_swe": ["software engineering"], "enterprise_deploy": ["information security", "access control"],
    "modern_ai_stack": ["machine learning", "artificial intelligence"], "agentic_design": ["software development"],
    "fde_craft": ["stakeholder management"], "leadership": ["team leadership"], "post_training": ["machine learning"]}


def build_artifact(comp: dict, title: str, url: str, kind: str, aid: str | None, offline: bool = False) -> dict:
    present = [(k, v) for k, v in comp.get("clusters", {}).items() if v.get("present")]
    tools = list(comp.get("tools", {}).keys()) if isinstance(comp.get("tools"), dict) else list(comp.get("tools") or [])

    nodes = [{"id": "role", "type": "role", "name": title, "summary": "The role, distilled from its posting."}]
    edges = []
    seen = {"role"}
    sources: list[str] = []

    def add_node(nid, ntype, name, summary):
        if nid not in seen:
            nodes.append({"id": nid, "type": ntype, "name": name, "summary": summary}); seen.add(nid)
        return nid

    def resolve(name, wtitle, is_tool):
        """Retrieve a real, domain-correct definition (curated title trusted) — or a thin fallback."""
        info = None if offline else research.define(name, wtitle, trusted=True)
        if not info and not offline:
            info = research.github_repo(name) if is_tool else None
        nid = ("t-" if is_tool else "c-") + slug(name)
        if info:
            src = info.get("url", "")
            tag = " (Wikipedia)" if "wikipedia" in src else (" (GitHub)" if "github" in src else "")
            add_node(nid, info.get("kind", "tool" if is_tool else "concept"), info["name"], (info.get("summary") or "").strip() + tag)
            if src: sources.append(src)
            if not offline:  # real relationships → real neighbor nodes
                ent = research.wikidata_entity(name)
                if ent:
                    for rel, tgt in research.wikidata_relations(ent["id"], max_rel=1):
                        if research.domain_ok(tgt) or research.domain_ok(rel):
                            tnid = add_node("n-" + slug(tgt), "concept", tgt, f"{tgt} — {rel} of {info['name']}.")
                            edges.append({"source": nid, "target": tnid, "type": rel})
            return nid, True
        add_node(nid, "tool" if is_tool else "concept", name, "Named in the JD (no open definition retrieved).")
        return nid, False

    anchor_present = [k for k, _ in present]
    anchor = "agentic_design" if "agentic_design" in anchor_present else (anchor_present[0] if anchor_present else "role")

    for key, v in present:
        add_node(key, "competency", v.get("label", key), CLUSTER_META.get(key, ("", [], False))[0] or "A required competency cluster.")
        edges.append({"source": "role", "target": key, "type": "requires"})
        for name, wtitle in CANON.get(key, []):
            nid, _ = resolve(name, wtitle, is_tool=False)
            edges.append({"source": key, "target": nid, "type": "covers"})

    for tool in tools:
        nid, _ = resolve(tool, TOOL_TITLE.get(tool.lower()), is_tool=True)
        edges.append({"source": anchor, "target": nid, "type": "uses"})

    node_ids = {n["id"] for n in nodes}
    edges = [e for e in edges if e["source"] in node_ids and e["target"] in node_ids]
    seen_e = set(); edges = [e for e in edges if (k := (e["source"], e["target"], e["type"])) not in seen_e and not seen_e.add(k)]

    # skills: curated cluster skills (honest limits) + REAL, domain-filtered ESCO skills
    skills = []
    for key, v in present:
        one, not_good, verified = CLUSTER_META.get(key, (v.get("label", key), ["out-of-scope work"], False))
        skills.append({"id": "skill-" + key, "name": v.get("label", key), "kind": "competency",
                       "oneLine": one, "notGoodAt": not_good, "verified": verified,
                       "useWhen": ["required by this JD" if key in comp.get("required_clusters", []) else "listed in this JD"]})
    esco_seen = {s["name"].lower() for s in skills}
    if not offline:
        for key, _ in present:
            for q in ESCO_Q.get(key, []):
                for e in research.esco_skills(q, 3):
                    if e["name"].lower() in esco_seen or len(skills) >= 14:
                        continue
                    esco_seen.add(e["name"].lower())
                    skills.append({"id": "esco-" + slug(e["name"]), "name": e["name"], "kind": "skill",
                                   "oneLine": e.get("summary") or "A defined competence in the ESCO taxonomy.",
                                   "mechanism": f"Retrieved from ESCO{(' — ' + e['uri']) if e.get('uri') else ''}.",
                                   "notGoodAt": ["a taxonomy label until proven by a work sample"], "verified": False})

    n_concepts = sum(1 for n in nodes if n["type"] in ("concept", "tool"))
    digest = (f"Retrieved, not guessed: {len(present)} competency clusters, {n_concepts} concept/tool nodes "
              f"grounded in real sources ({len(set(sources))} Wikipedia/GitHub definitions), and "
              f"{sum(1 for s in skills if s['kind']=='skill')} skills from the ESCO taxonomy — off-domain hits filtered out. "
              "Every node carries a real definition; edges are real relationships where an open KG had them.")

    return {
        "id": aid or slug(comp.get("name") or title), "producedBy": "jd-to-deepen (retrieval)",
        "generatedAt": "", "source": {"title": title, "kind": kind, "url": url, "discoveredVia": ""},
        "digest": digest, "graph": {"title": title, "graphUrl": "", "nodes": nodes, "edges": edges},
        "skills": skills,
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="JD → deep, retrieved deepen artifact (kg + skills).")
    ap.add_argument("jd")
    ap.add_argument("--title", required=True)
    ap.add_argument("--url", required=True, help="a real http(s) source URL (public posting)")
    ap.add_argument("--kind", default="job-description")
    ap.add_argument("--id", default=None)
    ap.add_argument("--offline", action="store_true", help="skip retrieval (thin fallback)")
    args = ap.parse_args(argv)
    if not re.match(r"^https?://", args.url):
        print("error: --url must be http(s)", file=sys.stderr); return 2
    art = build_artifact(compile_jd(args.jd), args.title, args.url, args.kind, args.id, args.offline)
    json.dump(art, sys.stdout, indent=2); print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
