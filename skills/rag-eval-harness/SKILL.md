---
name: rag-eval-harness
description: Score a RAG or agent eval set offline and deterministically — retrieval metrics (precision@k, recall@k, MRR, hit-rate), a grounding/faithfulness proxy that flags likely hallucinations, and citation coverage — with a configurable pass/fail gate. Use to measure RAG quality instead of eyeballing it, to gate a change in CI, or to catch ungrounded answers before they ship (especially in regulated domains like healthcare). The deterministic core needs no network or API key; an LLM-judge layer is an optional add-on.
---

# rag-eval-harness

> Stop eyeballing RAG output. Score it. A change either moved a metric or it didn't.
> Principle: **evaluation is the load-bearing skill of applied AI** — if you can't measure
> grounding, you can't trust the system, and in a pharmacy/healthcare context an ungrounded answer
> is a safety event, not a bug.

## What it measures

- **Retrieval:** `precision@k`, `recall@k`, `MRR`, `hit_rate@k` — is the right context being
  retrieved, and ranked high?
- **Grounding / faithfulness (proxy):** are the answer's claims lexically supported by the retrieved
  context? Catches the common hallucination shape — an answer asserting things the context never
  said. It's an **honest proxy** (content-token overlap per sentence), not a semantic judge: a low
  score means *investigate*, not *definitely wrong*.
- **Citation coverage:** do the answer's citations actually point at retrieved chunks?

## Run it

```bash
python3 skills/rag-eval-harness/scripts/rag_eval.py score <eval_set.json> --k 5 \
  --thresholds "recall@k=0.7,grounding=0.8,precision@k=0.4"
```

With `--thresholds` it becomes a **gate** (exit 1 on any unmet floor) — drop it into CI so a
retrieval regression fails the build. See `examples/pharmacy-rag-eval.json` for the input shape.

## Eval-set shape

A JSON list; each item: `query`, `retrieved` (ranked list of `{id, text, relevant}`),
`gold_context_ids` (the full relevant set — needed for recall), `answer` (for grounding),
`citations` (optional). Metrics that lack their labels report `n/a` and never hard-fail the gate.

## Honest edges

- The grounding score is **lexical**, not semantic — paraphrase that drops shared vocabulary can
  read as ungrounded, and a hallucination that reuses context words can slip through. Use it as a
  cheap, deterministic first gate; layer an LLM judge for nuance (an opt-in hook, not in the core).
- It does not call any model — it scores a set you already produced. Generation/retrieval is your
  pipeline's job; this measures it.

## Verify

```bash
python3 -m unittest discover -s skills/rag-eval-harness/tests -p 'test_*.py'
```

17 tests: metric correctness on hand-computed fixtures, grounding on supported vs hallucinated
answers, citation coverage, the gate (block/pass/unmeasured), and determinism.

## Provenance

Built for FDE-os as the concrete tool of the CVS Agentic AI Engineer prep's deepened eval cluster
([`course/prep/lessons/rag-evaluation.md`](../../course/prep/lessons/rag-evaluation.md)). Gate shape
mirrors `true-scorer`; offline/deterministic/stdlib-only by the repo's convention.
