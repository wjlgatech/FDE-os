# FDE readiness — Anthropic & OpenAI

*A JD-validated program to get educated, get proof, and apply for Forward Deployed Engineer roles at
Anthropic and OpenAI. Compiled from the live 2026 postings (see [`../target-jds/anthropic-fde-applied-ai.md`](../target-jds/anthropic-fde-applied-ai.md)
· [`../target-jds/openai-fde.md`](../target-jds/openai-fde.md)). Readiness = knowledge · skills ·
mindset · behavior/habits · **portfolio-proven** agentic systems.*

---

## What both companies are actually buying

Strip the two JDs to their overlap and the FDE is one thing: **an engineer who can walk into a
customer's mess, own it end-to-end, and ship a production LLM/agent system that gets adopted.**

| Shared core (train for this first) | Anthropic-distinctive | OpenAI-distinctive |
|---|---|---|
| Embed with strategic customers; end-to-end (discovery → build → **production**) | Deliver **MCP servers, sub-agents, agent skills** as artifacts | Own **scope/speed/quality trade-offs**; sequence + unblock |
| **Production Python** + shipped apps | Explicit **AI-safety** value | **Frontend + backend** prod code (Python/JS) |
| **LLM/agent production** exp: prompt eng, **evals**, deploy at scale | White-glove enterprise deployment | **Eval-driven feedback** that moves the model/product roadmap |
| **Autonomy under ambiguity**; strong stakeholder communication | 3+ yrs customer-facing | 5+ yrs; more senior; simplify-under-pressure |
| Field feedback → Product/Research | | Hybrid 3 days/office |

**Read:** Anthropic weights the *agentic artifact craft* (MCP/sub-agents/skills) + safety. OpenAI
weights *senior end-to-end ownership* + full-stack + eval-driven roadmap influence. The floor for
both is: **you have shipped a real LLM/agent system to production, with evals, and can prove it.**

---

## 1. Knowledge (what to know cold)

- **The FDE thesis & the field reality** — why embedded > remote; that ~95% of enterprise AI stalls on *approach, not model* (MIT); adoption is the metric. (See the marketing longform + `FDE-research-synthesis.md`.)
- **LLM production**: prompt engineering (system design, tool schemas, structured output), context management, cost/latency trade-offs, failure modes of probabilistic systems.
- **Agentic design**: tool-calling loops, **sub-agents / orchestration**, **agent skills**, planning/verification, human-in-the-loop, memory. Protocols: **MCP** (Anthropic's own — know it deeply) and **A2A**.
- **Evaluation** (the load-bearing skill): offline eval sets, golden sets, retrieval metrics (precision/recall/MRR), groundedness/hallucination checks, LLM-as-judge, **eval-as-gate** in CI, calibration against outcomes.
- **RAG & retrieval**: chunking, embeddings, vector + graph stores, grounding, citation coverage.
- **Enterprise deployment**: data boundaries, PII/tenant isolation, security/GRC, VPC/self-hosted inference, review gates before scale.
- **System design under ambiguity**: discovery, the smallest end-to-end win, sequencing, rollback.
- Provider fluency: **Claude** models + the Anthropic API (for Anthropic); OpenAI models + API (for OpenAI). Know the current model families and when to reach for each.

## 2. Skills (what to be able to *do*, on demand)

- **Production Python** from a blank page (the coding room is real). Drill it: [`tools/coding-drill-kit`](tools/coding-drill-kit/) — 6 templates from memory, mechanically scored, twice on different days.
- **Full-stack** for OpenAI: a real frontend (React/Next) + backend (Python/Node), deployed. You've done this — the Vercel apps below.
- **Build an agent end-to-end**: a tool-using agent + grounded RAG + an eval gate, in ~90 minutes. Drill: [`tools/agentic-solution-architect`](tools/agentic-solution-architect/SKILL.md).
- **Ship an MCP server** (Anthropic's exact deliverable): expose tools over MCP. You have one — `skills/fde-mcp-server` (7 tools).
- **Write the eval first**: turn "does it work?" into a pass/fail gate (`skills/rag-eval-harness`, `true-scorer`, `criteria-scorer`).
- **Deploy to production** ($0 stack): static + serverless on Vercel, env/secrets, verify the live surface. You've shipped 3 live apps.
- **Discovery / scoping**: run the [`field-kits/delta-discovery-protocol`](../../field-kits/delta-discovery-protocol/) on a messy problem → a site survey + the smallest win.

## 3. Mindset (how an FDE thinks)

- **Adoption over output.** Success = it's in production and used, not "the demo worked."
- **Evidence over claims.** Observed > claimed; no eval, no ship. Validate the probabilistic system in the field.
- **Autonomy under ambiguity.** No spec, no permission — find the real problem and the smallest end-to-end win, then move.
- **Contribute in code when momentum needs it** (OpenAI's line) — you are an engineer who sells, not a seller who codes.
- **Customer-obsessed, field-feedback loop** — the deployment teaches the product; carry that signal back.
- **Safety as a first-class value** (Anthropic) — creative technical application *toward* safe, beneficial AI.
- **Trade-offs are the job** (OpenAI) — scope vs speed vs quality, decided fast and soundly under pressure.

## 4. Behavioral patterns · habits · routines (build the muscle before the interview)

These are what turn knowledge into a reliable operator — the difference between "knows it" and "does it under pressure":

- **Daily (~30 min):** the coding drill (production from memory) + read one primary source (a model/API doc, an eval paper, a real postmortem). Log it.
- **Weekly build-in-public:** ship one small thing to production and write a 5-line field note (what broke, what you validated). This compounds into the portfolio *and* the "attributable, verified" evidence hirers trust.
- **Write-the-eval-first:** never build a capability without its pass/fail check. Make it a reflex.
- **Close the loop you open:** finish or explicitly kill; don't let repos go dark. (This is the reliability signal — and it's observable in your commit history.)
- **Ship-small-to-prod:** prefer a tiny end-to-end deployed slice over a big local demo. Deploy weekly.
- **Collect references as you go:** after every collaboration, ask for a 30-second structured vouch *while it's fresh*. Reliability is the one rung you can't self-issue (see the attestation-gap article).
- **Teach-back cadence:** explain each new tool to a non-engineer in one page. Anthropic/OpenAI FDEs enable customers — teaching *is* the job.
- **Timebox decisions:** practice "fast, sound, reversible" — set a clock, decide, note the trade-off. Builds the under-pressure muscle OpenAI screens for.

## 5. Portfolio proof — agentic systems that map 1:1 to the JD deliverables

This is the whole game: **don't claim it, show a deployed, evaluated, attributed system.** What's
already built here maps directly onto what these two roles ask for:

| JD deliverable | Proof you can point to | Tier |
|---|---|---|
| **MCP server** (Anthropic) | `skills/fde-mcp-server` — a runnable MCP server exposing 7 tools | observed / shippable |
| **Sub-agents + agent skills** (Anthropic) | `interview-agent` (a deployed conversational agent) + the FDE-os skills tree (one authoring, multi-runtime) | observed (live on Vercel) |
| **End-to-end deployment in production** (OpenAI) | `portfolio-trust` + `interview-agent` + `scorecard`/`staffing-brain` — **live on Vercel**, verified | observed (live) |
| **Eval frameworks / eval-driven** (both) | `rag-eval-harness`, `true-scorer`, `criteria-scorer`, `calibration.py` (validate predictions vs outcomes) | observed + tested |
| **Full-stack** (OpenAI) | The web cockpits (frontend) + serverless APIs (backend), deployed | observed (live) |
| **Discovery / scoping under ambiguity** (both) | `delta-discovery-protocol` + `invisible-workflow-mapper` | observed |
| **Reliability** (the rung you can't self-issue) | **collect vouches** — the attestation gap; run `portfolio-trust` on your own portfolio | needs attested |

**Self-assess before you apply:** paste your portfolio into [portfolio-trust.vercel.app](https://portfolio-trust.vercel.app)
→ it tells you which rung is missing. Almost certainly it's the vouch. Go get two.

**Package the portfolio for a recruiter/agent:** the [agentic portfolio](https://agentic-portfolio-lovat.vercel.app)
answers questions 24/7, grounded — and now carries the *evidence* extension (provenance + CI-verified
+ vouches), so it doesn't collapse into a prettier résumé.

---

## The 30 / 60 / 90-day plan

**Days 1–30 — Floor + one flagship.**
- Coding drill to **6/6 twice**. Read the MCP spec + Claude/OpenAI API docs end to end.
- Ship **one flagship agentic system to production** with an eval gate (you have several — pick the sharpest, harden its evals, deploy, write the field note).
- Publish an **MCP server** (Anthropic) — even a small one. It's their literal deliverable.

**Days 31–60 — Depth + proof.**
- Add **sub-agents + an agent skill** to the flagship; full-stack it (frontend + backend) for OpenAI.
- Wire **eval-driven feedback** (calibration): predicted vs actual, and show the loop.
- Run a **discovery protocol** on a real messy problem; write the site survey.
- Collect **2 structured vouches** from past collaborators.

**Days 61–90 — Apply, with evidence.**
- Tailor to each JD: Anthropic → lead with MCP/sub-agents/skills + safety framing; OpenAI → lead with end-to-end ownership, full-stack, eval-driven roadmap influence, and seniority (frame the 5+ yrs).
- Application = a **portfolio link that carries observed + attested evidence**, plus 3 field notes and one crisp "here's a customer problem I'd scope and how" write-up.
- Prep the interview loop with `coding-drill-kit` (coding room) + `agentic-solution-architect` (design round) + a mock discovery.

## The one-line strategy
Both roles hire the same proof: **a production LLM/agent system, eval-gated, that you can attribute
to yourself and that someone will vouch for.** You've built the systems and the evidence layer — the
remaining move is packaging (MCP + sub-agents to satisfy Anthropic; full-stack + eval-driven roadmap
for OpenAI) and collecting the vouches you can't self-issue.
