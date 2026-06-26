# Critical Evaluation — "Agent Loops that fix themselves" vs. FDE-os

*Source: [2026-agent-loops-self-fixing.md](sources/2026-agent-loops-self-fixing.md) +
the reference repo `aakashg/pm-github-workflow-repo`. Researched 2026-06-26.*

## Verdict (TL;DR)

**The core idea is real, durable, and unusually aligned with FDE-os — the framing is hype.** Strip
the "while you sleep 🤯" and you get a sound thesis FDE-os already half-embodies: *version-controlled,
eval-gated artifacts that mature from prompt → skill → automation, with git as the memory of what
worked.* FDE-os is **ahead on substance** (real tested skills, CI gates) and **behind on one
primitive**: an explicit **eval-loop with a keep/revert run-log**. That primitive is worth building —
it serves all three objectives at once. Do **not** clone their teaching repo; it's a tutorial, we're
a product.

## What's real and aligned (keep)

1. **The artifact lifecycle** — *prompt → repeated workflow → structured skill → eval criteria →
   team repo → automation.* This is a clean vocabulary for what FDE-os has been doing ad hoc. Our
   skills (`knowledgefy`, `true-scorer`, `rag-eval-harness`, `field-kit-generator`, `fde-mcp-server`)
   each climbed most of that ladder. Naming the ladder makes it teachable (Objective 1).
2. **Git as the memory layer** — keep/revert decisions live in history, not in someone's head. FDE-os
   already does this: every change is a scoped PR, and `CHANGELOG.md`'s *Investigated / Rejected*
   section is literally "what we tried and reverted, with the measurement that killed it."
3. **Eval gates before you trust an artifact** — their binary pass/fail (0–1 average) is the same
   family as our `true-scorer` (0–3, gate at ≥10 & no letter <2) and `rag-eval-harness` (metric gate).
   Convergent independent design = strong signal the pattern is right.
4. **Reversibility as the foundation** — "tracked, diffable, reversible." This is why FDE-os never
   edits the plan to record progress (git is the truth) and branches per stage.

## What's hype / be skeptical (discard)

1. **"Runs on its own while you sleep."** Their *actual* loop (`autoresearch/run-log.md`) is
   **manually triggered, local, human-supervised** — they explicitly keep brand voice + legal as
   *human checks outside the loop*. The autonomy claim is aspirational marketing, not what the repo
   shows. FDE-os's honest version: the loop is **assisted**, with humans owning taste and the gates
   owning the floor. Don't promise autonomy we (or they) can't deliver — that's an R4-style
   un-sourced claim.
2. **"Forget prompting."** Overstated — prompts are the *seed* of the lifecycle, not obsolete. The
   real claim is "don't *stop* at prompting."
3. **Two sources ≠ corroboration.** Ng and Saboo posted the *identical* text; it's one guide. Treat
   accordingly (already flagged in the source file).
4. **Audience gap.** It's PM-framed. FDE-os is engineer-framed. The mapping is strong but a Delta
   post must re-anchor it in FDE reality (a customer deployment loop, not a launch-announcement
   prompt).

## FDE-os scorecard against the article's loop

| The loop step | FDE-os today | Gap |
|---|---|---|
| Versioned artifacts | ✅ every skill, scoped PRs | — |
| Eval/scoring system | ✅ `true-scorer`, `rag-eval-harness` (+ CI runs them) | evals are per-skill unit tests, not artifact-quality scores |
| Keep-if-better / revert-if-worse | ⚠️ implicit (PR review, CHANGELOG Investigated/Rejected) | **no explicit scored keep/revert loop** |
| A run-log of what worked | ❌ | **missing** — CHANGELOG is prose, not a scored trajectory |
| Git as memory | ✅ | — |
| CI automation of gates | ✅ `tests.yml` runs gates on every PR (**more automated than their local loop**) | — |
| Artifact lifecycle, named + taught | ❌ | not articulated as FDE content |

**Two real gaps:** (a) an explicit **eval-loop primitive** (score an artifact across versions, keep
the winner, log the trajectory), and (b) the lifecycle, **named and taught** as FDE-os content.

## Alignment with the FDE-os mission (why this is tri-objective)

- **Objective 1 (course):** the self-improving artifact loop is teachable, and both target JDs want
  it — CVS lists *"evaluation pipelines"* and *"iteration"*; Reflection wants *"evolving playbooks."*
  A Delta Field Manual / lesson on it is on-thesis content.
- **Objective 2 (tooling):** an `eval-loop` skill that wraps our existing gates into a scored
  keep/revert loop with a run-log is a forkable Field Kit — and it dogfoods (we can run FDE-os's own
  artifacts through it).
- **Objective 3 (flywheel):** the lifecycle (prompt → … → automation) *is* the flywheel mechanic,
  and a run-log of what improved is exactly the field-signal the flywheel is supposed to capture.

## Recommendation (feeds the plan)

Build the **one missing primitive**, framed for engineers, reusing what we already have — don't
re-teach PM Git basics. Concretely:

1. An **`eval-loop`** skill: given an artifact + a scorer (our `true-scorer` / `rag-eval-harness` /
   a binary-criteria scorer) + versions, it scores each, **keeps the best, and appends a run-log row**
   (Round │ Change │ Score │ Verdict) — git is the memory. Deterministic, offline, tested, per repo
   convention.
2. A lightweight **binary pass/fail criteria scorer** (their eval style) as a third gate alongside
   `true-scorer` and `rag-eval-harness` — it's the simplest, most general artifact eval.
3. (Content, later) a **Delta post / course lesson** that names the artifact lifecycle for FDEs and
   ships the `eval-loop` as its Field Kit — closing content→tooling→course in one move.

Scope the build deliberately (see the plan). Do **not** import their repo's teaching scaffolding;
FDE-os is past it.
