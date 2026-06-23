# Lesson — Evaluating RAG & Agent Systems

*Cluster 3 of the [CVS Agentic AI Engineer prep](../cvs-agentic-ai-engineer-prep.md), deepened into
a full lesson. Pairs with the runnable [`rag-eval-harness`](../../../skills/rag-eval-harness/SKILL.md)
— read this, then run that on your own system.*

> **The one line to remember:** *if you can't measure whether the answer is grounded, you don't have
> a product — you have a demo that works until it doesn't.*

---

## 1. The felt problem (concrete first)

You build a RAG chatbot for a pharmacy. You ask it three questions, the answers look great, you ship.
Two weeks later it tells someone ibuprofen is safe with their blood-pressure meds. It isn't. The
model didn't "lie" — it answered confidently from context that didn't actually contain the answer,
and **nobody was measuring that.**

That gap — between *looks right* and *is grounded* — is the whole job of evaluation. A demo proves
the happy path exists. An eval proves the system is right *often enough, on the cases that matter,
and tells you the moment it stops being right.* For CVS (healthcare, HIPAA), that's not polish — an
ungrounded answer is a safety event.

## 2. The mental model — two questions, always both

Every RAG/agent answer is two steps, and each can fail independently:

```
question ──▶ [ RETRIEVE context ] ──▶ [ GENERATE answer from context ] ──▶ answer
                    │                            │
              did we fetch the            did the answer actually
              right stuff?  (retrieval)   use it?  (grounding)
```

- **Retrieval can be right, generation wrong:** the correct passage was retrieved, but the model
  ignored it and made something up. (Grounding fails.)
- **Generation can be "right," retrieval wrong:** the model answered from its own weights, not your
  data — fine until your data disagrees with its training. (Retrieval fails; you got lucky.)

So you must measure **both halves**. Measuring only end-to-end "did the answer look good" hides which
half broke — and you can't fix what you can't locate.

## 3. Measuring retrieval

Treat retrieval like search ranking. You need a small **labeled set**: for each query, which chunks
are actually relevant (`gold_context_ids`).

- **precision@k** — of the top *k* you retrieved, what fraction were relevant? (Are you feeding the
  model junk?)
- **recall@k** — of all the relevant chunks that exist, what fraction made it into the top *k*? (Are
  you *missing* the answer? This is the one that causes "I don't know" or hallucination.)
- **MRR** (mean reciprocal rank) — how high up is the *first* relevant chunk? (Rank matters: models
  weight early context more.)
- **hit_rate@k** — did *any* relevant chunk make the top *k*? (The floor: if this is low, generation
  never had a chance.)

Rule of thumb: **recall is usually the bottleneck.** If the right chunk isn't retrieved, no prompt
engineering saves you. Fix retrieval (chunking, embeddings, hybrid search, reranking) before you
touch the prompt.

## 4. Measuring grounding (faithfulness) — the hallucination catch

Grounding asks: **is every claim in the answer supported by the retrieved context?** An answer that
asserts things the context never said is a hallucination, even if it's *true* in general — because
you can't trust a system that invents, even when it invents correctly.

The cheap, deterministic proxy (what `rag-eval-harness` does): split the answer into sentences, and
for each, check whether its content words appear in the retrieved context. Mostly-present →
grounded; mostly-absent → flag it. It's lexical, so it's imperfect (paraphrase can read as
ungrounded; a hallucination reusing context words can slip through) — but it's free, runs in CI, and
needs no API key, so it's the right **first gate**. Layer an LLM judge on top for nuance once the
cheap gate is green.

> The honest framing (the FDE-os way): a proxy that you understand the failure modes of beats a
> black-box score you trust blindly. A low grounding score means *investigate*, not *condemn*.

## 5. Guardrails — eval that runs at request time, not just in CI

Evaluation offline tells you the system is good *on average*. **Guardrails** stop the specific bad
answer *right now*:

- **Grounding guardrail:** before returning, run the grounding check; if it's below a floor, refuse
  or hand off to a human ("I can't confirm that from the available sources"). In pharmacy, refusing
  beats guessing.
- **PHI/PII guardrail:** redact protected health info on the way in and out — same allow-list,
  fail-closed posture as FDE-os's own redact-at-capture design. HIPAA isn't optional here.
- **Citation enforcement:** require the answer to cite retrieved chunk ids; reject answers that cite
  nothing or cite chunks that weren't retrieved (the harness's citation-coverage metric).

The same grounding logic powers both the offline metric *and* the runtime guardrail — build it once.

## 6. Observability — close the loop in production

Offline evals use yesterday's questions. Production sees new ones. So:

- Log every query, retrieved ids, answer, and grounding score. Sample low-grounding answers into a
  review queue — they're tomorrow's eval cases. (This is the Delta Loop: field reality feeds back
  into the eval set.)
- Track the metrics over time; a drop in recall@k after a data refresh is a regression you want a
  dashboard to scream about, not a customer to discover.

## 7. Try it — the 15-minute version

1. Take any RAG system (or the example: `skills/rag-eval-harness/examples/pharmacy-rag-eval.json`).
2. Run the gate:
   ```bash
   python3 skills/rag-eval-harness/scripts/rag_eval.py score <your_eval_set.json> \
     --k 5 --thresholds "recall@k=0.7,grounding=0.8"
   ```
3. Make one change to your retriever (chunk size, k, add a reranker). Re-run. **Did a number move?**
   That's the entire discipline: change → measure → keep what helps. Now you're evaluating, not
   eyeballing.

## 8. The portfolio artifact (what this proves to CVS)

A published eval scoreboard for your RAG system + a grounding guardrail that blocks an ungrounded
answer = the single most trust-earning thing you can show for a healthcare AI role. It says: *I don't
ship what I can't measure, and I know that in this domain, "looks right" isn't good enough.*

**Next:** wire `rag-eval-harness` into your CI (it exits non-zero on a failed gate), so retrieval
quality is defended on every commit — exactly like this repo defends its own docs and tests.
