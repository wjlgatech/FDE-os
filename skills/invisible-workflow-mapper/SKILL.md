---
name: invisible-workflow-mapper
description: Reconstruct an organization's invisible DECISION workflow — how a "yes" actually happens — from partial, indirect signals, before the client can articulate it. Scores adoption-readiness, infers the likely decision-workflow archetype and its known adoption traps, and emits the oblique probes to surface what's still unknown. Use when scoping or deploying an AI/agentic solution into a real org and you sense the technical answer is the easy part — adoption depends on fitting how decisions get made. Deterministic, offline core + a pass/fail gate; pairs with the delta-discovery-protocol field kit.
---

# invisible-workflow-mapper

> The fourth gate, alongside `true-scorer`, `criteria-scorer`, and `rag-eval-harness` — but it scores
> a *deployment context*, not an artifact. It deepens the [`delta-discovery-protocol`](../../field-kits/delta-discovery-protocol/SKILL.md)
> field kit (Pass 2 maps the workflow, Pass 4 the political terrain) into the one axis that decides
> adoption: **how a decision actually gets made — and whether your answer can fit it.**

## Why this exists

From a reader of the Delta long-form: *"the biggest failures aren't model failures — they're
workflow failures. AI can produce a great answer, but if it doesn't fit how decisions actually get
made inside an organization, it never gets adopted."* Clients can rarely *describe* their own
decision workflow (it's tacit and political), so a Forward Deployed Engineer has to **reconstruct it
from signals — ideally before they spell it out.** This tool turns that reconstruction into a
deterministic, gateable step.

## The anatomy of a decision workflow

Eight dimensions; the four **load-bearing** ones are the adoption predictors — you cannot forecast
adoption without them.

| Dimension | Load-bearing | What it answers |
|---|---|---|
| Trigger | | the event that starts the decision — the moment your output must arrive in |
| **Decider** | ✅ | who actually says yes (not who is in the room) |
| **Approval chain** | ✅ | the real sign-off path and the quiet vetoes that can kill it |
| **Evidence ritual** | ✅ | the artifact / format / forum a decision is actually made on |
| Cadence | | the rhythm decisions happen on (standing review vs ad-hoc fire) |
| Incumbent process | | how it's done today — what your AI must augment or replace |
| **Adoption owner** | ✅ | whose daily behavior must change for the AI to actually get used |
| Kill points | | where a good answer dies — compliance, trust, format, politics |

## What it produces

An **Invisible Workflow Map**: per-dimension coverage, an **adoption-readiness score** (0–1 over the
load-bearing four), the **inferred decision-workflow archetype** + its canonical adoption traps, the
**oblique probes** to run next, and a **gate** (BLOCK until the load-bearing dimensions are known —
because a great answer that doesn't fit the workflow never gets adopted).

## The archetypes (the "before they tell you" inference)

Each carries the *tells* that hint at it and the *adoption traps* it brings: `single-strong-owner`,
`consensus-committee`, `regulated-signoff`, `shadow-bottom-up`, `procurement-gated`, `metrics-ritual`.
The mapper matches tells against your observations **and** the org context (industry, size, tools), so
even a thin first call yields a hypothesis + the traps to design around.

## Run it

```bash
# signals.json: {context:{org,industry,size,tools,notes}, signals:[{dimension,observation,confidence,source}]}
python3 scripts/workflow_map.py map examples/claims-triage-signals.json
python3 scripts/workflow_map.py map signals.json --threshold 0.6 --json
```

Exit code is `0` when the gate PASSes, `1` when it BLOCKs (CI-friendly). An unknown `dimension` is an
explicit error, never a silent pass (same posture as `criteria-scorer`).

## How an agent uses it (the loop)

1. After a discovery call, the agent reads the transcript and **emits signals** — one observation per
   dimension it can support, with an honest confidence (this interpretation step is the opt-in LLM
   part; the scoring below is deterministic).
2. Run the mapper → get the map, the archetype + traps, and the gate.
3. If BLOCKED, the **probes** are the agenda for the next conversation — oblique questions that surface
   the workflow without asking "what's your workflow?" (people can't answer that).
4. Re-run as signals accumulate; ship the integration only once the load-bearing four are known.

## Boundaries

Deterministic core, no network — runs inside a customer perimeter. It scores *coverage and fit*, not
truth: a confident signal can still be wrong, so treat a PASS as "you know enough to design for
adoption," not "you're right." Reading raw transcripts into signals is an LLM step the agent does
first; the archetype library is a starting taxonomy, not exhaustive — add archetypes as the field
teaches you new ones (that's the flywheel).
