#!/usr/bin/env python3
"""snowflake-os · graph — compile the catalogue into a navigable knowledge spine.

Pure stdlib, offline, deterministic (stable ids, sorted nodes and edges — the
same snapshot always produces a byte-identical graph, so it diffs cleanly).

    python3 snowflake-os/scripts/graph.py build \
        --out knowledge/snowflake-catalog.graph.json \
        --html knowledge/snowflake-catalog.html

Node types: role · competency · course · exam · track
Edge types: requires (role→competency, tiered) · builds (competency→course,
            carrying its basis) · certifies (competency→exam) · sequences
            (track→course, carrying the published ordinal)

Every course node keeps its provenance URL, so any claim in the graph can be
clicked back to the Snowflake page it came from.
"""
from __future__ import annotations

import argparse
import html as html_mod
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from catalog import Catalog  # noqa: E402


def build_graph(cat: Catalog) -> dict:
    nodes: list[dict] = []
    edges: list[dict] = []

    for role, spec in cat.roles.items():
        nodes.append({
            "id": f"role:{role}",
            "type": "role",
            "label": cat.roles_upstream.get(role, {}).get("title") or role.replace("-", " ").title(),
            "upstream": role in cat.roles_upstream,
        })
        for tier in ("core", "supporting"):
            for cid in spec.get(tier, []):
                edges.append({"source": f"role:{role}", "target": f"comp:{cid}",
                              "type": "requires", "tier": tier})

    for cid, comp in cat.competencies.items():
        units = cat.requirement_units(cid)
        nodes.append({
            "id": f"comp:{cid}",
            "type": "competency",
            "label": comp["name"],
            "why": comp["why"],
            "required_hours": round(sum(u["hours"] for u in units), 2),
        })
        for m in comp["courses"]:
            if m["code"] in cat.courses:
                edges.append({"source": f"comp:{cid}", "target": f"course:{m['code']}",
                              "type": "builds", "basis": m["basis"]})
        for e in comp["exams"]:
            if e["code"] in cat.exams:
                edges.append({"source": f"comp:{cid}", "target": f"exam:{e['code']}",
                              "type": "certifies", "basis": e["basis"]})

    for code, c in cat.courses.items():
        nodes.append({
            "id": f"course:{code}",
            "type": "course",
            "label": c["title"],
            "code": code,
            "hours": c["effort_hours"],
            "difficulty": c["difficulty"],
            "free": c["free"],
            "delivery": c["delivery"],
            "url": c["provenance"]["url"],
        })

    for code, e in cat.exams.items():
        nodes.append({
            "id": f"exam:{code}",
            "type": "exam",
            "label": e["title"],
            "code": code,
            "tier": e["tier"],
            "cost_usd": e["exam_cost_usd"],
            "cost_measured": e["exam_cost_measured"],
            "objectives": e["tests"],
            "url": e["provenance"]["url"],
        })

    for slug, t in cat.tracks.items():
        nodes.append({
            "id": f"track:{slug}",
            "type": "track",
            "label": t["title"],
            "published": t["sequence_published"],
            "url": t["provenance"]["url"],
        })
        for i, code in enumerate(t["sequence"], 1):
            if code in cat.courses:
                edges.append({"source": f"track:{slug}", "target": f"course:{code}",
                              "type": "sequences", "ordinal": i})

    nodes.sort(key=lambda n: (n["type"], n["id"]))
    edges.sort(key=lambda e: (e["type"], e["source"], e["target"]))
    counts = {t: sum(1 for n in nodes if n["type"] == t)
              for t in ("role", "competency", "course", "exam", "track")}
    counts["edges"] = len(edges)
    return {
        "schema": "snowflake-os/graph@1",
        "source": {
            "catalogue": cat.raw["source"]["origin"],
            "fetched_at": cat.raw["source"]["fetched_at"],
            "competency_spec": cat.spec["source"]["file"],
            "built_by": "snowflake-os/scripts/graph.py",
        },
        "counts": counts,
        "nodes": nodes,
        "edges": edges,
    }


_CSS = """<style>
  /* Light by default. Never a dark background. */
  :root { color-scheme: light;
    --paper:#faf9f5; --card:#ffffff; --ink:#141413; --muted:#6b6a63;
    --line:#e3e0d6; --accent:#d97757; --blue:#6a9bcc; --green:#788c5d; }
  * { box-sizing:border-box; }
  body { margin:0; background:var(--paper); color:var(--ink);
         font:14px/1.55 system-ui,-apple-system,"Segoe UI",sans-serif; }
  header { padding:14px 20px; border-bottom:1px solid var(--line); background:var(--card); }
  header b { font-size:16px; } header span { color:var(--muted); }
  #wrap { display:flex; height:calc(100vh - 56px); }
  #side { width:330px; overflow:auto; border-right:1px solid var(--line);
          padding:12px; background:var(--card); }
  #detail { flex:1; overflow:auto; padding:22px 26px; }
  h3 { margin:16px 0 6px; font-size:11px; letter-spacing:.09em; text-transform:uppercase;
       color:var(--muted); }
  .item { padding:5px 8px; border-radius:6px; cursor:pointer; }
  .item:hover { background:var(--paper); }
  .item.on { background:var(--accent); color:#fff; }
  .pill { display:inline-block; font-size:11px; border:1px solid var(--line);
          border-radius:10px; padding:1px 8px; margin-right:6px; color:var(--muted); }
  .pill.core { border-color:var(--accent); color:var(--accent); }
  .pill.curated { border-color:var(--blue); color:var(--blue); }
  .pill.free { border-color:var(--green); color:var(--green); }
  table { border-collapse:collapse; width:100%; margin-top:10px; }
  th,td { text-align:left; padding:7px 10px; border-bottom:1px solid var(--line); font-size:13px; }
  th { color:var(--muted); font-weight:600; font-size:11px; text-transform:uppercase;
       letter-spacing:.07em; }
  a { color:var(--accent); }
  .why { color:var(--muted); font-style:italic; margin:4px 0 12px; }
  .note { background:var(--card); border:1px solid var(--line); border-left:3px solid var(--blue);
          padding:10px 14px; border-radius:4px; margin-top:16px; color:var(--muted); font-size:13px; }
</style>"""


def render_html(g: dict) -> str:
    # Embed the graph in <script type="application/json">. Do NOT html-escape it:
    # a browser does not decode HTML entities inside a script element, so
    # `&quot;` would reach JSON.parse literally and throw — leaving the const in
    # its temporal dead zone and rendering a blank page with no console error to
    # explain it. The only sequence that must be neutralised is `</`, which would
    # otherwise close the script tag early.
    data = json.dumps(g, ensure_ascii=False).replace("</", "<\\/")
    c = g["counts"]
    subtitle = (f"{c['course']} courses &middot; {c['competency']} competencies &middot; "
                f"{c['exam']} exams &middot; {c['role']} roles &middot; {c['edges']} edges")
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Snowflake catalogue knowledge spine &middot; snowflake-os</title>
{_CSS}</head>
<body>
<header><b>Snowflake catalogue knowledge spine</b> &middot; <span>{subtitle}</span></header>
<div id="wrap"><div id="side"></div><div id="detail"></div></div>
<script id="g" type="application/json">{data}</script>
<script>
const G = JSON.parse(document.getElementById('g').textContent);
const byId = Object.fromEntries(G.nodes.map(n => [n.id, n]));
const out = e => G.edges.filter(x => x.source === e);
const side = document.getElementById('side'), detail = document.getElementById('detail');
const esc = s => String(s == null ? '' : s).replace(/[&<>"]/g, m =>
  ({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}}[m]));

function section(title, nodes) {{
  const h = document.createElement('h3'); h.textContent = title; side.appendChild(h);
  nodes.forEach(n => {{
    const d = document.createElement('div');
    d.className = 'item'; d.textContent = n.label; d.dataset.id = n.id;
    d.onclick = () => show(n.id);
    side.appendChild(d);
  }});
}}
section('Roles', G.nodes.filter(n => n.type === 'role'));
section('Competencies', G.nodes.filter(n => n.type === 'competency'));
section('Exams', G.nodes.filter(n => n.type === 'exam'));

function show(id) {{
  document.querySelectorAll('.item').forEach(e => e.classList.toggle('on', e.dataset.id === id));
  const n = byId[id];
  let h = '<h2>' + esc(n.label) + '</h2>';
  if (n.why) h += '<div class="why">' + esc(n.why) + '</div>';

  if (n.type === 'role') {{
    if (!n.upstream) h += '<span class="pill">FDE-os role, not one of Snowflake\\'s twelve</span>';
    ['core','supporting'].forEach(tier => {{
      const es = out(id).filter(e => e.tier === tier);
      if (!es.length) return;
      h += '<h3>' + tier + '</h3><table><tr><th>Competency</th><th>Required</th></tr>';
      es.forEach(e => {{ const c = byId[e.target];
        h += '<tr><td><a onclick="show(\\'' + c.id + '\\')" style="cursor:pointer">' +
             esc(c.label) + '</a></td><td>' + c.required_hours + 'h</td></tr>'; }});
      h += '</table>';
    }});
  }}

  if (n.type === 'competency') {{
    h += '<p><b>' + n.required_hours + 'h</b> required (alternatives collapsed)</p>';
    const cs = out(id).filter(e => e.type === 'builds');
    h += '<table><tr><th>Course</th><th>Hours</th><th>Cost</th><th>Basis</th></tr>';
    cs.forEach(e => {{ const c = byId[e.target];
      h += '<tr><td><a href="' + c.url + '" target="_blank">' + esc(c.code) + '</a> ' +
           esc(c.label) + '</td><td>' + (c.hours == null ? 'not measured' : c.hours + 'h') +
           '</td><td>' + (c.free ? '<span class="pill free">free</span>' : 'paid') + '</td><td>' +
           (e.basis === 'curated' ? '<span class="pill curated">curated</span>' : esc(e.basis)) +
           '</td></tr>'; }});
    h += '</table>';
    const ex = out(id).filter(e => e.type === 'certifies');
    if (ex.length) {{
      h += '<h3>Certifies</h3>';
      ex.forEach(e => {{ const x = byId[e.target];
        h += '<div><a onclick="show(\\'' + x.id + '\\')" style="cursor:pointer">' +
             esc(x.label) + '</a></div>'; }});
    }}
  }}

  if (n.type === 'exam') {{
    h += '<p><span class="pill">' + esc(n.tier) + '</span>' +
         (n.cost_measured ? '<span class="pill">$' + n.cost_usd + '</span>'
                          : '<span class="pill">cost not published</span>') + '</p>';
    if (n.objectives && n.objectives.length) {{
      h += '<h3>Published objectives</h3><ul>';
      n.objectives.forEach(o => h += '<li>' + esc(o) + '</li>');
      h += '</ul>';
    }} else {{
      h += '<div class="note">No objectives parsed &mdash; this is a localised exam page. ' +
           'Recorded as <b>not measured</b> rather than copied from the English page.</div>';
    }}
    h += '<p><a href="' + n.url + '" target="_blank">source &rarr;</a></p>';
  }}

  h += '<div class="note">Every course and exam links to the Snowflake page it was parsed from, ' +
       'captured ' + esc(G.source.fetched_at) + '. Mappings marked <b>curated</b> are snowflake-os ' +
       'judgment; Snowflake publishes no role&rarr;course mapping of its own.</div>';
  detail.innerHTML = h;
}}
show(G.nodes.find(n => n.type === 'role' && n.id.includes('forward-deployed')).id);
</script></body></html>"""


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build")
    b.add_argument("--out", required=True)
    b.add_argument("--html")
    args = p.parse_args(argv)

    g = build_graph(Catalog())
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(g, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    msg = f"graph: {out}"
    if args.html:
        Path(args.html).write_text(render_html(g), encoding="utf-8")
        msg += f"\nhtml:  {args.html}"
    c = g["counts"]
    print(f"{msg}\n  {c['role']} roles · {c['competency']} competencies · {c['course']} courses · "
          f"{c['exam']} exams · {c['track']} tracks · {c['edges']} edges")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
