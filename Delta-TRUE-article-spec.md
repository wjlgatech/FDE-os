# Delta — The TRUE Long-Form Article Spec

*Every Delta post has two tiers: a short feed post (the **Signal** — viral, exposure) that drives to a long-form LinkedIn article (the **Field Manual** — depth). Every Field Manual must be **TRUE**, and ships a downloadable **Field Kit** (reusable asset for agents). Running example throughout: Post #1, Palantir/Delta origin.*

## What TRUE means (and what each letter feeds)

| Letter | Meaning | Pillar it feeds | The test |
|---|---|---|---|
| **T** — Transferable | A mental model / skill a human can take and re-teach tomorrow | Course | "Could the reader teach this to a colleague tonight?" |
| **R** — Reusable for agents | A forkable artifact (prompt, skill, MCP spec, checklist) an AI agent or human+agent can run | Toolkit | "Did they leave with a working tool, not just an idea?" |
| **U** — Understandable | A sharp 15-year-old follows it start to finish, no jargon walls (concrete → bridge → abstract) | Reach / voice | "Any jargon introduced without a concrete anchor first?" |
| **E** — Experience-able | The reader DOES or FEELS something that produces conviction, not a nod | Community / conviction | "Is there a 'try this' that makes the truth felt?" |

TRUE is the flywheel in four letters: T=Course, R=Toolkit, U=voice, E=Community.

## The Field Manual template (each section delivers a TRUE letter)

1. **The Felt Problem** (U + E) — open with a concrete, 15-yo-legible story that makes the reader *feel* the problem before any abstraction. *(Post #1: you can't email a requirements doc to the CIA. A great French restaurant's waitstaff is part of the kitchen.)*
2. **The Mental Model** (T) — name and diagram the transferable idea. One model, one picture. *(Post #1: "The Delta Loop — deploy → learn → codify → feed back," and "one customer / many capabilities" vs "one capability / many customers.")*
3. **The Evidence** (credibility) — the data, history, trend, future. Depth version of the Signal's stats, with citations. *(1,165% growth; Palantir 80% vs Accenture 32%; $6 services per $1 software; MIT's 95%.)*
4. **The Experience / Try-It** (E) — a concrete exercise the reader does in <10 min that produces a felt result → conviction. *(Post #1: "Open your last project's requirements doc. Count how many requirements turned out wrong. That number is the deployment gap — and why the FDE exists.")*
5. **The Field Kit** (R) — the forkable asset, with a download/link and a one-line "how to run it." *(Post #1: "The Delta Discovery Protocol" — a prompt/skill that runs FDE-style context discovery.)*
6. **The Reframe + Forward** (E + community) — the conviction line, then a handoff to one pillar + the war-story question.

## The Field Kit menu (pick ONE reusable asset per post)

Each article ships exactly one, drawn from this menu. These accumulate into FDE-os.

- **Prompt / mega-prompt** — a runnable prompt for a specific FDE task
- **Agent skill** (`SKILL.md`) — a forkable skill for Claude/agents (ties directly to FDE-os)
- **MCP server spec** — a small, named server definition
- **Checklist / SOP** — e.g., a deployment pre-flight, a discovery checklist
- **Decision tree / framework canvas** — e.g., "Dev vs Delta: which is this work?"
- **Eval rubric** — a scoring rubric an agent can apply
- **Template** — Site Survey, Technical Scoping/PRD, Weekly Exec Summary (FDE field artifacts)
- **Workflow / runbook** — a multi-step repeatable procedure

Asset-to-post mapping should track the pillar map (Course-heavy posts → templates/checklists; Toolkit posts → skills/MCP specs; etc.).

## The TRUE eval rubric (run before publishing — agent-runnable)

Score each letter 0–3. **Ship threshold: total ≥ 10/12 AND no letter below 2.** This rubric is itself a reusable asset — an agent can score any draft.

- **T (0–3):** 0 = no model; 1 = model implied; 2 = model named; 3 = model named + diagrammed + re-teachable in one breath.
- **R (0–3):** 0 = nothing to run; 1 = vague "you could build…"; 2 = a real asset described; 3 = a complete, copy-pasteable asset with run instructions.
- **U (0–3):** 0 = jargon wall; 1 = mixed; 2 = mostly concrete-first; 3 = every abstraction earns a concrete anchor first; a 15-yo finishes it.
- **E (0–3):** 0 = pure assertion; 1 = vivid story only; 2 = story + a "try this"; 3 = a try-this that reliably produces a felt result → conviction.

## The pipeline (1 input → 4 outputs)

Research vault → **Signal** (feed post, exposure) → **Field Manual** (TRUE article, depth) → **Field Kit** (reusable asset, toolkit/product) → **War-story prompt** (community, retention). One research effort, four flywheel touches. AI does ~90% of the production from the vault; you do the 10% taste + lived experience.

## Scope discipline

Define the template once (this doc). Build **Post #1's full Field Manual + Field Kit** as the proof. Score it with the rubric. Only then systematize for posts 2–12. Don't template all twelve in the abstract — prove one, then let AI mass-produce against the proven shape.
