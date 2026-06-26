---
name: eval-loop
description: Turn a sequence of scored artifact versions into a kept winner plus a run-log (Round | Change | Score | Verdict) — the self-improving loop primitive. Score each version with a pluggable scorer (criteria-scorer / true-scorer / rag-eval-harness), keep a version only if it strictly beats the best so far, revert otherwise, and append the trajectory to a markdown run-log committed to git. Use to optimize a prompt/skill/doc with evidence instead of guessing, and to make "what improved it" memory live in git, not your head. Deterministic core, offline.
---

# eval-loop

> The primitive FDE-os was missing (see `docs/research/agent-loops-critical-eval.md`):
> *edit a version → score it → keep if better, revert if worse → log the trajectory.*
> Git is the memory; the run-log is a committed file. The decision logic is deterministic and
> tested; the **scorer is pluggable**.

## The loop

1. Produce candidate versions of an artifact (a prompt, a skill file, a doc, an answer).
2. `eval-loop` scores each (via any scorer), keeps a version **only if it strictly beats the best so
   far**, otherwise reverts (best-so-far stands — a tie reverts; improvement must be real).
3. It appends a row to the run-log: `Round | Change | Score | Verdict` (✅ accept / ❌ revert), and
   names the largest single gain ("what the loop learned").
4. Commit the run-log. Git now remembers which change helped and which broke it.

## Run it

```bash
# Manual logging — you already have scores (fully reproducible):
python3 skills/eval-loop/scripts/eval_loop.py log <rounds.json> --out run-log.md
#   rounds.json = [{"label","change","score"}, ...] in order

# Score-each — give it artifact versions + a scorer; it scores, decides, and logs:
python3 skills/eval-loop/scripts/eval_loop.py score-each v1.md v2.md v3.md \
  --scorer "python3 skills/criteria-scorer/scripts/criteria_score.py score {file} crit.json" \
  --out run-log.md
```

`{file}` is substituted per version; eval-loop parses the first numeric/`%` score from the scorer's
output (works cleanly with `criteria-scorer`; any scorer that prints a `score: <n>` line works).
See `examples/example-run-log.md` — the source article's 41%→90%-with-a-revert trajectory, regenerated
by this tool.

## What it is NOT (honest edges)

- **Not autonomous.** The source article's "runs while you sleep" is hype — their own loop is manual
  + human-supervised. This loop is *assisted*: you (or an agent) produce versions and own taste; the
  loop owns the scored keep/revert decision + the memory. Brand/taste/legal stay human checks.
- **Not a scorer.** It orchestrates scorers; it doesn't judge quality itself. Pair it with
  `criteria-scorer`, `true-scorer`, or `rag-eval-harness`.

## Verify

```bash
python3 -m unittest discover -s skills/eval-loop/tests -p 'test_*.py'
```

8 tests: all-improving → all accept; regression → revert keeping the best (reproduces the article's
reverted experiment); tie-reverts; largest-gain attribution; run-log table shape + marks;
determinism; and a `score-each` integration with a stub scorer (incl. `%` parsing).

## Provenance

Built for FDE-os (eval-loop plan, U2) as the missing primitive from
`docs/research/agent-loops-critical-eval.md`. Run-log shape from the source article; scoring reuses
the repo's existing gates.
