# Market intel — Maven "Forward Deployed Engineering Bootcamp" (reverse-engineered)

> **Source:** https://maven.com/boring-bot/ai-system-design (fetched + `anyagent reverse` 2026-07-02,
> fidelity 71/100) and the instructor's LinkedIn launch post. Instructor: Hamza Farooq
> (Traversaal.ai, ex-Google, adjunct UCLA/UMN). **This is direct market validation of FDE-os's
> premise** — their headline is literally *"Forward Deployed Engineer is the new moat in AI."*

## The blueprint (what they built)

| Dimension | Their design |
|---|---|
| Format | 4 weeks · 4 live sessions (Thu 90 min) · 4 shipped products · ~6 hrs/week async+projects |
| Price / traction | **$700**, cohort Jul 6–Aug 5 2026, "11 enrolled last week" |
| Thesis | Experiential, anti-lecture: live time = *problem identification + solution architecting*, not screen-watching |
| The gap they name | "Plenty can call an LLM API… far fewer can take an AI idea all the way to a shipped product" — the **demo→production gap** |
| Modules | 01 Ship a full-stack AI product · 02 Multimodal agentic RAG at scale · 03/04 (guardrails+evals, distributed multi-agent — inferred from outcomes list) |
| Stack | Google ADK, **A2A**, MCP, **Mem0**, **Arize**, **vLLM** (on RunPod / OpenRouter), **Llama Guard**, React, Node.js, **Neo4j** (+ semantic caching, knowledge graphs) |
| Prereqs | Python, willing full-stack (React/Node), ≥1 Docker deploy |
| Cross-promo | Optional "Claude Certified Architect – Foundations" partner certification |

## What FDE-os adopts (done in the same change)

1. **Their stack, into the taxonomy.** `jd-compiler`'s TOOLS library gained five categories the
   production-stack market speaks in — `web_stack` (React/Node/Next/FastAPI), `memory` (Mem0,
   semantic caching, Letta), `inference` (vLLM, RunPod, Ollama, SGLang, TGI, self-host),
   `guardrails` (Llama Guard, NeMo Guardrails), `graph_dbs` (Neo4j, GraphRAG, knowledge graph) —
   plus Arize/Phoenix/Langfuse/LangSmith under eval_obs, OpenRouter under providers, A2A promoted to
   protocols. **Before:** the compiler detected 3 of the 12 tools their post names. **After: 12/12**,
   and a word-boundary matcher killed the `rust`-in-"trust" / `scala`-in-"scalable" false positives
   the audit surfaced.
2. **The demo→production gap as course spine.** Their framing independently confirms the
   [regulated-engagement field note](../../docs/field-notes/2026-07-01-regulated-agentic-pipeline.md):
   the sellable skill is *surviving contact with production*, not model knowledge. FDE-os course
   modules should be sequenced as ship→ground→gate→scale (their 4-module arc is a good default).
3. **"Own the stack, not rent it."** Self-hosted inference (vLLM) as a curriculum item — cost,
   latency, data-residency — slots into the enterprise_deploy cluster and is a gap in our prep docs.

## What FDE-os deliberately does NOT adopt

- **Cohort-as-product.** Their moat is synchronous scarcity ($700 × seats); FDE-os's is
  **artifacts that gate themselves** (skills + evals, free, forkable). Complementary, not copied.
- **Stack-teaching.** Even they say "the goal isn't to teach you a stack." FDE-os stays
  provider-agnostic; named tools live in the *taxonomy* (so JDs and courses can be parsed), not as
  dependencies. Zero new imports were added by this adoption.
- **Their weakest claim, un-inherited:** "RAG that scales to millions of assets" in a 90-min live
  session is aspiration, not curriculum. FDE-os's equivalent claim must stay gated by
  `rag-eval-harness` numbers.

## Evidence trail

```
BEFORE  compile_jd(post) → tools: {a2a, mcp, react(pattern)} + false positives {rust, scala}
AFTER   compile_jd(post) → 12/12: adk, google adk, a2a, mcp, mem0, arize, vllm,
        llama guard, react, node.js, neo4j (+ semantic caching) · false positives GONE
TESTS   jd-compiler 8 → 11 (cohort-stack detection · word-boundary FP kill · stem regression)
```
