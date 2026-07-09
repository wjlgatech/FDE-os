#!/usr/bin/env python3
"""research.py — retrieve REAL knowledge for a term, from open, keyless sources.

Turns "the JD said python" into a grounded node: a real definition + a real source, and real
relationships — by querying existing knowledge, not inventing it:
  - Wikipedia REST summary  → a real one-line definition
  - Wikidata               → the entity + real relationships (instance-of / subclass-of / part-of / uses)
  - GitHub search          → niche tools with no encyclopedia entry (MLRun, Nuclio, …)
  - ESCO                    → the EU's open skills/competences taxonomy (real skills + URIs)

Every call is best-effort with a short timeout and a graceful skip — a network failure degrades the
node, never crashes the build. stdlib only, no API keys.
"""
from __future__ import annotations

import json
import re
import urllib.parse
import urllib.request

_UA = {"User-Agent": "fde-os-research/0.1 (https://github.com/wjlgatech/FDE-os)"}
_CACHE: dict = {}


def _get(url: str, timeout: int = 8):
    if url in _CACHE:
        return _CACHE[url]
    try:
        req = urllib.request.Request(url, headers=_UA)
        with urllib.request.urlopen(req, timeout=timeout) as r:
            data = json.loads(r.read().decode("utf-8", "ignore"))
    except Exception:
        data = None
    _CACHE[url] = data
    return data


# A retrieved fact only counts if it's actually about our domain — else "ship" → a boat.
_DOMAIN_RE = re.compile(r"softwar|comput|program|machine learn|artificial intelligence|\bai\b|"
    r"data|cloud|algorithm|neural|deep learning|\bmodel|engineering|security|network|serverless|"
    r"orchestrat|proof assistant|mathematic|access control|identit|reinforcement|\bagent|container|"
    r"kubernetes|\bapi\b|\bllm\b|language model|retrieval|devops|typing|framework|platform|protocol", re.I)

def domain_ok(text: str) -> bool:
    return bool(text and _DOMAIN_RE.search(text))


def wikipedia_summary(term: str, title: str | None = None):
    d = _get("https://en.wikipedia.org/api/rest_v1/page/summary/" + urllib.parse.quote((title or term).replace(" ", "_")))
    if not d or d.get("type") == "disambiguation" or not d.get("extract"):
        return None
    return {"name": d.get("title", term), "summary": d["extract"].split(". ")[0][:220],
            "url": (d.get("content_urls", {}).get("desktop", {}) or {}).get("page", ""), "kind": "concept"}


def wikidata_entity(term: str):
    d = _get(f"https://www.wikidata.org/w/api.php?action=wbsearchentities&search={urllib.parse.quote(term)}&language=en&format=json&limit=1")
    if not d or not d.get("search"):
        return None
    e = d["search"][0]
    return {"id": e["id"], "name": e.get("label", term), "summary": (e.get("description") or "")[:220],
            "url": "https://www.wikidata.org/wiki/" + e["id"], "kind": "concept"}


_REL = {"P31": "instance of", "P279": "subclass of", "P361": "part of", "P366": "used for", "P1535": "used by"}
def wikidata_relations(qid: str, max_rel: int = 3):
    """Return real (relation, target_label) pairs — resolved to human labels."""
    out, target_ids = [], []
    d = _get(f"https://www.wikidata.org/w/api.php?action=wbgetclaims&entity={qid}&format=json")
    if not d:
        return out
    for prop, rel in _REL.items():
        for c in (d.get("claims", {}).get(prop, []) or [])[:2]:
            try:
                tid = c["mainsnak"]["datavalue"]["value"]["id"]
                target_ids.append((rel, tid))
            except Exception:
                continue
    if not target_ids:
        return out
    ids = ",".join({tid for _, tid in target_ids})
    lab = _get(f"https://www.wikidata.org/w/api.php?action=wbgetentities&ids={ids}&props=labels&languages=en&format=json")
    labels = {k: (v.get("labels", {}).get("en", {}) or {}).get("value") for k, v in (lab.get("entities", {}) if lab else {}).items()}
    for rel, tid in target_ids:
        if labels.get(tid):
            out.append((rel, labels[tid]))
        if len(out) >= max_rel:
            break
    return out


def github_repo(term: str):
    d = _get(f"https://api.github.com/search/repositories?q={urllib.parse.quote(term)}&per_page=1")
    if not d or not d.get("items"):
        return None
    it = d["items"][0]
    return {"name": it["name"], "summary": (it.get("description") or "")[:220],
            "url": it.get("html_url", ""), "kind": "tool"}


def define(term: str, title: str | None = None, trusted: bool = False):
    """Resolve a term to a grounded node. `title` = exact Wikipedia page (disambiguates, e.g.
    'Python (programming language)'). `trusted`=True skips the domain filter (curated canonical
    terms). Otherwise the retrieved fact must look domain-relevant, or it's rejected (no boats)."""
    info = wikipedia_summary(term, title) or wikidata_entity(term) or github_repo(term)
    if not info:
        return None
    if trusted or domain_ok(info["summary"]) or domain_ok(info["name"]):
        return info
    return None  # off-domain hit ("ship" → watercraft) — refuse it


def esco_skills(query: str, limit: int = 6):
    d = _get(f"https://ec.europa.eu/esco/api/search?text={urllib.parse.quote(query)}&type=skill&language=en&limit={limit}")
    res = (d.get("_embedded", {}) if d else {}).get("results", []) or []
    out = []
    for x in res:
        title = x.get("title")
        if not title:
            continue
        desc = (x.get("description", {}).get("en", {}) or {}).get("literal", "") if isinstance(x.get("description"), dict) else ""
        if not (domain_ok(title) or domain_ok(desc)):
            continue  # drop "forward auctions" / "shipment forwarders" noise
        out.append({"name": title, "uri": x.get("uri", ""), "summary": desc[:200]})
    return out


if __name__ == "__main__":  # quick manual check: research.py <term>
    import sys
    t = " ".join(sys.argv[1:]) or "role-based access control"
    print("define:", json.dumps(define(t), indent=1))
    e = wikidata_entity(t)
    if e:
        print("relations:", wikidata_relations(e["id"]))
    print("esco:", [s["name"] for s in esco_skills(t)])
