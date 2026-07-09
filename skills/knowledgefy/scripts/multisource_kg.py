#!/usr/bin/env python3
"""multisource_kg.py — merge a knowledge graph from MULTIPLE sources into one, with every node
TAGGED by its information source, and render it as a light, interactive, source-colored graph.

Input: a knowledgefy spine graph.json (nodes already carry `source_file` — one tag per vault note).
Enrichment: for curated key concepts, RETRIEVE a real definition (research.py → Wikipedia/GitHub) and
add it as a node tagged with THAT source's URL, linked to the matching vault concept ("defines"). So
the graph connects vault-notes + the web, and each node knows where it came from.

Output: a self-contained HTML (white background) — force-directed, nodes colored by source, a legend
that filters by source, click a node to inspect its summary + source link.

    python3 multisource_kg.py <spine.graph.json> --out <graph.json> --html <view.html> --title "..."
"""
from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "jd-compiler", "scripts"))
try:
    import research
except Exception:
    research = None

# curated key concepts to ground with real, retrieved definitions (name, exact wiki title, match-keyword)
ENRICH = [
    ("MLRun", None, "mlrun"),
    ("Nuclio", None, "nuclio"),
    ("Role-based access control", "Role-based access control", "access control"),
    ("Kubernetes", "Kubernetes", "kubernetes"),
    ("OpenID Connect", "OpenID Connect", "oidc"),
    ("Identity management", "Identity management", "identity"),
    ("Open Policy Agent", "Open Policy Agent", "policy"),
]
SRC_LABEL = {
    "00-domain-map.md": "Domain map", "10-mlrun-nuclio-stack.md": "MLRun / Nuclio",
    "20-rbac-iam-foundations.md": "RBAC / IAM", "30-custom-rbac-design.md": "Custom-RBAC design",
    "40-scoping-and-portfolio-proof.md": "Scoping + proof",
}


def merge(spine: dict, offline: bool) -> dict:
    nodes, edges = [], list(spine.get("edges", []))
    by_id = {}
    for n in spine.get("nodes", []):
        src = n.get("source_file") or ("evidence" if n.get("type") == "evidence" else "vault")
        node = {"id": n["id"], "name": n.get("label", n["id"]), "type": n.get("type", "concept"),
                "source": SRC_LABEL.get(src, src), "sourceUrl": n.get("url") or "", "summary": ""}
        nodes.append(node); by_id[n["id"]] = node

    def find_vault(keyword: str):
        for nd in nodes:
            if keyword in nd["name"].lower():
                return nd["id"]
        return None

    if research and not offline:
        for name, title, kw in ENRICH:
            # wiki title given → trust the exact page; niche tool (no title) → GitHub-first,
            # then a DOMAIN-FILTERED search (so "Nuclio" can't become a Spanish astronomy centre)
            if title:
                info = research.define(name, title, trusted=True)
            else:
                info = research.github_repo(name) or research.define(name, None, trusted=False)
            if not info:
                continue
            src = "Wikipedia" if "wikipedia" in info.get("url", "") else ("GitHub" if "github" in info.get("url", "") else "Web")
            nid = "web-" + name.lower().replace(" ", "-")
            nodes.append({"id": nid, "name": info["name"], "type": "retrieved", "source": src,
                          "sourceUrl": info.get("url", ""), "summary": info.get("summary", "")})
            tgt = find_vault(kw)
            if tgt:
                edges.append({"source": nid, "target": tgt, "type": "defines"})
    counts = {}
    for nd in nodes:
        counts[nd["source"]] = counts.get(nd["source"], 0) + 1
    return {"nodes": nodes, "edges": edges, "sources": counts}


_HTML = r"""<!doctype html><html lang=en><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1"><title>__TITLE__</title>
<style>
 :root{color-scheme:light}
 *{box-sizing:border-box;margin:0} body{background:#ffffff;color:#1a1a1a;font:14px/1.5 system-ui,-apple-system,Segoe UI,Helvetica,Arial,sans-serif}
 header{padding:12px 18px;border-bottom:1px solid #e6e6e6} header b{font-size:16px}
 header span{color:#6b6b6b}
 #legend{display:flex;flex-wrap:wrap;gap:8px;padding:10px 18px;border-bottom:1px solid #eee}
 .lg{display:flex;align-items:center;gap:6px;font-size:12px;border:1px solid #e0e0e0;border-radius:999px;padding:3px 10px;cursor:pointer;user-select:none}
 .lg .sw{width:10px;height:10px;border-radius:50%} .lg.off{opacity:.35}
 #wrap{display:flex;height:calc(100vh - 92px)} #cv{flex:1;display:block}
 #ins{width:320px;border-left:1px solid #e6e6e6;padding:16px;overflow:auto}
 #ins h2{font-size:16px;margin-bottom:4px} #ins .tag{display:inline-block;font-size:11px;color:#fff;border-radius:999px;padding:1px 8px;margin:4px 0}
 #ins p{color:#333;font-size:13px;margin:8px 0} #ins a{color:#0b62d6;font-size:13px;word-break:break-all}
 .hint{color:#8a8a8a;font-size:12px}
</style></head><body>
<header><b>__TITLE__</b> &nbsp; <span id=meta></span></header>
<div id=legend></div>
<div id=wrap><canvas id=cv></canvas><div id=ins><p class=hint>Click a node to inspect it — its definition and the <b>source</b> it came from.</p></div></div>
<script id=g type=application/json>__DATA__</script>
<script>
const G=JSON.parse(document.getElementById('g').textContent);
const PALETTE=["#B0563A","#2F6F4F","#1F5FA8","#8A6D1F","#7A3E8E","#3E7C8E","#555","#A83C5B"];
const sources=[...new Set(G.nodes.map(n=>n.source))];
const color=Object.fromEntries(sources.map((s,i)=>[s,PALETTE[i%PALETTE.length]]));
const off=new Set();
document.getElementById('meta').textContent=G.nodes.length+' nodes · '+G.edges.length+' links · '+sources.length+' sources';
const legend=document.getElementById('legend');
sources.forEach(s=>{const c=G.sources[s]||0;const el=document.createElement('div');el.className='lg';
 el.innerHTML='<span class=sw style="background:'+color[s]+'"></span>'+s+' ('+c+')';
 el.onclick=()=>{el.classList.toggle('off');off.has(s)?off.delete(s):off.add(s);};legend.appendChild(el);});
const cv=document.getElementById('cv'),ctx=cv.getContext('2d');
let W,H;function size(){W=cv.width=cv.clientWidth*devicePixelRatio;H=cv.height=cv.clientHeight*devicePixelRatio;}
const idIndex=Object.fromEntries(G.nodes.map((n,i)=>[n.id,i]));
const P=G.nodes.map((n)=>({n,x:Math.random()*800-400,y:Math.random()*600-300,vx:0,vy:0}));
const E=G.edges.map(e=>[idIndex[e.source],idIndex[e.target]]).filter(([a,b])=>a!=null&&b!=null);
function step(){for(let i=0;i<P.length;i++){let p=P[i];p.vx*=.85;p.vy*=.85;p.vx-=p.x*.002;p.vy-=p.y*.002;
 for(let j=i+1;j<P.length;j++){let q=P[j],dx=p.x-q.x,dy=p.y-q.y,d2=dx*dx+dy*dy+.1,f=900/d2;p.vx+=dx*f*.01;p.vy+=dy*f*.01;q.vx-=dx*f*.01;q.vy-=dy*f*.01;}}
 for(const [a,b] of E){let p=P[a],q=P[b],dx=q.x-p.x,dy=q.y-p.y,d=Math.hypot(dx,dy)||1,f=(d-90)*.02;p.vx+=dx/d*f;p.vy+=dy/d*f;q.vx-=dx/d*f;q.vy-=dy/d*f;}
 for(const p of P){p.x+=p.vx;p.y+=p.vy;}}
let cx=0,cy=0,scale=1;
function draw(){ctx.setTransform(1,0,0,1,0,0);ctx.clearRect(0,0,W,H);ctx.save();ctx.translate(W/2,H/2);ctx.scale(devicePixelRatio*scale,devicePixelRatio*scale);ctx.translate(cx,cy);
 ctx.strokeStyle='#d7d7d7';ctx.lineWidth=1;for(const[a,b]of E){const p=P[a],q=P[b];if(off.has(p.n.source)||off.has(q.n.source))continue;ctx.beginPath();ctx.moveTo(p.x,p.y);ctx.lineTo(q.x,q.y);ctx.stroke();}
 for(const p of P){if(off.has(p.n.source))continue;const r=p.n.type==='retrieved'?7:5;ctx.beginPath();ctx.arc(p.x,p.y,r,0,7);ctx.fillStyle=color[p.n.source];ctx.fill();
  if(p.n.type==='retrieved'||p.n.type==='concept'&&p.n.name.length<26){ctx.fillStyle='#333';ctx.font='9px system-ui';ctx.fillText(p.n.name.slice(0,26),p.x+8,p.y+3);}}
 ctx.restore();}
for(let i=0;i<220;i++)step();size();(function loop(){step();draw();requestAnimationFrame(loop);})();
addEventListener('resize',size);
cv.addEventListener('click',ev=>{const rect=cv.getBoundingClientRect();const mx=(ev.clientX-rect.left-cv.clientWidth/2)/scale-cx,my=(ev.clientY-rect.top-cv.clientHeight/2)/scale-cy;
 let best=null,bd=1e9;for(const p of P){if(off.has(p.n.source))continue;const d=Math.hypot(p.x-mx,p.y-my);if(d<bd){bd=d;best=p;}}
 if(best&&bd<20){const n=best.n;const ins=document.getElementById('ins');
  ins.innerHTML='<h2>'+n.name+'</h2><span class=tag style="background:'+color[n.source]+'">'+n.source+'</span>'+
   (n.summary?'<p>'+n.summary+'</p>':'<p class=hint>'+n.type+'</p>')+
   (n.sourceUrl?'<a href="'+n.sourceUrl+'" target=_blank rel=noreferrer>source →</a>':'');}});
</script></body></html>"""


def render_html(graph: dict, title: str) -> str:
    return _HTML.replace("__TITLE__", title).replace("__DATA__", json.dumps(graph))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("spine")
    ap.add_argument("--out", required=True)
    ap.add_argument("--html", required=True)
    ap.add_argument("--title", default="Multi-source knowledge graph")
    ap.add_argument("--offline", action="store_true")
    args = ap.parse_args(argv)
    spine = json.load(open(args.spine, encoding="utf-8"))
    g = merge(spine, args.offline)
    json.dump(g, open(args.out, "w", encoding="utf-8"), indent=2)
    open(args.html, "w", encoding="utf-8").write(render_html(g, args.title))
    print(f"{len(g['nodes'])} nodes across {len(g['sources'])} sources → {args.html}")
    print("sources:", g["sources"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
