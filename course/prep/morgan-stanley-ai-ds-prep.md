# Interview Prep — Morgan Stanley · AI Data Science (Snowflake-centric)

Prep for an AI data-science conversation anchored on the **Snowflake Summit 2026** material
(user-provided summary, grounded and compiled 2026-07-17). Companion artifacts:

- **Knowledge graph:** [`knowledge/snowflake-summit-2026.graph.json`](../../knowledge/snowflake-summit-2026.graph.json)
  (+ [HTML viewer](../../knowledge/snowflake-summit-2026.html)) — 16 concepts, 17 cited sources.
- **Skills (honest edges):** [`knowledge/snowflake-ds-skills.json`](../../knowledge/snowflake-ds-skills.json)
  — 8 skills, each with `notGoodAt`.
- **Vault:** [`knowledge/vault/snowflake-summit-2026/`](../../knowledge/vault/snowflake-summit-2026/).

## The one-line thesis

> *"Summit 2026's headline number is that governed context took agent accuracy from 24% to 83% —
> the model was never the lever. That's also how a bank has to run AI: identity, least privilege,
> lineage, audit, evals. I've been building exactly that layer in the open."*

The convergence is real and public: Morgan Stanley's OpenAI partnership is famously
**eval-driven** ([OpenAI case study](https://openai.com/index/morgan-stanley/)), the firm is
opening wealth management to **AI agents** ([CNBC, June 2026](https://www.cnbc.com/2026/06/03/ai-agents-morgan-stanley-wealth-management-funnel.html)),
and Snowflake+OpenAI signed a ~$200M pact to run frontier models inside the governance boundary
([OpenAI](https://openai.com/index/snowflake-partnership/)). The Summit thesis — *agentic AI needs
a governed context layer, not just compute* — is a banker's thesis wearing a data-cloud badge.

## Feature-by-feature: what to say in the room

| Feature | The one sharp sentence | The DS depth behind it |
|---|---|---|
| **Snowpark for Python** | "Move compute to the data — a laptop extract is a governance leak *and* a scale ceiling." | Lazy DataFrames compile to SQL; UDFs/UDTFs for custom logic; Snowpark pandas for the exploratory idiom. Know when NOT: GPU training loops go outside, hand back via Feature Store. |
| **Notebooks** | "EDA and production in one governed surface — no Jupyter-to-prod rewrite tax." | Git-backed, schedulable; SQL+Python cells on live data. |
| **Cortex AI** | "RAG where the data already lives — retrieval, embeddings, and text-to-SQL inside the same RBAC." | Cortex Search = hybrid retrieval; Cortex Analyst = text-to-SQL over a *semantic model* (the accuracy lever); models from OpenAI/Anthropic/Meta/Mistral under one boundary. |
| **Zero-Copy Cloning** | "Prod-scale experiment sandboxes in seconds — clone, test the pipeline, drop." | Metadata-only; time travel underneath; compute still costs — clones isolate *data*, not contention. |
| **Feature Store** | "The train/serve-skew killer: define once, backfill, serve identically to training and inference." | Feature views + Model Registry = auditable lineage raw→feature→model. The real prerequisite is feature-reuse discipline. |
| **Governance & Security (Horizon)** | "Governance as a platform property, not a wrapper — that's why regulated ML can run here at all." | RBAC, dynamic masking, row-access policies, tagging, column lineage, audit. Wire masking policies *into* the feature pipeline, not around it. |
| **Sharing & Marketplace** | "Live data without copies — vendor and counterparty data as native tables, under audit." | Market/alternative data enrichment with zero ETL; contrast with FTP-era vendor feeds. |
| **The 2026 agentic layer** | "Cortex Sense (enterprise memory) took agents from 24%→83%. Agent Identity (GA) makes every agent a principal: cryptographic identity, per-agent RBAC, audit trail." | CoWork/CoCo as surfaces; Horizon Context (preview) pulls external metadata + lineage; Adaptive Compute removes warehouse-tuning toil; Openflow/Iceberg v3/Datastream are the substrate. Flag preview-vs-GA honestly. |

## Map to receipts (theirs ↔ yours)

| Summit 2026 concept | Your public receipt |
|---|---|
| AI Agent Identity — agent as principal, per-agent RBAC, audit | [`brace`](https://github.com/wjlgatech/brace) (security controls + sign-off for autonomous agents) · portfolio-trust (signed, non-self-issuable attestations) — same thesis: **identity and attestation are the trust root, not claims** |
| Cortex Sense — enterprise memory as the accuracy lever | knowledgefy/graphify knowledge spines; anyagent's curated memory (backbone/playbooks) — **context engineering beats model swapping**, which you can argue from your own 83-vs-24-style experience |
| Eval culture (MS × OpenAI evals) | [`cli-judge`](https://github.com/wjlgatech/cli-judge) + [`rag-eval-harness`](../../skills/rag-eval-harness/SKILL.md) (deterministic retrieval metrics + grounding proxy, CI-gated) — "no evidence ⇒ No" |
| Governed retrieval (Cortex Search under RBAC) | jd-compiler's provenance-required knowledge graphs (no source URL ⇒ flagged thin, never faked) |
| Guardrails / HITL for agents touching money | anyagent cofounder: reversible→auto only after 3 unanimous human choices; irreversible = hard-stop forever |

## The honest gaps (name them before they do)

1. **Hands-on Snowflake depth.** Your receipts are platform-agnostic; none are Snowpark-native.
   Half-day artifact before the interview: free Snowflake trial → load a public dataset → one
   feature view in the Feature Store → one Cortex Search RAG query → score it with your own
   rag-eval-harness. Push it public. Now "have you used Snowpark?" → "yes — and I brought my own
   eval harness to it."
2. **Finance-domain ML.** Don't bluff Basel/model-risk-management jargon. Your bridge: the
   *evidence-gated, auditable pipeline* pattern is exactly SR 11-7 model-governance instinct
   (validation independent of development = maker ≠ checker, which you've built).
3. **Preview vs GA.** Cortex Sense/Horizon Context numbers come from vendor materials at a summit;
   say "reported 83%" — precision about evidence tiers is itself the skill they're hiring.

## Five stories (30 seconds each, all true)

1. **Eval-gated shipping** — rag-eval-harness: precision@k/MRR + grounding proxy, exits non-zero
   in CI; LLM-judge is opt-in enrichment, not the foundation. *Hook: MS's eval culture.*
2. **Agent as principal** — BRACE: rubric-as-data, evidence per source, no evidence ⇒ No, gates
   can't pass on unmeasured items. *Hook: AI Agent Identity GA, audit trails.*
3. **Context as the accuracy lever** — the jd-compiler pipeline: deterministic parse + retrieval
   grounding (every node carries provenance) beat keyword guessing; the depth came from retrieval,
   not the model. *Hook: Cortex Sense's 83-vs-24.*
4. **Earned autonomy for agents near money** — cofounder shadow mode: 🟢/🟡/🔴 routing, autonomy
   earned after 3 unanimous human choices, irreversible stays human forever. *Hook: agents in the
   wealth-management funnel.*
5. **Honest ❌ over fake ✅** — the pipeline flags a node thin when retrieval fails rather than
   inventing a definition; same discipline as refusing an unmeasured compliance pass. *Hook: little
   tolerance for unreliable outputs in a bank.*

## Likely questions → anchored answers

- **"How do you prevent train/serve skew?"** → One feature definition, two consumers: Feature
  Store feature views backfilled for training and served for inference from the same lineage;
  verify with a skew eval (population-stats diff between training batch and serving window) gated
  in CI.
- **"Design a RAG system for advisor/research documents."** → Ingestion with lineage → hybrid
  retrieval (Cortex Search or equivalent: BM25 + dense + rerank) → grounding contract (answers
  must cite retrieved spans) → dual-layer eval (retrieval precision@k/MRR separate from generation
  faithfulness) → RBAC-scoped: retrieval must respect row/column policies so the model can't leak
  what the user can't see. That last clause is the bank-grade sentence.
- **"Text-to-SQL accuracy?"** → It's a semantic-model problem, not a model problem: curated
  metric/dimension definitions (Cortex Analyst's semantic model, or your own), eval set of
  question→SQL pairs, and an abstain path — wrong SQL confidently executed is worse than no answer.
- **"How would you experiment safely on production data?"** → Zero-copy clone the schema, run the
  candidate pipeline, diff outputs, drop the clone; time travel for rollback; masking policies
  follow the clone so PII stays masked in the sandbox.
- **"Cost/latency trade-offs?"** → Adaptive Compute removes warehouse-tuning toil but not
  cost-awareness: cache embeddings, batch LLM functions, push filters before UDFs, and meter
  per-agent spend the way you'd meter per-agent permissions.

## Questions to ask them

- "Where is your agent accuracy bottleneck today — model choice, or the context/semantic layer?"
  (Their answer tells you if they've internalized the 83-vs-24 lesson.)
- "How do agents inherit entitlements — do you have per-agent identity and audit yet, or is it
  service-account inheritance?" (Agent Identity GA makes this a fair, current question.)
- "What does the eval gate look like between a model change and production — who owns it, and can
  it block?" (Maker ≠ checker probe.)
- "How much of the DS workflow lives inside the governed boundary vs. laptop extracts?" (Their
  Snowpark/Notebooks maturity, and your chance to tell story #5.)

## Pre-interview checklist

- [ ] Half-day Snowflake artifact (trial account → feature view → Cortex Search query → scored
      with rag-eval-harness) pushed public — the single highest-ROI item.
- [ ] Re-read the [skills artifact](../../knowledge/snowflake-ds-skills.json) — the `notGoodAt`
      edges are your credibility ("clones don't isolate compute contention" beats feature-list
      recitation).
- [ ] Open the [KG viewer](../../knowledge/snowflake-summit-2026.html) the morning of; rehearse
      the 83-vs-24 sentence and the five stories aloud.
- [ ] Have `brace`, `cli-judge`, and the portfolio open in tabs.
