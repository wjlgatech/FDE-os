# Prep Curriculum — CVS Health Agentic AI Engineer (Senior)

A JD-validated study plan for the [CVS Agentic AI Engineer role](../target-jds/cvs-agentic-ai-engineer.md).
**Validation question:** *would someone who finishes this be ready to land the role?*

Same dual-tier shape as the [Reflection AI prep](reflection-ai-fde-prep.md) (the FDE-os TRUE model):
every cluster ships 📘 **Learn** (human knowledge) + 🛠️ **Tool** (a forkable agent asset you build &
keep) + ✅ **Prove** (a JD-anchored gate). Building the tool *is* the deepest way to learn it, and the
tools become the portfolio that gets you hired.

This role is senior + applied-AI-deep, so the bar is **production-grade**, not demos. Two things are
non-negotiable for this JD: a real **Claude MCP integration** (Cluster 1) and a real **eval/guardrails**
story (Cluster 3 — deepened into full lessons + a runnable tool, see below).

Suggested order: 4 (SWE foundation) → 1 (agents) → 2 (RAG) → 3 (eval) → 5 (cloud/devops) → 6 (domain).

---

## Cluster 1 — Agentic systems & orchestration

*JD anchor: "agents capable of reasoning, planning, tool usage, memory, multi-step execution" ·
"LangChain, LangGraph, CrewAI, AutoGen, Semantic Kernel" · "1+ Claude MCP integrations."*

- 📘 **Learn:** agent loops, planning/ReAct, tool-use, memory, multi-step orchestration; build the
  *same* agent in two frameworks (e.g. LangGraph + CrewAI) to feel the trade-offs; multi-agent
  patterns; **the Model Context Protocol** (what an MCP server/client is, why it standardizes tools).
- 🛠️ **Tool:** **build a real Claude MCP server** exposing one enterprise capability (a DB query, a
  knowledge lookup, a ticket action) — this directly satisfies the JD's hard "1+ Claude MCP
  integrations" requirement *and* is a portfolio centerpiece. (Field Kit menu: MCP server spec;
  scaffold the convention with [`field-kit-generator`](../../skills/field-kit-generator/SKILL.md).)
- ✅ **Prove:** a working multi-step agent using your MCP server across ≥2 tools, with a memory story.

## Cluster 2 — RAG & retrieval

*JD anchor: "RAG pipelines integrating vector databases and enterprise knowledge systems" ·
"Pinecone, Weaviate, FAISS, ChromaDB" · "semantic search."*

- 📘 **Learn:** chunking strategies, embeddings, the retrieve→rerank→generate pipeline, ≥2 vector DBs
  (one managed e.g. Pinecone, one local e.g. FAISS/Chroma), hybrid + semantic search, and the
  enterprise-knowledge integration reality (messy docs, access, freshness).
- 🛠️ **Tool:** a reusable **RAG pipeline harness** (ingest → index → query) you can point at any
  corpus; pair it with the eval-harness from Cluster 3 so retrieval quality is measured, not assumed.
- ✅ **Prove:** a RAG system over a real corpus with a published retrieval-quality scoreboard.

## Cluster 3 — Applied-AI eval, guardrails & observability  ⭐ deepened

*JD anchor: "evaluation pipelines, guardrails, and AI safety mechanisms" · "AI observability,
monitoring, hallucination detection, and performance optimization."*

This is the cluster most likely to separate strong candidates, and CVS (healthcare/HIPAA) weights it
heavily — a hallucination in pharmacy context is a safety event, not a bug. **Deepened into full
lessons + a concrete runnable tool:**

- 📘 **Learn:** [`lessons/rag-evaluation.md`](lessons/rag-evaluation.md) — a full concept-first lesson
  on evaluating RAG/agent systems (retrieval metrics, grounding/faithfulness, hallucination
  detection, guardrails, the offline eval set, regression gating, observability in prod).
- 🛠️ **Tool:** **[`rag-eval-harness`](../../skills/rag-eval-harness/SKILL.md)** — a real, runnable,
  offline, deterministic skill (Python + tests) that scores a RAG eval set: retrieval metrics
  (precision@k, recall@k, MRR, hit-rate) + a grounding/faithfulness proxy (are the answer's claims
  supported by retrieved context?) + citation coverage, with a pass/fail **gate** (the true-scorer
  pattern). Optional LLM-judge enrichment is an opt-in hook; the deterministic core needs no network.
- ✅ **Prove:** run `rag-eval-harness` on your Cluster-2 system; show a before/after where a change
  moved a metric; add a guardrail that blocks an ungrounded answer.

## Cluster 4 — Production SWE & platform

*JD anchor: "scalable backend services and APIs using Python, Java, Node.js, or Go" · "FastAPI,
Flask, Spring Boot, Node.js" · "microservices · REST APIs, distributed systems, scalable backend."*

- 📘 **Learn:** ship a production-grade service in **Python** + one of (Java/Go/TS); REST design,
  async, error handling, testing, design patterns, scalability, observability. Senior bar: own it
  end-to-end with long-term-scalable decisions.
- 🛠️ **Tool:** a **test/CI + pre-push hook stack** that gates your repos (fork this repo's
  [`tests.yml`](../../.github/workflows/tests.yml)) + a code-review skill that runs your suite.
- ✅ **Prove:** a deployed, tested, observable service; a stranger can run it from the README.

## Cluster 5 — Cloud-native & DevOps

*JD anchor: "AWS, Azure, or GCP" · "Docker and Kubernetes" · "CI/CD pipelines, testing frameworks,
and infrastructure-as-code (Terraform)."*

- 📘 **Learn:** containerize + orchestrate (Docker → K8s), IaC (Terraform), CI/CD (GitHub
  Actions/Jenkins), secrets, monitoring/observability. Pick one cloud deeply (the JD needs one).
- 🛠️ **Tool:** a **deployment-preflight checklist** agent skill/SOP (perimeter, secrets, rollback,
  monitoring) — scaffold with `field-kit-generator`; doubles for any enterprise deploy.
- ✅ **Prove:** the Cluster-4 service deployed via container + IaC + CI to one cloud, with monitoring.

## Cluster 6 — Domain, governance & leadership

*JD anchor: "healthcare, retail, insurance, or pharmacy" · "AI governance, responsible AI, enterprise
security" · "HIPAA" · "Mentor junior engineers · enterprise AI strategy."*

- 📘 **Learn:** HIPAA + regulated-AI basics, responsible-AI / governance frameworks, enterprise
  security (PII/PHI handling — connects to FDE-os's own redact-at-capture posture), and the senior
  soft skills: architecture reviews, mentoring, influencing direction.
- 🛠️ **Tool:** a **PHI/PII guardrail** check (an allow-list redaction pass over agent inputs/outputs —
  reuse the pattern from the roadmap's U12 redact-at-capture design) so your agent is HIPAA-aware.
- ✅ **Prove:** a written architecture-review doc for one of your systems + a working PHI guardrail.

## ➕ The FDE differentiator (optional, but it's what FDE-os is for)

This JD doesn't require the forward-deployed craft — but adding it makes you rare. Run the
[Delta Discovery Protocol](../../field-kits/delta-discovery-protocol/SKILL.md) and the
[agentic-solution-architect](tools/agentic-solution-architect/SKILL.md) on a real problem: you'll be
the Agentic AI Engineer who can *also* sit with the business stakeholders, find the real problem, and
architect the smallest first build — exactly the "collaborate with stakeholders / enterprise AI
strategy" line, done at FDE level.

---

## Readiness gate (eval-as-gate)

Self-score each cluster 0–3 (same rubric as the Reflection prep). **Apply when total ≥ 13/18 AND no
cluster below 2 AND the two JD hard-gates are met:** a real **Claude MCP integration** (Cluster 1)
and a real **eval/guardrails** artifact (Cluster 3). Senior role → the bar is "shipped + owned
end-to-end," not "built a demo."

## Your portfolio (the by-product that gets you hired)

A Claude MCP server, a multi-tool agent, a RAG system + an eval scoreboard, a deployed cloud-native
service (container + IaC + CI + monitoring), a PHI guardrail, and an architecture-review doc — plus
the agent tools you built for each. For a healthcare AI role, the eval + guardrail artifacts are the
ones that earn trust.
