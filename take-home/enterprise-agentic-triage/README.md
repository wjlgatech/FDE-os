# Take-home: Procurement Triage Agent

A realistic Agentic AI Engineer take-home, derived term-by-term from the
a Big-Four consulting firm (name withheld) JD ("Agentic AI Engineer — Senior Consultant / Consultant") and
built head-to-head against it. Everything below runs offline, stdlib-only,
deterministically, and is gated by the repo's `make check`.

## The brief (as a candidate would receive it)

> Build an agent that triages purchase requests for a regulated enterprise.
> Policy lives in six fragmented documents with **nuanced business rules**
> (approval limits by role, vendor risk tiers, privacy addenda), **evolving
> requirements** (a v4 amendment supersedes part of v3), and **little
> tolerance for unreliable outputs**: every decision must cite the clause it
> relied on, anything above a human's authority must reach a human, and a
> prohibited vendor must never be approved. Ship the agent AND the evidence
> that it works.

**59 labeled cases** exercise the edges: the original 12 requests plus a
**47-case golden dataset** (`data/golden/`) across 11 tag families — common,
exact-dollar boundaries, vendor tiers, PII, the v3→v4 supersede, memory
windows, injection (including a benign phrase that must NOT be flagged),
invalid inputs, competitive bids, and multi-rule combos.

## Run it

```bash
python3 scripts/run.py --out runs/latest        # the original 12 → decisions + traces
python3 scripts/eval.py --run-dir runs/latest   # grade vs ground truth; exit 0/2
python3 scripts/run.py --requests data/golden/golden-requests.jsonl --out runs/golden
python3 scripts/eval.py --run-dir runs/golden --ground-truth data/golden/golden-truth.json
python3 -m unittest discover -s tests -p 'test_*.py'   # 56 tests, offline
```

Or just play with it live — the **Playground** runs the real agent behind
`/api/triage`: https://enterprise-triage-brief.vercel.app/#play

Current scoreboard (deterministic, reproduce with the commands above), on
both the 12-case set and the 47-case golden set: decision_accuracy **1.0** ·
escalation_recall **1.0** (gated at exactly 1.0) · citation_doc_coverage
**1.0** · citation_validity **1.0** · trace_completeness **1.0** → PASS, and
the golden run is a permanent CI gate (`tests/test_golden_eval.py`).

**Honest history the scoreboard earned:** the golden set's FIRST run failed
(exit 2, escalation recall 0.889) — it exposed an unimplemented policy rule
(v3 §3: competitive bids above $75k, Preferred exempt) and a crash on
vendor-less invalid requests. Both were fixed the same day, the bids
threshold parsed from retrieved policy text like every other rule. A golden
set that can't fail you isn't measuring anything.

## Head-to-head: JD term → artifact

| JD term | Artifact | What it proves |
|---|---|---|
| Stateful workflows, branching, retries, self-correction, HITL checkpoints | `scripts/graph.py` — durable-execution StateGraph: checkpoint per super-step, `interrupt_unless_resumed` + `Command(resume=...)`, per-node RetryPolicy, bounded steps; one bounded expand-retrieval loop on ungrounded decisions | LangGraph 1.x semantics rebuilt from the primitive up (~170 lines); the framework is a seam, not a load-bearing wall |
| Tool integration, safe operation in business workflows | `scripts/tools.py` — schema-validated registry, repair-friendly errors, idempotency keys, `gated` permission tier: the PO tool physically cannot fire without human approval | The 2026 tool-reliability canon (validation + idempotency + least privilege), enforced not described |
| RAG: ingestion, chunking, hybrid retrieval, reranking, contextual compression, grounding | `scripts/retrieval.py` — heading-aware chunking with line spans, BM25 + bigram rankings fused by RRF, sentence-level compression, citations whose quotes are verbatim-verifiable (`verify_citation`) | Grounding you can check with grep: an answer that can't produce a checkable quote doesn't count |
| Memory & context: conversational state, persistent memory, token-efficient assembly | `scripts/memory.py` — SessionMemory catches split purchasing (R-006 is invisible without it); ContextAssembler enforces a token budget and emits include/exclude **receipts** | Context engineering made measurable; context rot is the reason the budget exists |
| Evaluation & observability | `scripts/eval.py` + traces.jsonl — task-based eval vs labeled ground truth; safety metric (escalation_recall) gated at 1.0; every step/tool call/retrieval/context receipt/guard trip traced | The eval harness ships WITH the agent — the single most-reported take-home differentiator |
| Reliability, safety, guardrails | `scripts/guardrails.py` — input validation, instruction hygiene (free text is data, not instructions — flagged, never obeyed, never hidden), monotonic-severity hard floor that can tighten but never loosen | Defense in depth on structured facts, independent of retrieval |
| Translate ambiguous business process → robust system logic | `scripts/reasoner.py` — the model seam: every threshold parsed FROM retrieved policy text (change the corpus, the decision changes — tested); missing clause ⇒ refuses to guess | No evidence ⇒ No, applied to reasoning itself |

## Design decisions an interviewer will ask about

- **Why a deterministic reasoner behind the LLM seam?** The take-home grades
  the machinery around the model. `Reasoner.decide(request, evidence)` is
  the swap point for an LLM; with a deterministic implementation, every
  other layer is testable to ground truth, and the eval gate means a model
  swap is *measured*, not vibed. LLM judges miss most real errors and carry
  position/verbosity bias — deterministic checks gate, judges advise.
- **Why is the pause the answer?** In batch mode an escalation ends at the
  human gate on purpose: the agent's job is to know what it may not decide.
  `resume(Command(...))` continues the same checkpoint stream, and only a
  human verdict unlocks the gated PO tool.
- **Why lexical hybrid instead of embeddings?** On a six-document corpus,
  BM25+RRF is the honest baseline; `Retriever` is the seam where a dense
  index plugs in when the corpus earns one. Boring-baseline-first is the
  field's own consensus.
- **Compression vs the deterministic reasoner.** Compressed chunks and the
  budget receipt are what an LLM would see (and what the traces show); the
  deterministic reasoner reads full retrieved sections because determinism
  is cheap. An LLM behind the seam consumes the assembler's output as-is.

## Honest boundaries

No embeddings/dense retrieval, no live LLM call in the loop (seam
documented above), no cross-session persistence (SessionMemory is
in-process; the checkpoint files are the durable layer), token counts are
whitespace estimates, and the injection scanner is a pattern list — the
real defense is architectural (data-plane text is never executed), the
scanner just makes attempts visible in the audit trail.
