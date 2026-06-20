#!/usr/bin/env python3
"""knowledgefy — local-first, offline, deterministic: a prose research vault → knowledge spine.

The gap this fills (verified, see roadmap KTD3): `living-repo` parses only GFM tables;
`dreammaketrue`/`kgfy` needs a running engine (Neo4j). Neither does a deterministic, no-network
parse of a *prose* vault. This does, using only the structure prose actually carries:

  - Markdown heading hierarchy            -> `concept` nodes (+ `part_of` edges by nesting)
  - inline [text](url) AND bare https URLs -> `evidence` nodes (+ `cites` edges to the concept)

Edge inference beyond nesting/citation and any semantic enrichment are OUT of the deterministic
base path (they belong to an optional NIM-enrich pass, not implemented here). The base path makes
no network calls and is byte-for-byte reproducible.

Output contract (borrowed from knowledge-graph / living-repo): a normalized `*.graph.json` plus a
self-contained HTML view that works from file:// with no external scripts.

Usage:
  python3 knowledgefy.py build <vault.md | vault_dir/> --out spine.graph.json --html spine.html
"""
from __future__ import annotations

import argparse
import glob
import html
import json
import os
import re
import sys

HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*#*$")
MD_LINK_RE = re.compile(r"\[([^\]]+)\]\((https?://[^)]+)\)")
BARE_URL_RE = re.compile(r"(?<![(\"'])\bhttps?://[^\s)>\]\"'`]+")
TRAILING = ".,;:!?)]}>\"'"
CODE_FENCE_RE = re.compile(r"^```")


def slug(text: str, used: set[str]) -> str:
    base = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-") or "node"
    cand, n = base, 2
    while cand in used:
        cand, n = f"{base}-{n}", n + 1
    used.add(cand)
    return cand


def parse_file(path: str, rel: str, used_ids: set[str], nodes: list, edges: list) -> None:
    """Extract concept + evidence nodes from one markdown file. Deterministic, no I/O beyond read."""
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    # heading stack: list of (level, node_id) for part_of nesting
    stack: list[tuple[int, str]] = []
    current_concept: str | None = None
    seen_evidence: dict[str, str] = {}  # url -> evidence node id (dedupe within run)
    in_fence = False

    for line in text.splitlines():
        if CODE_FENCE_RE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue

        m = HEADING_RE.match(line)
        if m:
            level = len(m.group(1))
            title = m.group(2).strip()
            if not title:
                continue
            nid = slug(f"{rel}:{title}" if rel else title, used_ids)
            nodes.append({"id": nid, "type": "concept", "label": title,
                          "level": level, "source_file": rel})
            while stack and stack[-1][0] >= level:
                stack.pop()
            if stack:
                edges.append({"source": nid, "target": stack[-1][1], "type": "part_of"})
            stack.append((level, nid))
            current_concept = nid
            continue

        if current_concept is None:
            continue
        # citations in this line -> evidence nodes + cites edges
        for label, url in MD_LINK_RE.findall(line):
            _add_evidence(url.rstrip(TRAILING), label, current_concept, rel,
                          used_ids, nodes, edges, seen_evidence)
        # bare urls not already captured as markdown links
        line_wo_md = MD_LINK_RE.sub("", line)
        for url in BARE_URL_RE.findall(line_wo_md):
            _add_evidence(url.rstrip(TRAILING), None, current_concept, rel,
                          used_ids, nodes, edges, seen_evidence)


def _add_evidence(url, label, concept_id, rel, used_ids, nodes, edges, seen_evidence) -> None:
    if url in seen_evidence:
        eid = seen_evidence[url]
    else:
        domain = re.sub(r"^https?://(www\.)?", "", url).split("/")[0]
        eid = slug(f"ev:{domain}:{url[-12:]}", used_ids)
        seen_evidence[url] = eid
        nodes.append({"id": eid, "type": "evidence",
                      "label": label or domain, "url": url, "source_file": rel})
    # one cites edge per (concept, evidence)
    edge = {"source": concept_id, "target": eid, "type": "cites"}
    if edge not in edges:
        edges.append(edge)


def build_graph(target: str) -> dict:
    files: list[tuple[str, str]] = []  # (abspath, relname)
    if os.path.isdir(target):
        for p in sorted(glob.glob(os.path.join(target, "**", "*.md"), recursive=True)):
            files.append((p, os.path.relpath(p, target)))
    else:
        files.append((target, os.path.basename(target)))

    used_ids: set[str] = set()
    nodes: list = []
    edges: list = []
    multi = len(files) > 1
    for abspath, rel in files:
        parse_file(abspath, rel if multi else "", used_ids, nodes, edges)

    # deterministic ordering: nodes by (type, id), edges by (type, source, target)
    nodes.sort(key=lambda n: (n["type"], n["id"]))
    edges.sort(key=lambda e: (e["type"], e["source"], e["target"]))
    return {
        "schema": "knowledgefy/1",
        "source": os.path.basename(target.rstrip("/")),
        "counts": {"concepts": sum(1 for n in nodes if n["type"] == "concept"),
                   "evidence": sum(1 for n in nodes if n["type"] == "evidence"),
                   "edges": len(edges)},
        "nodes": nodes,
        "edges": edges,
    }


def render_html(graph: dict) -> str:
    """Self-contained, no external scripts. Deterministic layered layout (x by level, y by order)."""
    data = html.escape(json.dumps(graph), quote=True)
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>FDE knowledge spine</title>
<style>
  body {{ margin:0; background:#0d1117; color:#e6edf3; font:14px/1.5 system-ui,sans-serif; }}
  header {{ padding:12px 16px; border-bottom:1px solid #30363d; }}
  header b {{ color:#58a6ff; }}
  #wrap {{ display:flex; height:calc(100vh - 50px); }}
  #list {{ width:340px; overflow:auto; border-right:1px solid #30363d; padding:8px; }}
  .c {{ padding:2px 0; }} .c a {{ color:#e6edf3; text-decoration:none; cursor:pointer; }}
  .c.l1 {{ font-weight:700; color:#58a6ff; margin-top:8px; }}
  .c.l2 {{ margin-left:14px; }} .c.l3 {{ margin-left:28px; color:#9da7b3; }}
  #detail {{ flex:1; overflow:auto; padding:16px; }}
  .ev {{ display:block; color:#7ee787; text-decoration:none; font-size:13px; margin:2px 0; }}
  .pill {{ display:inline-block; font-size:11px; color:#9da7b3; border:1px solid #30363d;
           border-radius:10px; padding:0 6px; margin-left:6px; }}
</style></head>
<body>
<header><b>FDE knowledge spine</b> &middot; <span id="meta"></span></header>
<div id="wrap"><div id="list"></div><div id="detail">Select a concept.</div></div>
<script id="g" type="application/json">{data}</script>
<script>
const G = JSON.parse(document.getElementById('g').textContent);
document.getElementById('meta').textContent =
  G.counts.concepts + ' concepts &middot; ' + G.counts.evidence + ' sources';
const byId = Object.fromEntries(G.nodes.map(n => [n.id, n]));
const concepts = G.nodes.filter(n => n.type === 'concept');
const cites = G.edges.filter(e => e.type === 'cites');
const list = document.getElementById('list');
// preserve document order via level/label is lost after sort; reconstruct order by source_file then label
concepts.forEach(c => {{
  const div = document.createElement('div');
  div.className = 'c l' + Math.min(c.level, 3);
  const a = document.createElement('a');
  a.textContent = c.label;
  a.onclick = () => show(c.id);
  div.appendChild(a);
  list.appendChild(div);
}});
function show(id) {{
  const c = byId[id];
  const ev = cites.filter(e => e.source === id).map(e => byId[e.target]);
  const d = document.getElementById('detail');
  d.innerHTML = '<h2>' + c.label + '<span class="pill">level ' + c.level + '</span></h2>';
  if (!ev.length) {{ d.innerHTML += '<p>No direct sources.</p>'; return; }}
  d.innerHTML += '<p>' + ev.length + ' source(s):</p>';
  ev.forEach(e => {{
    const a = document.createElement('a');
    a.className = 'ev'; a.href = e.url; a.target = '_blank';
    a.textContent = '→ ' + (e.url || e.label);
    d.appendChild(a);
  }});
}}
</script></body></html>"""


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build")
    b.add_argument("target", help="vault file or directory")
    b.add_argument("--out", required=True, help="graph.json output path")
    b.add_argument("--html", default=None, help="HTML view output path")
    args = ap.parse_args()

    graph = build_graph(args.target)
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(graph, f, indent=2, ensure_ascii=False, sort_keys=True)
        f.write("\n")
    if args.html:
        os.makedirs(os.path.dirname(os.path.abspath(args.html)), exist_ok=True)
        with open(args.html, "w", encoding="utf-8") as fh:
            fh.write(render_html(graph))
    c = graph["counts"]
    print(f"spine: {args.out} — {c['concepts']} concepts, {c['evidence']} evidence, {c['edges']} edges")
    if args.html:
        print(f"view:  {args.html} (self-contained, works from file://)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
