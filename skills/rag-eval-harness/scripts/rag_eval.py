#!/usr/bin/env python3
"""rag-eval-harness — score a RAG/agent eval set, offline and deterministically.

Two layers (the true-scorer pattern):
  - deterministic CORE: retrieval metrics (precision@k, recall@k, MRR, hit-rate) + a grounding /
    faithfulness proxy + citation coverage. No network, byte-reproducible.
  - optional LLM-judge ENRICHMENT (a hook, not implemented here): for nuanced faithfulness you can
    layer an LLM judge on top, but the core gate runs with zero dependencies so it works in CI and
    inside a customer perimeter.

The grounding score is an HONEST PROXY: it measures whether an answer's claims are lexically
supported by the retrieved context (content-token overlap per sentence). It catches the common
hallucination shape — an answer asserting things the context never said — without pretending to be a
semantic judge. Treat a low grounding score as "investigate," not "definitely wrong."

Eval-set schema (JSON list); per item:
  {
    "query": "...",
    "retrieved": [{"id": "c1", "text": "...", "relevant": true}, ...],  # ordered best-first
    "answer": "...",                      # the generated answer (optional; needed for grounding)
    "gold_context_ids": ["c1", "c3"],     # the full set of truly-relevant ids (needed for recall)
    "citations": ["c1"]                   # ids the answer cited (optional)
  }

Usage:
  python3 rag_eval.py score eval_set.json --k 5
  python3 rag_eval.py score eval_set.json --k 5 --thresholds recall@k=0.7,grounding=0.8,precision@k=0.5
"""
from __future__ import annotations

import argparse
import json
import re
import sys

STOPWORDS = {
    "the", "a", "an", "is", "are", "was", "were", "to", "of", "and", "or", "in", "on", "for",
    "with", "as", "at", "by", "it", "this", "that", "these", "those", "be", "has", "have", "had",
    "from", "but", "not", "no", "can", "will", "would", "i", "you", "we", "they", "he", "she",
}
WORD_RE = re.compile(r"[a-z0-9]+")
SENT_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")


def _content_tokens(text: str) -> set[str]:
    return {w for w in WORD_RE.findall((text or "").lower()) if w not in STOPWORDS and len(w) > 1}


def _is_relevant(chunk: dict, gold: set[str]) -> bool:
    return bool(chunk.get("relevant")) or (chunk.get("id") in gold)


# ----------------------------------------------------------------- retrieval metrics

def precision_at_k(item: dict, k: int) -> float:
    gold = set(item.get("gold_context_ids", []))
    topk = item.get("retrieved", [])[:k]
    if not topk:
        return 0.0
    hits = sum(1 for c in topk if _is_relevant(c, gold))
    return hits / len(topk)


def recall_at_k(item: dict, k: int) -> float | None:
    gold = set(item.get("gold_context_ids", []))
    if not gold:
        return None  # recall undefined without the full relevant set
    topk_ids = {c.get("id") for c in item.get("retrieved", [])[:k]}
    return len(gold & topk_ids) / len(gold)


def mrr(item: dict) -> float:
    gold = set(item.get("gold_context_ids", []))
    for rank, c in enumerate(item.get("retrieved", []), start=1):
        if _is_relevant(c, gold):
            return 1.0 / rank
    return 0.0


def hit_rate_at_k(item: dict, k: int) -> float:
    gold = set(item.get("gold_context_ids", []))
    return 1.0 if any(_is_relevant(c, gold) for c in item.get("retrieved", [])[:k]) else 0.0


# ----------------------------------------------------------------- grounding & citations

def grounding_score(item: dict, sentence_threshold: float = 0.5) -> float:
    """Fraction of answer sentences whose content tokens are mostly present in retrieved context.
    Returns 1.0 when there is no answer to check (nothing ungrounded)."""
    answer = item.get("answer", "") or ""
    sentences = [s for s in SENT_SPLIT_RE.split(answer.strip()) if s.strip()]
    if not sentences:
        return 1.0
    context_tokens: set[str] = set()
    for c in item.get("retrieved", []):
        context_tokens |= _content_tokens(c.get("text", ""))
    grounded = 0
    for s in sentences:
        toks = _content_tokens(s)
        if not toks:
            grounded += 1  # no checkable content (e.g. "Sure!") — not a hallucination
            continue
        overlap = len(toks & context_tokens) / len(toks)
        if overlap >= sentence_threshold:
            grounded += 1
    return grounded / len(sentences)


def citation_coverage(item: dict) -> float | None:
    """Fraction of cited ids that are actually in the retrieved set. None if no citations given."""
    cites = item.get("citations")
    if not cites:
        return None
    retrieved_ids = {c.get("id") for c in item.get("retrieved", [])}
    return sum(1 for cid in cites if cid in retrieved_ids) / len(cites)


# ----------------------------------------------------------------- aggregate + gate

def evaluate(eval_set: list[dict], k: int = 5) -> dict:
    n = len(eval_set)
    if n == 0:
        return {"n": 0, "metrics": {}}
    prec = sum(precision_at_k(it, k) for it in eval_set) / n
    recs = [recall_at_k(it, k) for it in eval_set]
    rec_vals = [r for r in recs if r is not None]
    recall = (sum(rec_vals) / len(rec_vals)) if rec_vals else None
    mrr_v = sum(mrr(it) for it in eval_set) / n
    hit = sum(hit_rate_at_k(it, k) for it in eval_set) / n
    ground = sum(grounding_score(it) for it in eval_set) / n
    covs = [citation_coverage(it) for it in eval_set]
    cov_vals = [c for c in covs if c is not None]
    coverage = (sum(cov_vals) / len(cov_vals)) if cov_vals else None
    return {
        "n": n, "k": k,
        "metrics": {
            "precision@k": round(prec, 4),
            "recall@k": round(recall, 4) if recall is not None else None,
            "mrr": round(mrr_v, 4),
            "hit_rate@k": round(hit, 4),
            "grounding": round(ground, 4),
            "citation_coverage": round(coverage, 4) if coverage is not None else None,
        },
    }


def gate(metrics: dict, thresholds: dict) -> tuple[bool, list[str]]:
    """Pass iff every thresholded metric meets its floor. Skips metrics that are None (not measured)."""
    reasons: list[str] = []
    for name, floor in thresholds.items():
        val = metrics.get(name)
        if val is None:
            reasons.append(f"{name}: not measured (need labels) — cannot gate on it")
            continue
        if val < floor:
            reasons.append(f"{name}={val} < {floor}")
    hard_fail = any("<" in r for r in reasons)
    return (not hard_fail), reasons


def parse_thresholds(arg: str) -> dict:
    out = {}
    for part in arg.split(","):
        if not part.strip():
            continue
        k, _, v = part.partition("=")
        out[k.strip()] = float(v)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("score")
    s.add_argument("eval_set", help="path to a JSON eval set (list of items)")
    s.add_argument("--k", type=int, default=5)
    s.add_argument("--thresholds", default="", help="e.g. recall@k=0.7,grounding=0.8")
    args = ap.parse_args()

    try:
        with open(args.eval_set, encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"error: cannot read eval set: {exc}", file=sys.stderr)
        return 2
    if not isinstance(data, list):
        print("error: eval set must be a JSON list of items", file=sys.stderr)
        return 2

    report = evaluate(data, k=args.k)
    print(f"RAG eval — {report['n']} items, k={report.get('k')}:")
    for name, val in report["metrics"].items():
        print(f"  {name:18} {'n/a (no labels)' if val is None else val}")

    if args.thresholds:
        thresholds = parse_thresholds(args.thresholds)
        passed, reasons = gate(report["metrics"], thresholds)
        if passed:
            print("VERDICT: PASS — all thresholded metrics met.")
            return 0
        print("VERDICT: BLOCK — " + "; ".join(reasons))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
