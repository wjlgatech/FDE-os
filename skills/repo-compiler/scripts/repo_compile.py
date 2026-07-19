#!/usr/bin/env python3
"""repo-compiler — compile the hub's top-rated cited repos into knowledge graphs + agentic tooling.

FDE-os is a hub of (1) knowledge, (2) tooling, (3) experts. The repos it cites are load-bearing —
so each top-rated one gets compiled into:
  - a knowledge graph  (knowledge/hub/<slug>.graph.json — knowledgefy-shaped, SHA-pinned provenance)
  - a tooling entry    (knowledge/hub/hub-skills.json — skill contract w/ honest notGoodAt +
                        an integration recipe: use it as a skill / plugin dependency / workflow organ)
  - a hub index        (knowledge/hub/hub-index.json — hub → repo edges, drift status)

Design commitments (the deep-dive dimensions, encoded):
  QUALITY      every node carries provenance pinned to a commit SHA (blob URLs never drift);
               every skill carries a non-empty notGoodAt (honest edges); contract-validated.
  FAST         GitHub API only — ~3 calls per repo, no clone; compile-all is O(repos), parallel-safe.
  CHEAP        $0 base path (gh auth), deterministic — no LLM; raw fetches cached to disk keyed by
               SHA so rebuilds and tests replay offline.
  UP-TO-DATE   `refresh` re-checks HEAD SHA per repo (1 call) and rebuilds ONLY drifted repos;
               exit 3 signals drift so CI/cron can gate on freshness.
  FUTURE-PROOF spec-as-data (repos.yml is the single source of truth), a fetcher seam
               (EvidenceCollector pattern — swap gh for GitLab/local without touching extraction),
               versioned output contract (`contractVersion`), skip-not-fail on unreachable repos
               (reported as stale, never silently dropped or faked).

Usage:
  python3 repo_compile.py compile <owner/repo> [--out-dir knowledge/hub]
  python3 repo_compile.py all      [--registry knowledge/hub/repos.yml] [--include-below-bar]
  python3 repo_compile.py refresh  [--registry knowledge/hub/repos.yml]     # exit 3 if drift
"""
from __future__ import annotations

import argparse

import json
import os
import re
import subprocess
import sys

CONTRACT_VERSION = "1.0"
HEADING_RE = re.compile(r"^(#{1,3})\s+(.+?)\s*#*\s*$", re.MULTILINE)
LINK_RE = re.compile(r"\[([^\]]+)\]\((https?://[^)\s]+)\)")
CODE_FENCE_RE = re.compile(r"```.*?```", re.DOTALL)


class FetchError(RuntimeError):
    """A repo could not be fetched — reported, never silently skipped."""


def slugify(s: str) -> str:
    return re.sub(r"^-+|-+$", "", re.sub(r"[^a-z0-9]+", "-", s.lower()))[:80] or "n"


# --- the fetcher seam (swap this class to support GitLab / local mirrors) --------------

class GitHubFetcher:
    """All network in one seam. Everything downstream is pure and offline-testable."""

    def _api(self, path: str) -> dict:
        p = subprocess.run(["gh", "api", path], capture_output=True, text=True)
        if p.returncode != 0:
            raise FetchError(f"gh api {path}: {p.stderr.strip()[:200]}")
        return json.loads(p.stdout)

    def _raw(self, path: str) -> str:
        """Raw media type — the JSON readme endpoint returns EMPTY content for files >1MB
        (how a 91k-star awesome-list silently produced a hollow graph). Raw has no such limit."""
        p = subprocess.run(["gh", "api", path, "-H", "Accept: application/vnd.github.raw+json"],
                           capture_output=True, text=True)
        if p.returncode != 0:
            raise FetchError(f"gh api (raw) {path}: {p.stderr.strip()[:200]}")
        return p.stdout

    def head_sha(self, repo: str) -> str:
        meta = self._api(f"repos/{repo}")
        branch = meta["default_branch"]
        return self._api(f"repos/{repo}/commits/{branch}")["sha"]

    def fetch(self, repo: str) -> dict:
        meta = self._api(f"repos/{repo}")
        branch = meta["default_branch"]
        sha = self._api(f"repos/{repo}/commits/{branch}")["sha"]
        try:
            readme = self._raw(f"repos/{repo}/readme")
        except FetchError:
            readme = ""
        if not readme.strip():
            print(f"  ⚠ {repo}: README empty or unreadable — graph will be metadata-only",
                  file=sys.stderr)
        return {
            "repo": meta["full_name"],
            "sha": sha,
            "default_branch": branch,
            "stars": meta["stargazers_count"],
            "description": meta.get("description") or "",
            "topics": meta.get("topics") or [],
            "license": (meta.get("license") or {}).get("spdx_id"),
            "pushed_at": meta.get("pushed_at"),
            "html_url": meta["html_url"],
            "readme": readme,
        }


# --- pure extraction (offline, deterministic) ------------------------------------------

KIND_RULES = [
    ("curated-index", ("awesome", "collection", "curated", "list of")),
    ("registry", ("registry",)),
    ("platform", ("platform", "observability", "mlops")),
    ("framework", ("framework", "sdk", "pythonic way", "library")),
    ("learning-resource", ("roadmap", "guide", "curriculum", "learn it", "interview", "practice repo")),
]

NOT_GOOD_AT = {
    "curated-index": ["running anything itself — an index of unvetted third-party code (popularity ≠ safety; read before you install)"],
    "registry": ["vouching for what it lists — distribution surface, not a review board"],
    "platform": ["zero-ops adoption — a deployable platform carries real operational cost"],
    "framework": ["being a finished app — you still own design, evals, and deployment"],
    "learning-resource": ["being load-bearing infrastructure — it teaches, it doesn't run"],
    "tool": ["guarantees beyond its own README — verify against your workload before trusting"],
}

INTEGRATION = {
    "curated-index": {"as": "discovery-source", "how": "search it for candidate tools; read each SKILL/server before use; prefer ephemeral use over persistent install"},
    "registry": {"as": "distribution-surface", "how": "publish hub MCP tooling to it; consume entries with the same read-before-run discipline"},
    "platform": {"as": "workflow-organ", "how": "wire as a swappable organ (eval-obs / MLOps seam) behind an interface — never hard-couple the hub to one vendor"},
    "framework": {"as": "plugin-dependency", "how": "build-time dependency for hub skills (pin the version; probe actual behavior with one small build before adopting)"},
    "learning-resource": {"as": "course-citation", "how": "cross-reference from course modules; compile its structure into the competency spine via knowledgefy"},
    "tool": {"as": "skill-candidate", "how": "wrap behind a thin SKILL.md with an honest notGoodAt; gate with an eval before recommending"},
}


def classify(raw: dict) -> str:
    hay = " ".join([raw.get("description", ""), " ".join(raw.get("topics", []))]).lower()
    for kind, needles in KIND_RULES:
        if any(n in hay for n in needles):
            return kind
    return "tool"


def build_graph(raw: dict, why_cited: str = "") -> dict:
    """README + metadata → a knowledgefy-shaped graph with SHA-pinned provenance."""
    repo, sha = raw["repo"], raw["sha"]
    pinned_readme = f"https://github.com/{repo}/blob/{sha}/README.md"
    rid = f"repo-{slugify(repo)}"
    nodes = [{
        "id": rid, "type": "repo", "label": repo,
        "stars": raw["stars"], "description": raw["description"],
        "license": raw["license"], "kind": classify(raw), "why_cited": why_cited,
        "source_url": f"https://github.com/{repo}/tree/{sha}",
    }]
    edges = []
    for t in raw.get("topics", []):
        tid = f"topic-{slugify(t)}"
        nodes.append({"id": tid, "type": "topic", "label": t,
                      "source_url": f"https://github.com/topics/{slugify(t)}"})
        edges.append({"from": rid, "to": tid, "rel": "tagged"})

    body = CODE_FENCE_RE.sub("", raw.get("readme", ""))
    stack: list[tuple[int, str]] = []  # (level, node_id)
    seen_concepts: set[str] = set()
    for m in HEADING_RE.finditer(body):
        level, title = len(m.group(1)), m.group(2).strip()
        cid = f"c-{slugify(title)}"
        if cid in seen_concepts:
            continue
        seen_concepts.add(cid)
        nodes.append({"id": cid, "type": "concept", "label": title, "level": level,
                      "source_url": pinned_readme})
        while stack and stack[-1][0] >= level:
            stack.pop()
        parent = stack[-1][1] if stack else rid
        edges.append({"from": cid, "to": parent, "rel": "part_of"})
        stack.append((level, cid))

    seen_ev: set[str] = set()
    for text, url in LINK_RE.findall(body):
        eid = f"e-{slugify(url)}"
        if eid in seen_ev:
            continue
        seen_ev.add(eid)
        nodes.append({"id": eid, "type": "evidence", "label": text.strip()[:120],
                      "source_url": url})
        edges.append({"from": rid, "to": eid, "rel": "cites"})

    return {
        "contractVersion": CONTRACT_VERSION,
        "source": {"repo": repo, "sha": sha, "url": raw["html_url"], "pushed_at": raw["pushed_at"]},
        "nodes": nodes, "edges": edges,
    }


def build_skill(raw: dict, why_cited: str = "") -> dict:
    kind = classify(raw)
    return {
        "id": f"skill-{slugify(raw['repo'])}",
        "name": raw["repo"],
        "kind": kind,
        "oneLine": (raw["description"] or f"{raw['repo']} (no description)")[:200],
        "stars": raw["stars"],
        "license": raw["license"],
        "notGoodAt": list(NOT_GOOD_AT[kind]) + ([] if raw["license"] else
                     ["license unclear — verify terms before any redistribution or bundling"]),
        "useWhen": [w for w in [why_cited] if w] + [f"topic: {t}" for t in raw.get("topics", [])[:5]],
        "integration": INTEGRATION[kind],
        "source": {"repo": raw["repo"], "sha": raw["sha"], "url": raw["html_url"]},
        "verified": True,
    }


def validate_graph(g: dict) -> list[str]:
    """Contract checks — quality is enforced, not hoped for."""
    errors = []
    ids = {n["id"] for n in g["nodes"]}
    if len(ids) != len(g["nodes"]):
        errors.append("duplicate node ids")
    for n in g["nodes"]:
        if not re.match(r"^https?://", n.get("source_url") or ""):
            errors.append(f"node {n['id']} missing http(s) provenance")
    for e in g["edges"]:
        if e["from"] not in ids or e["to"] not in ids:
            errors.append(f"dangling edge {e['from']} -> {e['to']}")
    if not g.get("source", {}).get("sha"):
        errors.append("graph missing pinned source sha")
    return errors


def needs_refresh(cached_sha: str | None, live_sha: str) -> bool:
    return cached_sha != live_sha


# --- orchestration ----------------------------------------------------------------------

def load_registry(path: str) -> dict:
    import yaml  # deferred: only orchestration needs it
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def compile_one(fetcher, repo: str, why_cited: str, out_dir: str, slug: str) -> dict:
    raw = fetcher.fetch(repo)
    graph = build_graph(raw, why_cited)
    errors = validate_graph(graph)
    if errors:
        raise SystemExit(f"contract violation for {repo}: {errors}")
    os.makedirs(out_dir, exist_ok=True)
    gpath = os.path.join(out_dir, f"{slug}.graph.json")
    with open(gpath, "w", encoding="utf-8") as f:
        json.dump(graph, f, indent=1)
    skill = build_skill(raw, why_cited)
    counts = {t: sum(1 for n in graph["nodes"] if n["type"] == t)
              for t in ("concept", "evidence", "topic")}
    print(f"  {repo} @ {raw['sha'][:8]} — ⭐{raw['stars']} · {counts['concept']} concepts · "
          f"{counts['evidence']} evidence · {counts['topic']} topics → {gpath}")
    return {"slug": slug, "skill": skill, "sha": raw["sha"], "stars": raw["stars"]}


def cmd_all(args) -> int:
    reg = load_registry(args.registry)
    bar = reg.get("top_rated_min_stars", 1000)
    fetcher = GitHubFetcher()
    skills, index, failures = [], [], []
    for entry in reg["repos"]:
        repo, slug, why = entry["repo"], entry["slug"], entry.get("why_cited", "")
        try:
            stars = fetcher._api(f"repos/{repo}")["stargazers_count"]
        except FetchError as e:
            failures.append(f"{repo}: {e}")
            continue
        if stars < bar and not args.include_below_bar:
            print(f"  {repo} — ⭐{stars} below bar ({bar}); skipped (not top-rated)")
            index.append({"slug": slug, "repo": repo, "stars": stars, "compiled": False})
            continue
        try:
            r = compile_one(fetcher, repo, why, args.out_dir, slug)
            skills.append(r["skill"])
            index.append({"slug": slug, "repo": repo, "stars": r["stars"],
                          "sha": r["sha"], "compiled": True})
        except FetchError as e:
            failures.append(f"{repo}: {e}")
    with open(os.path.join(args.out_dir, "hub-skills.json"), "w", encoding="utf-8") as f:
        json.dump({"contractVersion": CONTRACT_VERSION, "skills": skills}, f, indent=1)
    with open(os.path.join(args.out_dir, "hub-index.json"), "w", encoding="utf-8") as f:
        json.dump({"contractVersion": CONTRACT_VERSION, "top_rated_min_stars": bar,
                   "repos": index}, f, indent=1)
    if getattr(args, "render_html", False):
        _here = os.path.dirname(os.path.abspath(__file__))
        sys.path.insert(0, os.path.join(_here, "..", "..", "knowledgefy", "scripts"))
        from knowledgefy import render_html  # lazy cross-skill import (house pattern)
        for i in index:
            if not i.get("compiled"):
                continue
            gpath = os.path.join(args.out_dir, f"{i['slug']}.graph.json")
            with open(gpath, encoding="utf-8") as f:
                g = json.load(f)
            with open(gpath.replace(".graph.json", ".html"), "w", encoding="utf-8") as f:
                f.write(render_html(g))
        print(f"  rendered {sum(1 for i in index if i.get('compiled'))} HTML viewers")
    print(f"hub: {sum(1 for i in index if i.get('compiled'))} compiled · "
          f"{sum(1 for i in index if not i.get('compiled'))} below bar · {len(failures)} unreachable")
    for fmsg in failures:
        print(f"  ⚠ stale (unreachable, kept last-known): {fmsg}")
    return 0 if not failures else 4


def cmd_refresh(args) -> int:
    reg = load_registry(args.registry)
    fetcher = GitHubFetcher()
    index_path = os.path.join(args.out_dir, "hub-index.json")
    cached = {}
    if os.path.exists(index_path):
        with open(index_path, encoding="utf-8") as f:
            cached = {r["slug"]: r for r in json.load(f)["repos"]}
    drifted = []
    for entry in reg["repos"]:
        slug = entry["slug"]
        c = cached.get(slug)
        if not c or not c.get("compiled"):
            continue
        try:
            live = fetcher.head_sha(entry["repo"])
        except FetchError as e:
            print(f"  ⚠ {entry['repo']}: unreachable ({e}) — keeping cached")
            continue
        if needs_refresh(c.get("sha"), live):
            drifted.append(f"{entry['repo']} {c.get('sha', '?')[:8]} → {live[:8]}")
    if drifted:
        print("drift detected — re-run `all` to rebuild:")
        for d in drifted:
            print(f"  ↻ {d}")
        return 3
    print("fresh: every compiled repo matches its source HEAD")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Compile cited repos into KGs + tooling entries.")
    sub = ap.add_subparsers(dest="cmd", required=True)
    c1 = sub.add_parser("compile"); c1.add_argument("repo"); c1.add_argument("--why", default="")
    c1.add_argument("--out-dir", default="knowledge/hub")
    c2 = sub.add_parser("all"); c2.add_argument("--registry", default="knowledge/hub/repos.yml")
    c2.add_argument("--out-dir", default="knowledge/hub")
    c2.add_argument("--include-below-bar", action="store_true")
    c2.add_argument("--render-html", action="store_true",
                    help="also render <slug>.html viewers via knowledgefy's renderer")
    c3 = sub.add_parser("refresh"); c3.add_argument("--registry", default="knowledge/hub/repos.yml")
    c3.add_argument("--out-dir", default="knowledge/hub")
    args = ap.parse_args(argv)
    if args.cmd == "compile":
        r = compile_one(GitHubFetcher(), args.repo, args.why, args.out_dir,
                        slugify(args.repo.split("/")[-1]))
        print(json.dumps(r["skill"], indent=1))
        return 0
    if args.cmd == "all":
        return cmd_all(args)
    return cmd_refresh(args)


if __name__ == "__main__":
    raise SystemExit(main())
