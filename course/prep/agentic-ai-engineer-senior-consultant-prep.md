# Interview Prep — Agentic AI Engineer · Senior Consultant / Consultant

Interview-ready map for the [Agentic AI Engineer (Senior Consultant) JD](../target-jds/agentic-ai-engineer-senior-consultant.md):
**knowledge** (what to be able to explain) · **AI tooling** (what you've built and run) ·
**open-source receipts** (public repos that prove it). Grounded deepen artifact (retrieved
definitions + ESCO skills, not keyword guesses): [`knowledge/agentic-ai-consultant-deepen.json`](../../knowledge/agentic-ai-consultant-deepen.json).

## The one-line thesis

> *"You're hiring for the thinking layer — orchestration, retrieval, memory, evals, guardrails. I
> build exactly that layer, in the open: a governed agent engine, an MCP tool ecosystem, a
> verification-first eval harness, and a security framework for autonomous agents. Here are the
> repos."*

The JD's closing line — *"enjoys designing the machinery behind intelligent systems, not just the
interface"* — is literally the wjlgatech GitHub profile. Lead with that.

---

## The map: JD pillar → knowledge → tooling → OSS receipt

| JD pillar | What you know (say this) | Your tooling | Public receipt |
|---|---|---|---|
| **Agent architecture & orchestration** | Agent loop = model + tools + state + stopping rule; graph-vs-loop orchestration trade-offs; sub-agents; earned autonomy | `anyagent` engine (build/refine/refactor loops, cofounder shadow-mode); AgentFlow/weaver | [`loop-engineering-anything`](https://github.com/wjlgatech/loop-engineering-anything), [`company-os`](https://github.com/wjlgatech/company-os), [`flywheel`](https://github.com/wjlgatech/flywheel) |
| **Tool integration & workflow execution** | MCP as the tool standard (client/server, stdio JSON-RPC, schemas); tool-call error handling; structured outputs | fde-mcp-server (stdlib MCP server in this repo); `anyagent mcp` + `anyagent serve` (key-gated API) | [`amazing_mcp`](https://github.com/wjlgatech/amazing_mcp), [`FDE-os/skills/fde-mcp-server`](../../skills/fde-mcp-server/SKILL.md), [`CLI-Anything`](https://github.com/wjlgatech/CLI-Anything) |
| **Retrieval & grounding pipelines** | Ingest→chunk→embed→retrieve→rerank→generate; hybrid retrieval; grounding = every claim traceable to a source; graph-RAG | rag-eval-harness (this repo); knowledgefy multi-source source-tagged graphs; jd-compiler retrieval (`jd_to_deepen` grounds every node in Wikipedia/Wikidata/ESCO) | [`FDE-os/skills/rag-eval-harness`](../../skills/rag-eval-harness/SKILL.md), [`FDE-os/skills/jd-compiler`](../../skills/jd-compiler/SKILL.md), [`neuro-os`](https://github.com/wjlgatech/neuro-os) |
| **Memory & context management** | Working vs persistent memory; promotion thresholds (a lesson enters durable memory only after recurring ≥3×); token-budgeted context assembly; progressive disclosure (backbone / playbooks / bundles) | anyagent reflect loop (`~/.anyagent/backbone.md` + playbooks, anti-bloat caps); CLAUDE.md-style file memory; knowledge-graph spines as retrievable memory | [`hermes-wjl`](https://github.com/wjlgatech/hermes-wjl) ("the agent that grows with you"), [`career-os`](https://github.com/wjlgatech/career-os), knowledgefy in [`FDE-os`](https://github.com/wjlgatech/FDE-os) |
| **Evaluation & observability** | Deterministic metrics first (precision@k, MRR, grounding proxies), LLM-judge as opt-in enrichment; regression gates in CI; "no evidence ⇒ No"; traces over claims | rag-eval-harness pass/fail gate; cli-judge verification harness; sos SMARC output-quality verification + audit trails | [`cli-judge`](https://github.com/wjlgatech/cli-judge), [`sos`](https://github.com/wjlgatech/sos), [`FDE-os/skills/rag-eval-harness`](../../skills/rag-eval-harness/SKILL.md) |
| **Reliability, safety & guardrails** | Human-in-the-loop checkpoints; reversible-vs-irreversible action routing; earned autonomy (3 unanimous human choices before auto); supply-chain trust ("popularity ≠ safety") | BRACE controls as executable CI gate (`anyagent brace`); cofounder shadow mode (🟢 auto / 🟡 batch / 🔴 hard-stop); provider fallback chains so agents never die on a 429 | [`brace`](https://github.com/wjlgatech/brace), [`company-os`](https://github.com/wjlgatech/company-os) (governed runtime), portfolio-trust in [`FDE-os`](https://github.com/wjlgatech/FDE-os) |
| **Enterprise / regulated environments** | RBAC/IdM in deployment; provenance & attestation (signed, non-self-issuable vouches); PR-only main, evidence-gated ship | enterprise-rbac-mlops track in this repo; `anyagent enterprise` 7-pillar readiness scorer; attestation-gap work | [`FDE-os`](https://github.com/wjlgatech/FDE-os) (rbac-demo, readiness rubric), [`agentic-portfolio-public`](https://github.com/wjlgatech/agentic-portfolio-public) (⭐7) |

---

## The honest gap — LangGraph (JD says "especially LangGraph")

Zero LangGraph code in the portfolio today; every orchestration receipt is a **custom engine**
(anyagent, AgentFlow, flywheel) or the **Claude/MCP stack**. Two-part play:

1. **Translate, don't bluff.** Every LangGraph primitive has a 1:1 you've already built — say the
   mapping out loud:
   - `StateGraph` + typed state ↔ anyagent's `ClosedLoop` (score-carrying state threaded through stages)
   - checkpointer / persistence ↔ the reflect loop's banked memory + `resumeFromRunId`-style resume
   - `interrupt()` human-in-the-loop ↔ cofounder's 🔴 hard-stop verdicts and human-gated `publish --approve`
   - conditional edges / retries / self-correction ↔ `refactor`'s test-gated accept-or-rollback loop
   - reusable orchestration patterns ↔ backbone/playbook/bundle layering
   The strong-candidate line: *"I've built the machinery LangGraph packages, so I know **why** each
   primitive exists — the checkpointer is there because resumability breaks the moment you allow
   `Date.now()` in a node; I learned that the hard way."*
2. **Close it with one artifact before the interview** (½ day): rebuild the jd-compiler pipeline as
   a small LangGraph app — a 4-node `StateGraph` (compile → retrieve → assemble → validate) with a
   checkpointer, one conditional retry edge, and one `interrupt()` gate. Commit it public. Now the
   answer to "have you used LangGraph?" is "yes — here's the repo, and here's what my custom engine
   does that it doesn't."

Same honest note for **Pinecone/Weaviate/Milvus** (preferred, not required): your retrieval receipts
are graph-spine + deterministic-eval flavored, not managed-vector-DB flavored. Know the trade-offs
cold (managed HNSW vs local FAISS/Chroma vs pgvector; hybrid = BM25 + dense + rerank) and mention the
rag-eval-harness measures whatever backend you point it at. **LoRA/QLoRA** (preferred): FM-os is your
curated map of the post-training space — speak to when adapter tuning beats prompting/RAG (stable
domain style, latency/cost floors) even though your hands-on depth is inference-side.

---

## Six 30-second stories (STAR-shaped, all true, all citable)

1. **Self-correcting workflow with rollback** — `anyagent refactor` drives a repo toward an OOP
   quality target but only accepts a change if the project's *own discovered test command* still
   passes; regressions roll back automatically. Score trajectory is reported honestly (e.g. 62→71
   with per-step accept/rollback). *JD hook: branching, retries, self-correction.*
2. **Human-in-the-loop by design** — the cofounder subsystem records every fork the agent would
   babysit, routes reversible+calibrated ones to auto, queues the rest with a recommendation, and
   hard-stops irreversible ones forever; a decision-kind earns autonomy only after 3 unanimous human
   choices. *JD hook: HITL checkpoints, guardrails, unsafe-action prevention.*
3. **Grounded retrieval, not keyword guessing** — the jd-compiler's `jd_to_deepen` seeds terms
   deterministically, then grounds every node against Wikipedia/Wikidata/GitHub and pulls skills
   from ESCO; contract-enforced provenance (source URLs must be http(s), no dangling edges, thin
   fallback only when retrieval fails — flagged, never faked). *JD hook: grounding, traceability,
   precision.*
4. **Evaluation as a CI gate** — rag-eval-harness scores retrieval (precision@k, recall@k, MRR) plus
   a grounding/faithfulness proxy and citation coverage, deterministic and offline, exiting non-zero
   on fail so it gates CI; LLM-judge is an opt-in hook, not the foundation. cli-judge does the same
   for agent-native CLIs and MCP servers. *JD hook: automated metrics, task-based eval, both layers.*
5. **Operationalizing a safety rubric** — BRACE turns a paper security checklist into executable
   controls: rubric items encoded as data, evidence collected per source (config/telemetry/API),
   "no evidence ⇒ No," unreachable items are *not measured* (never a fake pass), blocking gates
   can't pass on unmeasured items. *JD hook: guardrails, safety controls, regulated environments.*
6. **Reliability under provider failure** — the free-LLM survival chain: probe each model's *actual*
   behavior with one curl (tool_calls? streaming shape?), verify model ids against the live catalog
   (caught a viral post shipping two wrong ids), and wire NIM → Groq/Gemini → Ollama → paid as a
   fallback chain ordered for correctness — an agent never dies on a 429. *JD hook: model providers,
   latency/cost trade-offs, failure handling, LLM behavior in practice.*

---

## Likely questions → your anchored answers

- **"Walk me through an agent you've taken to production."** → anyagent end-to-end: goal routing →
  discovered verification harness → closed loop → reflect/memory → key-gated API (`serve`) and MCP
  surface. Emphasize the *verification-is-the-only-truth* stance — honest ❌ beats fake ✅.
- **"How do you stop hallucinations reaching users?"** → layers, not one trick: grounding contract
  (every claim carries a source), deterministic faithfulness scoring in CI, guardrail that blocks
  ungrounded answers, and evidence-tiering (grounded/weak/ungrounded surfaced to the user — pain2gain
  pattern). Never "the model is usually right."
- **"How do you manage context for long-running agents?"** → three tiers: always-on backbone (capped,
  promotion threshold), situational playbooks (loaded on trigger — progressive disclosure), and
  retrievable knowledge spines (graphs). Token budget is a design input, not an afterthought.
- **"Multi-agent collaboration?"** → orchestrator-plus-specialists with deterministic control flow
  (pipeline vs barrier), adversarial-verify panels for findings, judge panels for wide solution
  spaces — and when NOT to multi-agent (cost, coordination overhead, single-context suffices).
- **"How do you evaluate retrieval vs generation separately?"** → retrieval metrics on the index
  (precision@k/MRR/hit-rate against a labeled eval set), then generation faithfulness *conditioned
  on retrieved context* (claim-support checking, citation coverage) — a system can retrieve
  perfectly and still hallucinate, so gate both.
- **"Ambiguous business process → system logic?"** → the jd-compiler story in miniature: prose in,
  deterministic taxonomy + retrieval-grounded structure out, extend-the-taxonomy flywheel as the
  domain teaches you vocabulary. Consulting-relevant: the artifact is reusable across clients.

## Questions to ask them (thinking-layer signal)

- "What does your eval story look like today — deterministic gates in CI, or human review only?"
- "When an agent action is irreversible, what's the current human-in-the-loop mechanism?"
- "How fragmented is the context — one knowledge system or many, and who owns freshness?"
- "What's the tolerance for 'not measured' — can a launch gate pass on unverified items?"

---

## Pre-interview checklist

- [ ] Build + push the LangGraph artifact (½ day, see gap section) — the single highest-ROI prep item.
- [ ] Re-run `python3 skills/jd-compiler/scripts/jd_compile.py compile course/target-jds/agentic-ai-engineer-senior-consultant.md` and skim the competency profile the morning of.
- [ ] Skim [`lessons/rag-evaluation.md`](lessons/rag-evaluation.md) — retrieval-metric definitions cold (precision@k vs MRR vs hit-rate).
- [ ] Have 3 repos open in tabs: `brace`, `cli-judge`, `agentic-portfolio-public`.
- [ ] Rehearse the six stories aloud once — 30 seconds each, end on the JD hook.
