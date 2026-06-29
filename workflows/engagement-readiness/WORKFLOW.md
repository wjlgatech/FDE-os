---
name: engagement-readiness
description: A dynamic workflow that composes two FDE-os skills into one go/no-go gate for an engagement — invisible-workflow-mapper (will it get ADOPTED?) AND rag-eval-harness (does it WORK?). Ship only if both pass. Use before committing to build/deploy an agentic solution for a customer, to combine adoption-fit and technical correctness into a single, honest verdict. Deterministic; it orchestrates the skills' cores, adds no new scoring.
---

# engagement-readiness  ·  the first composition workflow

> Skills are building blocks; a **workflow** chains them. This is the tool-base's first composition —
> the FDE engagement pipeline (`discovery → adoption-fit → architecture → eval`) reduced to its two
> *runnable, gateable* steps, AND-ed into one verdict.

## The question it answers

*Should we build/ship this engagement?* Two failure modes kill deployments, and you must clear both:

1. **Will it get adopted?** → [`invisible-workflow-mapper`](../../skills/invisible-workflow-mapper/SKILL.md)
   scores adoption-readiness from the decision-workflow signals. *A great answer that doesn't fit how
   decisions get made never gets adopted.*
2. **Does it work?** → [`rag-eval-harness`](../../skills/rag-eval-harness/SKILL.md) scores the system
   against a real eval set. *A well-adopted answer that doesn't work is worse.*

**GO only if both pass.** If a stage is missing, the verdict is **NO-GO** — you cannot ship on a
dimension you haven't measured (honest, never a false green).

## Run it

```bash
python3 run.py examples/engagement.json            # markdown report; exit 0 = GO, 1 = NO-GO
python3 run.py engagement.json --wf-threshold 0.6 --json
```

Input bundle:

```json
{
  "workflow": { "context": {...}, "signals": [ {"dimension":"decider","observation":"…","confidence":0.85}, … ] },
  "eval":     { "k": 3, "thresholds": {"recall@k": 0.5}, "eval_set": [ … rag-eval-harness items … ] }
}
```

## How it's built

It lazy-imports the two skill cores by repo-relative path (the same pattern `fde-mcp-server` uses)
and AND-s their gates — **no new scoring logic lives here.** That's the point of a composition: the
skills stay the single source of truth; the workflow only sequences them and combines verdicts.
Deterministic and offline; 6 tests under `tests/`. Discovered by CI alongside the skills
(`workflows/*/tests`).

## Extending

Add a stage by importing another skill core and folding its gate into the combined verdict (e.g. a
`criteria-scorer` pass on the proposed architecture doc, or a `true-scorer` gate on the customer
write-up). Keep the rule: **GO requires every assessed stage to pass, and an unassessed stage blocks GO.**
