#!/usr/bin/env python3
"""jd-compiler — turn a Forward-Deployed-Engineer job description into structured competency
knowledge, and compile many JDs into a cross-company competency matrix that feeds the knowledge base.

This is idea I1 from the FDE-os ideation ("a JD is the input → competency knowledge → readiness").
The repo's knowledge base was thin and the demand signal was locked inside prose JDs; this extracts
it deterministically: which of the FDE competency clusters a role requires, the *specific* tools and
frameworks it names, and its level/seniority — then aggregates across JDs into "what the FDE market
actually demands." The `to_note` / `matrix --note` outputs are prose the `knowledgefy` skill turns
into a navigable competency spine, so compiling JDs literally grows the knowledge base.

Deterministic, offline core (a taxonomy + keyword extraction over the JD text). Reading a raw web
posting into clean JD markdown is an upstream step a human/agent does first; this scores the markdown.

Usage:
  python3 jd_compile.py compile course/target-jds/reflection-ai-fde.md [--json]
  python3 jd_compile.py matrix course/target-jds/*.md --note knowledge/vault/jd-competencies
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

# ---------------------------------------------------------------- the FDE competency taxonomy
# Six clusters (+ a post-training stretch) — the same spine the course curriculum uses. Each carries
# the TELLS that mark a JD as requiring it.
CLUSTERS = {
    "production_swe":   {"label": "Production SWE",
                         "tells": ["software engineering", "production", "python", "typescript", "ship", "code review", "ci/cd", "testing"]},
    "enterprise_deploy":{"label": "Enterprise / hybrid deployment",
                         "tells": ["docker", "kubernetes", "k8s", "terraform", "devops", "cloud", "vpc", "on-prem", "on premises", "hybrid", "gke", "deploy"]},
    "modern_ai_stack":  {"label": "Modern AI stack",
                         "tells": ["rag", "vector database", "vector db", "embedding", "fine-tun", "evaluation", "eval pipeline", "retrieval"]},
    "agentic_design":   {"label": "Agentic system design",
                         "tells": ["agent", "agentic", "llm workflow", "orchestrat", "mcp", "model context protocol", "tool-use", "tool use", "multi-agent", "guardrail"]},
    "fde_craft":        {"label": "The FDE craft",
                         "tells": ["customer-facing", "customer facing", "stakeholder", "discovery", "pre-sales", "presales", "high agency", "ambiguity", "embed"]},
    "leadership":       {"label": "Technical leadership & playbooks",
                         "tells": ["lead", "mentor", "playbook", "best practices", "technical strategy", "scale the", "standards", "team"]},
    "post_training":    {"label": "Post-training (stretch)",
                         "tells": ["post-training", "rlhf", "reward model", "preference optimization", "rl environment", "distributed training", "verifier"]},
}

# Specific named tools/frameworks worth extracting — the concrete vocabulary the market demands.
TOOLS = {
    "languages":       ["python", "typescript", "golang", "java ", "rust", "scala"],
    "agent_frameworks":["langgraph", "langchain", "crewai", "autogen", "llamaindex", "openai agents", "claude agent sdk", "google adk", " adk", "a2a"],
    "protocols":       ["model context protocol", "mcp"],
    "vector_dbs":      ["pinecone", "weaviate", "faiss", "chromadb", "milvus", "pgvector"],
    "llm_providers":   ["openai", "anthropic", "claude", "gemini", "vertex", "bedrock", "azure openai"],
    "deploy":          ["docker", "kubernetes", "k8s", "terraform", "gke", "helm", "ci/cd", "vpc", "on-prem", "air-gap"],
    "eval_obs":        ["evaluation", "observability", "ragas", "llm-as-judge", "tracing", "eval pipeline"],
    "ml":              ["rag", "fine-tun", "rlhf", "reward model", "embedding"],
    "patterns":        ["react", "self-reflection", "hierarchical delegation", "multi-agent", "tool-use", "guardrail", "orchestrat"],
}

_YEARS = re.compile(r"(\d+)\+?\s*years?")
_LEVELS = re.compile(r"\b(staff|principal|senior|lead|junior|level\s*[ivx]+|fde-?[ivx]+|l[3-7])\b", re.I)


def _norm(text: str) -> str:
    """Lowercase and collapse whitespace for matching."""
    return re.sub(r"\s+", " ", text.lower())


def _found(blob: str, terms: list) -> list:
    """Which of the given terms appear in the normalized text."""
    return sorted({t.strip() for t in terms if t in blob})


def compile_jd(text: str, name: str = "") -> dict:
    """Extract the competency profile of one JD: clusters required, tools named, level."""
    blob = _norm(text)
    clusters = {}
    for cid, meta in CLUSTERS.items():
        hits = [t for t in meta["tells"] if t in blob]
        clusters[cid] = {"label": meta["label"], "present": len(hits) > 0, "hits": len(hits), "matched": hits}
    tools = {cat: _found(blob, terms) for cat, terms in TOOLS.items()}
    tools = {cat: v for cat, v in tools.items() if v}
    years = sorted({int(m) for m in _YEARS.findall(blob)}, reverse=True)
    levels = sorted({m.strip() for m in _LEVELS.findall(text)})
    return {
        "name": name or "jd",
        "clusters": clusters,
        "required_clusters": [c for c, v in clusters.items() if v["present"]],
        "tools": tools,
        "years_max": years[0] if years else None,
        "levels": levels,
    }


def cross_compile(compiled: list) -> dict:
    """Aggregate many compiled JDs → which competencies & tools recur across the market."""
    n = len(compiled)
    cluster_freq = {c: 0 for c in CLUSTERS}
    tool_freq: dict = {}
    for jd in compiled:
        for c in jd["required_clusters"]:
            cluster_freq[c] += 1
        for cat, terms in jd["tools"].items():
            for t in terms:
                tool_freq.setdefault(cat, {}).setdefault(t, 0)
                tool_freq[cat][t] += 1
    # universal = required by every JD; the load-bearing core of the FDE role
    universal = [CLUSTERS[c]["label"] for c, k in cluster_freq.items() if n and k == n]
    return {
        "n": n,
        "names": [jd["name"] for jd in compiled],
        "cluster_freq": {CLUSTERS[c]["label"]: k for c, k in cluster_freq.items()},
        "universal_clusters": universal,
        "tool_freq": {cat: dict(sorted(d.items(), key=lambda x: -x[1])) for cat, d in tool_freq.items()},
    }


def to_note(jd: dict, source: str = "") -> str:
    """Prose competency note for one role — headings become concepts, tools become evidence (for knowledgefy)."""
    L = [f"# {jd['name']} — FDE competency profile", ""]
    if source:
        L.append(f"Source: [{source}]({source})" if source.startswith("http") else f"Source: {source}")
        L.append("")
    lvl = ", ".join(jd["levels"]) or "unspecified"
    yrs = f"{jd['years_max']}+ years" if jd["years_max"] else "unspecified"
    L.append(f"This role demands **{len(jd['required_clusters'])} of {len(CLUSTERS)}** FDE competency "
             f"clusters. Seniority: {lvl}; experience: {yrs}.")
    L.append("")
    for cid in jd["required_clusters"]:
        c = jd["clusters"][cid]
        L.append(f"## {c['label']}")
        L.append(f"Required by the {jd['name']} role (signal terms: {', '.join(c['matched'])}).")
        L.append("")
    if jd["tools"]:
        L.append("## Named tools and frameworks")
        for cat, terms in jd["tools"].items():
            L.append(f"- **{cat.replace('_', ' ')}**: {', '.join(terms)}.")
        L.append("")
    return "\n".join(L).rstrip() + "\n"


def cross_note(cross: dict) -> str:
    """The cross-company synthesis note — the grounded 'what the FDE market demands' knowledge."""
    L = ["# FDE competency demand — cross-company synthesis", "",
         f"Compiled from {cross['n']} real job descriptions: {', '.join(cross['names'])}.", ""]
    if cross["universal_clusters"]:
        L.append("## Universal competencies")
        L.append("Required by **every** JD compiled — the load-bearing core of the FDE role: "
                 + ", ".join(cross["universal_clusters"]) + ".")
        L.append("")
    L.append("## Competency demand frequency")
    for label, k in sorted(cross["cluster_freq"].items(), key=lambda x: -x[1]):
        if k:
            L.append(f"- **{label}**: required by {k}/{cross['n']} roles.")
    L.append("")
    L.append("## Most-demanded tools and frameworks")
    for cat, d in cross["tool_freq"].items():
        top = ", ".join(f"{t} ({k})" for t, k in d.items())
        L.append(f"- **{cat.replace('_', ' ')}**: {top}.")
    L.append("")
    return "\n".join(L).rstrip() + "\n"


def _read(path: str) -> str:
    """Read a JD file as UTF-8 text."""
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def _name_from_path(path: str) -> str:
    """Role label derived from a JD filename."""
    return os.path.splitext(os.path.basename(path))[0]


def main(argv: list[str] | None = None) -> int:
    """CLI entry point: compile | matrix."""
    ap = argparse.ArgumentParser(description="Compile FDE job descriptions into competency knowledge.")
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("compile", help="compile one JD → competency profile")
    c.add_argument("jd")
    c.add_argument("--json", action="store_true")
    m = sub.add_parser("matrix", help="compile many JDs → cross-company competency matrix")
    m.add_argument("jds", nargs="+")
    m.add_argument("--json", action="store_true")
    m.add_argument("--note", metavar="DIR", help="also write per-JD + synthesis prose notes into DIR (a knowledgefy vault)")
    args = ap.parse_args(argv)

    if args.cmd == "compile":
        jd = compile_jd(_read(args.jd), _name_from_path(args.jd))
        print(json.dumps(jd, indent=2) if args.json else to_note(jd, source=args.jd))
        return 0

    compiled = [compile_jd(_read(p), _name_from_path(p)) for p in args.jds]
    cross = cross_compile(compiled)
    if args.note:
        os.makedirs(args.note, exist_ok=True)
        for jd, path in zip(compiled, args.jds):
            with open(os.path.join(args.note, f"{jd['name']}.md"), "w", encoding="utf-8") as fh:
                fh.write(to_note(jd, source=path))
        with open(os.path.join(args.note, "_cross-company-synthesis.md"), "w", encoding="utf-8") as fh:
            fh.write(cross_note(cross))
        print(f"wrote {len(compiled)} competency notes + synthesis to {args.note}/")
    if args.json:
        print(json.dumps(cross, indent=2))
    elif not args.note:
        print(cross_note(cross))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
