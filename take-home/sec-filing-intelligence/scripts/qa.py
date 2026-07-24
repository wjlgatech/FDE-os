#!/usr/bin/env python3
"""qa — the SEC filing question agent: parse → retrieve → validate → compute → answer.

Where the LLM is and isn't (the assignment's central question):
  * Arithmetic is DETERMINISTIC — Decimal, never a model. An LLM computing
    (94,827 − 97,690) / 97,690 is a hallucination waiting for scale; a growth
    rate must be exactly reproducible or the trust problem returns.
  * Value lookup is DETERMINISTIC — the facts store (facts.py) is a parsed
    coordinate system, not a similarity search.
  * The question parser here is deterministic patterns behind the same seam
    discipline as take-home #1: an LLM could replace `parse_question` for
    robustness to phrasing, and it would be promoted through the same golden
    gate — measured, not vibed.
  * Prose questions ("what did management cite as risks?") route to an
    EXTRACTIVE path: keyword-scored passages quoted verbatim with page
    citations — labeled prose, never paraphrased into confident numbers.

Refusal is a first-class outcome: unknown company, unfiled period (the
assignment's own headline example "growth between 2025 and 2026" is
unanswerable — FY2026 hasn't been filed), ambiguous metric. Every refusal
says WHY and what the corpus does hold.

The orchestration runtime is take-home #1's durable graph, imported by
repo-relative path per the repo rule: import skill cores, never re-implement.
"""
from __future__ import annotations

import importlib.util
import os
import re
from decimal import Decimal, ROUND_HALF_UP

from facts import CANONICALS, find_metric, load_facts

_HERE = os.path.dirname(os.path.abspath(__file__))
_TRIAGE = os.path.abspath(os.path.join(_HERE, "..", "..",
                                       "enterprise-agentic-triage", "scripts"))


def _load(name: str, path: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

_graph = _load("th1_graph", os.path.join(_TRIAGE, "graph.py"))
StateGraph, END = _graph.StateGraph, _graph.END

COMPANIES = {"tesla": "Tesla", "apple": "Apple"}
# Companies the assignment's example questions name but the corpus does not hold.
KNOWN_ABSENT = ["Microsoft", "Amazon", "NVIDIA", "Google", "Alphabet", "Meta", "Netflix"]

METRIC_SYNONYMS = [
    (r"total revenue|revenues?\b|net sales|top.?line", "total_revenue"),
    (r"net income attributable|attributable to common", "net_income_attributable"),
    (r"net income|profit\b|earnings\b|bottom.?line", "net_income"),
    (r"gross profit", "gross_profit"),
    (r"gross margin", "gross_margin"),
    (r"operating margin", "operating_margin"),
    (r"operating income|income from operations", "operating_income"),
    (r"operating cash flow|cash flow from operations|cash provided by operating", "operating_cash_flow"),
    (r"research and development|r&d", "research_development"),
    (r"sg&a|selling, general", "sga"),
    (r"diluted eps|earnings per share|eps\b", "diluted_eps"),
    (r"cash and cash equivalents|cash position|how much cash", "cash_and_equivalents"),
    (r"total assets", "total_assets"),
    (r"total liabilities", "total_liabilities"),
]
DERIVED = {"gross_margin": ("gross_profit", "total_revenue"),
           "operating_margin": ("operating_income", "total_revenue")}
PROSE_RE = re.compile(r"risk|management (?:said|cite|discuss)|outlook|headwind|margin pressure", re.I)

_FACTS = None
def corpus_facts():
    global _FACTS
    if _FACTS is None:
        _FACTS = load_facts()
    return _FACTS


def latest_annual_period(company: str) -> str | None:
    fys = sorted({f["period"] for f in corpus_facts()
                  if f["company"] == company and re.fullmatch(r"FY20\d\d", f["period"])})
    return fys[-1] if fys else None


def available_periods(company: str) -> list[str]:
    return sorted({f["period"] for f in corpus_facts() if f["company"] == company})


# ---- nodes ------------------------------------------------------------------

def parse_question(state: dict) -> dict:
    q = state["question"].lower()
    state["company"] = next((v for k, v in COMPANIES.items() if k in q), None)
    state["absent_company"] = next((c for c in KNOWN_ABSENT if c.lower() in q), None)
    state["metric"] = next((canon for pat, canon in METRIC_SYNONYMS if re.search(pat, q)), None)
    state["prose"] = bool(PROSE_RE.search(q)) and state["metric"] is None
    years = re.findall(r"\b(20\d\d)\b", q)
    qm = re.search(r"\bq([1-4])\s*(20\d\d)?", q)
    state["periods"] = []
    if qm:
        y = qm.group(2) or (years[0] if years else None)
        if not y and state["company"]:
            # bare "Q2" → the latest matching quarter on file for the company
            qs = sorted(p for p in available_periods(state["company"])
                        if p.startswith(f"Q{qm.group(1)}-"))
            y = qs[-1].split("-")[1] if qs else None
        if y:
            state["periods"].append(f"Q{qm.group(1)}-{y}")
    else:
        state["periods"] = [f"FY{y}" for y in years]
    state["intent"] = ("growth" if re.search(r"growth|change|increase|decrease|grow|year.over.year|yoy", q)
                       else "value")
    if re.search(r"year.over.year|yoy", q) and len(state["periods"]) == 1 and state["periods"][0].startswith("Q"):
        quarter, y = state["periods"][0].split("-")
        state["periods"].append(f"{quarter}-{int(y) - 1}")
    if "latest annual" in q or "latest filing" in q or (not state["periods"] and state["company"]):
        la = latest_annual_period(state["company"] or "")
        if la:
            state["periods"] = [la] if state["intent"] == "value" else [la, f"FY{int(la[2:]) - 1}"]
    if state["intent"] == "growth" and len(state["periods"]) == 1 and state["periods"][0].startswith("FY"):
        state["periods"].insert(0, f"FY{int(state['periods'][0][2:]) - 1}")
    # chronological order, always — "growth A→B" must mean older→newer
    def _pkey(p: str):
        m = re.search(r"(20\d\d)", p)
        return (int(m.group(1)) if m else 0, p)
    state["periods"] = sorted(dict.fromkeys(state["periods"]), key=_pkey)
    return state


def route_after_parse(state: dict) -> str:
    if state["prose"] and state["company"]:
        return "prose"
    if not state["company"] or not state["metric"]:
        return "refuse"
    return "retrieve"


def refuse(state: dict) -> dict:
    reasons = []
    if state.get("absent_company"):
        reasons.append(f"{state['absent_company']} is not in the corpus — it holds "
                       f"Tesla (10-K FY2025, 10-Q Q1/Q2 2026) and Apple (10-K FY2025). "
                       f"Adding a company = running fetch_filings.py + ingest on its filings.")
    elif not state.get("company"):
        reasons.append("No company in the corpus matched the question (corpus: Tesla, Apple).")
    if state.get("company") and not state.get("metric") and not state.get("prose"):
        reasons.append("No supported metric matched (supported: "
                       + ", ".join(sorted(CANONICALS)) + ").")
    state["answer"] = {"type": "refusal", "answer": "Cannot answer from the corpus.",
                       "reasons": reasons, "citations": [], "calc": [],
                       "confidence": "refused"}
    return state


def retrieve(state: dict) -> dict:
    metric = state["metric"]
    needed = list(DERIVED.get(metric, [metric]))
    state["operands"] = {}
    state["ambiguity"] = []
    state["missing"] = []
    for period in state["periods"]:
        for m in needed:
            hits, near = find_metric(corpus_facts(), state["company"], m, period)
            key = (m, period)
            if len({h["value"] for h in hits}) == 1:
                state["operands"][key] = hits[0]
                for n in near:
                    if n["period"] == period or n["period"] == f"AsOf-{period}":
                        state["ambiguity"].append(
                            f"'{hits[0]['label']}' answered; nearby line item "
                            f"'{n['label']}' = {n['value']:,.0f} ({period}) is a "
                            f"DIFFERENT number — disambiguated by exact label match.")
            elif len({h["value"] for h in hits}) > 1:
                state["missing"].append((m, period,
                    f"conflicting candidates {sorted({h['value'] for h in hits})} — refusing rather than guessing"))
            else:
                state["missing"].append((m, period, "not present in any filed document in the corpus"))
    return state


def route_after_retrieve(state: dict) -> str:
    return "validate" if not state["missing"] else "explain_missing"


def explain_missing(state: dict) -> dict:
    reasons = []
    for m, period, why in state["missing"]:
        r = f"{m} for {period}: {why}."
        year = period[2:] if period.startswith("FY") else None
        if year and why.startswith("not present"):
            avail = [p for p in available_periods(state["company"]) if not p.startswith("AsOf")]
            r += (f" A FY{year} annual filing does not exist yet for {state['company']} "
                  f"(latest annual: {latest_annual_period(state['company'])}; "
                  f"periods on file: {', '.join(avail)}).")
        reasons.append(r)
    state["answer"] = {"type": "refusal", "answer": "Cannot answer from filed documents.",
                       "reasons": reasons, "citations": [], "calc": [],
                       "confidence": "refused"}
    return state


def validate(state: dict) -> dict:
    ops = state["operands"].values()
    state["caveats"] = list(dict.fromkeys(state["ambiguity"]))
    scales = {f["scale"] for f in ops}
    if len(scales) > 1 and "per_share_usd" not in scales:
        state["caveats"].append(f"operands carry mixed scales {scales} — verify units.")
    docs = {f["doc_id"] for f in ops}
    if len(docs) > 1:
        state["caveats"].append(
            "operands come from different filings (" + ", ".join(sorted(docs)) +
            ") — periods aligned by label, cross-filing consistency checked by reconcile.py.")
    if any(f["form"] == "10-Q" for f in ops):
        state["caveats"].append("10-Q figures are unaudited.")
    state["caveats"].append("All figures are GAAP as filed; the corpus carries no non-GAAP reconciliations.")
    return state


def _fmt(f: dict) -> str:
    if f["scale"] == "per_share_usd":
        return f"${f['value']:.2f}"
    unit = {"millions": "M", "thousands": "K", "billions": "B"}[f["scale"]]
    return f"${f['value']:,.0f}{unit}"


def compute(state: dict) -> dict:
    metric, intent = state["metric"], state["intent"]
    ops, calc, cites = state["operands"], [], []
    for (m, period), f in sorted(ops.items(), key=lambda kv: kv[0][1]):
        calc.append(f"{m}[{period}] = {_fmt(f)}  ← '{f['label']}' {f['doc_id']} p.{f['page']}")
        cites.append({"doc_id": f["doc_id"], "page": f["page"], "line": f["line"],
                      "quote": f["quote"], "source_url": f["source_url"],
                      "period": period, "label": f["label"]})
    if metric in DERIVED:
        num_m, den_m = DERIVED[metric]
        results = []
        for period in state["periods"]:
            n, d = ops[(num_m, period)]["value"], ops[(den_m, period)]["value"]
            pct = (Decimal(str(n)) / Decimal(str(d)) * 100).quantize(Decimal("0.01"), ROUND_HALF_UP)
            calc.append(f"{metric}[{period}] = {n:,.0f} / {d:,.0f} = {pct}%")
            results.append(f"{period}: {pct}%")
        text = f"{state['company']} {metric.replace('_', ' ')}: " + "; ".join(results)
    elif intent == "growth":
        (p0, p1) = state["periods"][0], state["periods"][-1]
        a, b = ops[(metric, p0)]["value"], ops[(metric, p1)]["value"]
        delta = Decimal(str(b)) - Decimal(str(a))
        pct = (delta / Decimal(str(abs(a))) * 100).quantize(Decimal("0.01"), ROUND_HALF_UP)
        calc.append(f"growth = ({b:,.0f} − {a:,.0f}) / |{a:,.0f}| = {pct}%")
        text = (f"{state['company']} {metric.replace('_', ' ')} {p0} → {p1}: "
                f"{_fmt(ops[(metric, p0)])} → {_fmt(ops[(metric, p1)])} = {pct:+}%")
    else:
        parts = [f"{p}: {_fmt(ops[(metric, p)])}" for p in state["periods"]]
        text = f"{state['company']} {metric.replace('_', ' ')} — " + "; ".join(parts)
    state["answer"] = {"type": "numeric", "answer": text, "calc": calc,
                       "citations": cites, "reasons": state["caveats"],
                       "confidence": "high (deterministic extraction + arithmetic; "
                                     "verify any quote verbatim at the cited page)"}
    return state


def prose(state: dict) -> dict:
    q_terms = set(re.findall(r"[a-z]{4,}", state["question"].lower()))
    best = []
    for f in []:  # placeholder to keep symmetry
        pass
    import json as _json  # local, stdlib
    import glob as _glob
    docs_dir = os.path.join(os.path.dirname(_HERE), "corpus", "extracted")
    for path in sorted(_glob.glob(os.path.join(docs_dir, "*.json"))):
        doc = _json.load(open(path))
        if doc["company"].lower() != (state["company"] or "").lower():
            continue
        for page in doc["pages"]:
            text = " ".join(page["lines"])
            paras = [p.strip() for p in re.split(r"\s{4,}", text) if len(p.strip()) > 120]
            for p in paras:
                score = sum(1 for t in q_terms if t in p.lower())
                if score >= 2:
                    best.append((score, doc["doc_id"], page["page"], p[:400], doc["source_url"]))
    best.sort(key=lambda t: -t[0])
    top = best[:3]
    if not top:
        state["answer"] = {"type": "refusal", "answer": "No relevant prose found in the corpus.",
                           "reasons": ["prose retrieval found no passage scoring ≥2 query terms"],
                           "citations": [], "calc": [], "confidence": "refused"}
        return state
    state["answer"] = {
        "type": "prose",
        "answer": "Extractive passages (verbatim, not paraphrased):\n" +
                  "\n---\n".join(f"[{d} p.{pg}] {t}…" for _, d, pg, t, _ in top),
        "calc": [],
        "citations": [{"doc_id": d, "page": pg, "quote": t[:200], "source_url": u}
                      for _, d, pg, t, u in top],
        "reasons": ["Prose answers are EXTRACTIVE quotes with page cites — an LLM "
                    "summarization seam could sit here, promoted via the golden gate."],
        "confidence": "extractive (quotes verbatim; interpretation left to the reader)"}
    return state


def build_agent() -> StateGraph:
    g = StateGraph(entry="parse")
    g.add_node("parse", parse_question)
    g.add_conditional_edges("parse", route_after_parse)
    g.add_node("refuse", refuse)
    g.add_edge("refuse", END)
    g.add_node("prose", prose)
    g.add_edge("prose", END)
    g.add_node("retrieve", retrieve)
    g.add_conditional_edges("retrieve", route_after_retrieve)
    g.add_node("explain_missing", explain_missing)
    g.add_edge("explain_missing", END)
    g.add_node("validate", validate)
    g.add_edge("validate", "compute")
    g.add_node("compute", compute)
    g.add_edge("compute", END)
    return g


def ask(question: str, tracer=None) -> dict:
    out = build_agent().run({"question": question}, tracer=tracer)
    return out["state"]["answer"]


if __name__ == "__main__":
    import json
    import sys
    q = " ".join(sys.argv[1:]) or "What was Apple's total revenue in 2025?"
    print(json.dumps(ask(q), indent=2))
