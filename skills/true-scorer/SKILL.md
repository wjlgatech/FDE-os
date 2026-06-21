---
name: true-scorer
description: Score a Delta Field Manual draft against the TRUE rubric (Transferable, Reusable, Understandable, Experience-able) 0–3 per letter and apply the ship gate (total ≥ 10 AND no letter < 2). Use before publishing any Delta post, or whenever you need a runnable, repeatable quality gate on long-form content that must ship a forkable asset and a felt exercise. Refuses to pass a draft below threshold and names what to fix.
---

# TRUE-scorer

> The publish gate for Delta Field Manuals. The rubric is itself a reusable asset (Field Kit
> menu: eval rubric) — an agent can score any draft and **refuse to pass** a weak one.

## TRUE, and the gate

| Letter | Meaning | 3 looks like |
|---|---|---|
| **T** Transferable | a re-teachable mental model | named **and** diagrammed, re-teachable in one breath |
| **R** Reusable | a forkable asset for agents | a complete, copy-pasteable asset with run instructions |
| **U** Understandable | a sharp 15-yo follows it | every abstraction earns a concrete anchor first |
| **E** Experience-able | a felt "try this" → conviction | a try-this that reliably produces a felt result |

**Ship gate (hard): total ≥ 10 / 12 AND every letter ≥ 2.** A draft with a perfect total but one
weak letter does **not** ship — the AND is the whole point.

## How to run

```bash
# Heuristic baseline + verdict on a draft (agent then refines the 0–3 with judgment):
python3 skills/true-scorer/scripts/score.py <draft.md>

# Apply the gate to explicit per-letter scores (e.g. after agent judgment):
python3 skills/true-scorer/scripts/score.py --scores T=3,R=3,U=2,E=2
```

## How an agent uses this (the two layers)

1. **Run the script** for the deterministic signals: does the draft link a Field Kit (R)? have a
   concrete "try this" (E)? name + diagram a model (T)? keep jargon density low (U)? These set a
   defensible *baseline* — they raise the floor, they never guarantee a 3.
2. **Refine each letter with semantic judgment** per the rubric above. The script cannot tell
   whether a model is genuinely re-teachable or a "try this" actually produces conviction — you
   can. Adjust the 0–3 up or down, then re-run `--scores` to apply the gate.
3. **Honor the verdict.** If BLOCK, do not publish — fix the named-weak letter first. The script
   never invents a pass; the gate is exact.

## Verify

```bash
python3 -m unittest discover -s skills/true-scorer/tests -p 'test_*.py'
```

Covers the gate exhaustively (perfect pass; total=10-but-E=1 blocks; boundary total=10/min=2
passes; sub-total blocks; missing letter blocks) and the heuristic against the real Post #1
(scores 12/12, its known reference) and a deficient draft (blocked).

## Provenance

Built for FDE-os (roadmap U4) from `Delta-TRUE-article-spec.md`'s 0–3 rubric and ship threshold.
