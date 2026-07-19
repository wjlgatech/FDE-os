# Target JD — Agentic AI Engineer · Senior Consultant / Consultant

**Source:** provided by user (posting text pasted 2026-07-17; consulting-firm "Work You'll Do / The Team" format — no public URL supplied).
**Level:** Senior Consultant / Consultant.

## Honest framing — the "thinking layer" role

Explicitly *not* a prompt-only role: the spine is the reasoning / orchestration / retrieval /
memory / control layers of LLM systems under enterprise constraints. Heaviest named-tool signal:
**LangGraph** (called out twice, "especially LangGraph"). Closest sibling in this vault:
[`cvs-agentic-ai-engineer.md`](cvs-agentic-ai-engineer.md) (Senior SWE flavor); this one is the
consulting flavor of the same competency core.

## Work You'll Do

Design, build, and operationalize LLM-powered systems capable of reasoning, planning, retrieving
information, using tools, and executing multi-step workflows reliably at scale — the "thinking
layer":

- Agent architecture and orchestration
- Tool integration and workflow execution
- Retrieval and grounding pipelines
- Memory and context management
- Evaluation and observability
- Reliability, safety, and guardrails

Transform complex domain knowledge into production-grade AI behavior, with a strong emphasis on
precision, traceability, maintainability, and operational robustness.

## Key Responsibilities

- Design and implement agentic AI systems capable of multi-step reasoning, planning, tool use, and
  workflow execution.
- Build stateful workflows using frameworks such as **LangGraph** and **LangChain**, including
  branching, retries, self-correction, human-in-the-loop checkpoints, and reusable orchestration
  patterns.
- Develop and integrate **Retrieval-Augmented Generation (RAG)** pipelines: ingestion, chunking,
  embeddings, vector and hybrid retrieval, reranking, contextual compression, grounding strategies.
- Engineer **memory and context management**: conversational state, persistent memory,
  retrieval-aware context assembly, token-efficient context engineering.
- Build integrations with internal/external tools, APIs, enterprise systems, databases, and model
  providers so agents operate safely within real business workflows.
- Contribute to context delivery and model interaction patterns (how AI systems discover, retrieve,
  and use relevant information).
- Evaluate system quality across retrieval **and** generation layers: automated metrics, human
  review, task-based evaluation frameworks.
- Implement **observability** for prompts, tool calls, retrieval quality, agent traces, failures,
  drift, latency, production behavior.
- Apply **guardrails**, safety controls, and failure handling to reduce hallucinations and unsafe
  actions.
- Stay current on LLMs, agentic systems, evaluation methodologies, and context engineering;
  translate research into practical engineering decisions.

## Required Qualifications

- Bachelor's in CS / Engineering / Data Science / Computational Linguistics or related.
- Hands-on **production-grade LLM applications**: prompt engineering, tool use, structured outputs,
  error handling, model behavior tuning.
- Strong **LangChain** and *especially* **LangGraph** experience for orchestrating complex LLM
  workflows and agent behavior.
- End-to-end **RAG** design and optimization: indexing, retrieval, reranking, grounding, evaluation.
- Strong understanding of **memory and context management**: context windows, retrieval-driven
  context assembly, persistent memory, high-signal context selection.
- Deep understanding of **LLM behavior in practice**: strengths, limitations, hallucination risks,
  reasoning constraints, latency/cost trade-offs, evaluation methods.
- Strong **Python** engineering; testing, CI/CD, version control, API integration.
- **Observability, tracing, and debugging** for LLM systems in production.
- Translate ambiguous, high-complexity business processes into robust system logic and reusable AI
  patterns.

## Preferred Qualifications

- **Multi-agent systems** and agent collaboration patterns.
- Vector databases / retrieval infrastructure: **Pinecone**, **Weaviate**, **Milvus**.
- Model adaptation / fine-tuning: **LoRA**, **QLoRA**.
- Traditional NLP: tokenization, semantic similarity, entity extraction, summarization, transformer
  fundamentals.
- Habit of staying current with AI research, benchmarks, emerging engineering patterns.
- Experience in highly regulated, high-stakes, or operationally complex enterprise environments.

## The Team

Engineers, architects, product leaders, domain specialists; "one of the most complex enterprise
operating environments" — nuanced business rules, fragmented context, evolving requirements, little
tolerance for shallow or unreliable outputs. Success = enjoying the **machinery behind intelligent
systems**, not just the interface.
