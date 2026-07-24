# Field note — the Deloitte take-home as a gap audit (2026-07-21)

**What happened:** took the Deloitte "Agentic AI Engineer" JD, derived the
realistic take-home it implies (a procurement-triage agent over fragmented,
conflicting policy docs), and built it head-to-head in `take-home/
deloitte-agentic-triage/` — term by term, stdlib-only, eval-gated. 12/12
decisions matched ground truth on the first full run; 48 new tests; repo
suite 158 → 206, both harness modes green.

The point was never the take-home. It was to use a real hiring bar to find
where our tooling is strong, where it is weak, and where a weakness converts
into an advantage competitors can't copy in a generation.

## Strengths the bar confirmed (evidence, not vibes)

- **Eval-first DNA transfers.** The field's most-reported take-home
  differentiator in 2025-26 is "ship the eval harness with the agent." That
  is this repo's default posture (every skill is a gate), which is why the
  build hit 12/12 on the first run: the ground truth was designed before the
  agent.
- **Evidence discipline scales down to a single quote.** `verify_citation`
  makes grounding checkable with grep — the same no-evidence⇒No rule as
  `outcome-contract`, applied inside the reasoning loop.
- **Deterministic-first is now defensible SOTA, not a quirk.** 2026 research:
  LLM judges carry position/verbosity bias and miss ~80% of real errors in
  production transcripts. Our stance — deterministic checks gate, judges
  advise — matches where the field landed.

## Weaknesses the bar exposed (honest ledger)

Before this build the repo had **zero** orchestration runtime, HITL
checkpoint code, memory abstraction, hybrid retrieval, or injection
hygiene — the JD's first four terms were prose, not artifacts. Now filled
stdlib-grade, but still true and stated:

- No live LLM inside the loop (a documented seam, exercised only by a
  deterministic reasoner) and no embeddings/dense retrieval (a documented
  seam, exercised only by lexical hybrid).
- No cross-session memory persistence; no OTel GenAI attribute alignment in
  traces; injection scanner is a short pattern list (the architectural
  defense — data is never instructions — is the real control).
- Interviewers ask for **LangGraph fluency specifically**. "I rebuilt its
  durable-execution semantics in ~170 lines" is a strong answer only when
  paired with fluency in the real API's names (`interrupt`, `Command`,
  checkpointer backends) — kept 1:1 in `graph.py` for exactly that reason.

## The 10X reading (three telescopes)

- **/last30days:** LangGraph 1.x made durable execution table stakes; MCP
  went Linux-Foundation-neutral; OWASP shipped an *Agentic* Top 10; judge
  reliability collapsed under measurement. The field is converging on our
  question — "how do you TRUST an agent?" — with tooling that mostly answers
  "how do you WATCH one."
- **/last30years:** every orchestration generation (BPEL → Airflow →
  Temporal → LangGraph) re-learned the same primitives: state machine +
  write-ahead log + human gate. Frameworks churn (AutoGen: 59.9k stars,
  frozen this spring); primitives persist. Building on primitives behind
  seams means we ride the churn instead of being ridden.
- **/last300years:** enterprises already run on a trust technology —
  double-entry bookkeeping. Every material action leaves two independently
  checkable records, and audit = reconciliation, performed by people who
  weren't in the room. Agent observability as practiced (traces for the
  engineer who built it) is single-entry. **The generational gap is
  audit-native agents:** every layer emits a receipt a third party can
  reconcile — verbatim quotes against a corpus, context budgets with
  include/exclude lists, guard trips, checkpoint streams, eval gates in CI.
  That's not a feature to bolt on; it's structural, in every seam. This
  repo's DNA is already double-entry. The field's isn't. That is the moat.

## Deltas shipped / queued

1. **Shipped:** `take-home/` as a repeatable pattern — a JD becomes a built,
   gated artifact, and the build doubles as a gap audit (this note).
2. **Shipped:** CI + `make check` discover `take-home/*/tests`; AGENTS.md
   maps the dir and marks `graph.py`/`tools.py`/`retrieval.py`/`memory.py`
   as candidate skill cores (promote on second consumer, per house rule).
3. **Queued (trigger: next agent build with live traces):** name trace
   attributes per OTel GenAI conventions — cheap alignment, flag their
   "Development" stability honestly.
4. **Queued (trigger: first real client corpus > ~50 docs):** dense index
   behind the `Retriever` seam, measured by `rag-eval-harness` before/after.
5. **Queued (trigger: next security review):** grow the injection corpus
   from OWASP Agentic Top 10 examples; keep the architectural control
   primary.
