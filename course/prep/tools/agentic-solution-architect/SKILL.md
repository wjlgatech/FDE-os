---
name: agentic-solution-architect
description: Turn a discovered customer problem (a Site Survey) into a concrete, deployable agentic-system architecture — the smallest end-to-end slice first, with the data/perimeter reality and an eval plan baked in. Use after the Delta Discovery Protocol, when scoping or pitching an agent solution for an enterprise customer, or when an interview/JD asks you to "architect agentic solutions." Refuses to design past the evidence; marks every assumption as a RISK.
---

# Agentic Solution Architect

> The bridge from *what's true* to *what to build*. Takes a **Site Survey** (from the
> [Delta Discovery Protocol](../../../../field-kits/delta-discovery-protocol/SKILL.md)) and
> produces an agent-system architecture — **gravel road first**, not a cathedral.
> Principle: **architecture is a hypothesis about the customer's reality.** If the reality is
> thin (gaps in the Survey), the architecture is thin — go back and discover, don't invent.

## When to run this

- Right after a discovery pass, when you have a Site Survey (or equivalent real context).
- Scoping / pitching an agentic solution to an enterprise customer.
- Prepping the JD responsibility "architect agentic solutions" — run it on any real problem and
  you have a portfolio artifact.

## Inputs it needs (refuse without them)

A Site Survey, or at minimum: the real workflow, the data reality (where data lives + perimeter
constraints), the true success metric (in the customer's numbers), and the political map. If these
are missing, **stop and run discovery** — do not design on guesses.

## The five passes

### Pass 1 — Restate the job-to-be-done from the Survey
- One sentence: who is the operator, and what outcome (in *their* numbers) makes this undeniably worth it?
- Name the single smallest end-to-end win that would build belief (the first paved inch).

### Pass 2 — Map the data & perimeter reality to a deployment shape
- Where does the data live; what can't leave the perimeter (VPC / on-prem / residency)?
- → choose the deployment target (public cloud / VPC / on-prem / hybrid) **from the constraint**, not preference.
- Name the integration truth that will actually take longest (assume longer).

### Pass 3 — Design the agent system (smallest viable)
- The loop: what triggers it, what the agent perceives, the tools/actions it can take, where a human stays in the loop.
- Tools & integrations: each external system it touches (DB, API, ticketing) — real, from the Survey.
- Model choice + why (capability vs cost vs latency vs where it can run given the perimeter).
- Guardrails: what it must never do; where it must ask; how failures fail safe.
- **Build-vs-buy / extend-vs-invent** per component — default to the smallest thing that ships.

### Pass 4 — Define the eval before building
- The 5pm test: what does "it works" look like to the operator on a normal day?
- The metric + how it's measured; the offline eval set; the "we're wrong early" signal.
- (Pair with a RAG/agent eval-harness so this is runnable, not aspirational.)

### Pass 5 — Sequence the first build (the gravel road)
- The one narrow end-to-end slice to ship first; what it deliberately does NOT do yet.
- The codify-back step: what learning from this slice feeds the next (the Delta Loop closing).

## Output: the Architecture Brief template

```
# Agentic Solution Architecture — <customer / problem>
Date: <date>   |   From Site Survey: <link/ref>

## 1. Job-to-be-done (operator + outcome in their numbers)
## 2. Deployment shape (chosen FROM the perimeter constraint)
- Target: <cloud | VPC | on-prem | hybrid> because <constraint>
- Hardest integration (assume slow): <...>
## 3. Agent system (smallest viable)
- Trigger / perception / actions / human-in-the-loop:
- Tools & integrations (real, from the Survey):
- Model + rationale (capability/cost/latency/perimeter):
- Guardrails & fail-safe:
- Build-vs-buy per component:
## 4. Eval (defined BEFORE building)
- "It works" at 5pm: ; Metric + measurement: ; Offline eval set: ; Early-wrong signal:
## 5. First build — the gravel road
- The one end-to-end slice to ship: ; Explicitly NOT yet: ; Codify-back step:
## 6. RISKS & unknowns (do NOT invent — list gaps to go re-discover)
-
```

## How to use as an agent skill

1. Load after a Site Survey exists. Refuse to produce the brief if Passes 1–2 inputs are missing —
   send the user back to discovery, naming the specific gap as a RISK.
2. Work pass by pass; keep every choice traceable to a line in the Survey.
3. Bias every decision to the **smallest end-to-end slice that proves value** — the gravel road,
   not the highway. A cathedral architecture from a thin Survey is the #1 FDE failure mode.

## Provenance

Built for FDE-os as the Cluster-4/5 flagship tool of the Reflection AI FDE prep curriculum. Composes
with the Delta Discovery Protocol (its input) and a RAG/agent eval-harness (its Pass-4 companion).
Distilled from the Delta Loop — service is an input to product, and the first paved inch beats the
big-bang plan.
