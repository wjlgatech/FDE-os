---
title: "feat: eval-loop + criteria-scorer — the self-improving artifact primitive"
type: feat
created_at: 2026-06-26
depth: standard
origin: docs/research/agent-loops-critical-eval.md
---

# feat: eval-loop + criteria-scorer

Build the one primitive the [agent-loops critical eval](../research/agent-loops-critical-eval.md)
found FDE-os missing: an **explicit, scored keep/revert loop with a run-log**, plus a general
**binary pass/fail criteria scorer** to feed it — reusing our existing gates, framed for engineers,
deterministic and offline like the rest of the repo.

---

## Summary

The article "Agent Loops that fix themselves" describes a loop FDE-os half-embodies (versioned,
eval-gated artifacts; git as memory) but is missing as an explicit tool: *edit a version → score it
→ keep if better, revert if worse → log the trajectory.* FDE-os already has the **scorers**
(`true-scorer`, `rag-eval-harness`) and the **memory** (git, scoped PRs, CHANGELOG). What's missing
is (a) a **general artifact scorer** — binary pass/fail criteria, the simplest eval style, mechanically
checkable — and (b) the **loop runner** that turns a sequence of scored versions into a kept winner +
a run-log (Round │ Change │ Score │ Verdict). This plan builds both, tested and offline.

## Problem Frame

FDE-os's self-improvement is currently *implicit* (PR review + prose CHANGELOG). That's fine for
humans but not (i) runnable, (ii) teachable, or (iii) dogfoodable. The article names the gap; the
critical eval confirms it's tri-objective (course content, forkable tooling, flywheel mechanic). The
risk to avoid: re-implementing an LLM judge or cloning their PM-tutorial scaffolding. The discipline:
deterministic, offline core; LLM judgment stays an opt-in hook, exactly as `rag-eval-harness` does it.

## Key Technical Decisions

- KTD1. **Criteria are typed, deterministic predicates, not free-form LLM judgments.** Each criterion
  is a checkable rule (`min_words`, `max_words`, `must_match`/`must_not_match` regex,
  `must_contain_number`, `must_cite`). This keeps the core offline + reproducible, and it covers the
  article's own examples (their biggest win, "force a concrete number," is regex-checkable). An
  LLM-judge criterion type is a documented opt-in hook, not in the core (mirrors `rag-eval-harness`).
- KTD2. **eval-loop's tested core is the keep/revert + run-log logic, scoring is pluggable.** Given a
  sequence of `(label, score)` rounds it decides accept/revert (keep if score beats best-so-far) and
  renders the run-log; the actual scorer (criteria-scorer / true-scorer / rag-eval-harness) is wired
  at the CLI edge. This makes the decision logic deterministic and unit-testable without invoking a
  scorer, and matches the article's manual-logging reality.
- KTD3. **The run-log format is the article's 4 columns** (Round │ Change │ Score │ Verdict) + a
  "what the loop learned" summary. Adopting their proven shape makes FDE-os run-logs legible to
  anyone who read the guide, and the run-log is a markdown file = git is the memory (KTD-free reuse).
- KTD4. **Gate reuse, not reinvention.** criteria-scorer exposes the same `gate(...)` shape as
  `true-scorer` (a threshold + reasons), so all three scorers are interchangeable behind eval-loop.

## Output Structure

```text
skills/
  criteria-scorer/
    SKILL.md
    scripts/criteria_score.py
    tests/test_criteria_score.py
    examples/launch-announcement-criteria.json
  eval-loop/
    SKILL.md
    scripts/eval_loop.py
    tests/test_eval_loop.py
    examples/example-run-log.md
```

---

## U1. criteria-scorer skill

- **Goal:** A deterministic, offline binary pass/fail criteria scorer — the simplest general artifact
  eval, the third gate alongside `true-scorer` and `rag-eval-harness`.
- **Requirements:** the critical eval's recommendation #2 (a general artifact scorer).
- **Dependencies:** none.
- **Files:** `skills/criteria-scorer/scripts/criteria_score.py`,
  `skills/criteria-scorer/tests/test_criteria_score.py`,
  `skills/criteria-scorer/examples/launch-announcement-criteria.json`,
  `skills/criteria-scorer/SKILL.md`.
- **Approach:** Input = an artifact (text or path) + a criteria file (JSON list). Each criterion has a
  `type` (one of `min_words`, `max_words`, `must_match`, `must_not_match`, `must_contain_number`,
  `must_cite`), a `value` where relevant, and a human `question`. Evaluate each → pass/fail (1/0);
  score = mean (0.00–1.00); `gate(score, threshold)` returns (passed, reasons) naming each failed
  criterion. Unknown criterion `type` is an explicit error, not a silent skip. Expose `score_artifact`
  and `gate` as pure functions for reuse by eval-loop.
- **Patterns to follow:** `true-scorer`'s gate/return shape; `rag-eval-harness`'s "deterministic core,
  LLM-judge is an opt-in hook" framing.
- **Test scenarios:**
  - Happy path: an artifact meeting all criteria scores 1.0 and passes the gate.
  - `must_contain_number`: text with a digit passes, text without fails (the article's key criterion).
  - `max_words`: a 200-word artifact fails a `max_words: 150` criterion with a naming reason.
  - `must_not_match` (buzzword list): an artifact containing a forbidden buzzword fails.
  - `must_cite`: an artifact with no `[...]`/URL citation fails the citation criterion.
  - Error: an unknown criterion `type` raises a clear error (not a false pass).
  - Gate: score below threshold blocks and names the failed criteria; at/above passes.
  - Determinism: two runs over the same inputs return identical scores.
- **Verification:** `criteria_score.py score <artifact> <criteria.json> --threshold 0.8` prints
  per-criterion pass/fail + the average + a verdict; the example criteria file scores its example.

## U2. eval-loop skill

- **Goal:** The missing primitive — turn a sequence of scored artifact versions into a kept winner +
  a run-log (Round │ Change │ Score │ Verdict), git as memory.
- **Requirements:** the critical eval's recommendation #1 (the eval-loop with keep/revert run-log).
- **Dependencies:** U1 (criteria-scorer is one wireable scorer; true-scorer / rag-eval-harness are
  others).
- **Files:** `skills/eval-loop/scripts/eval_loop.py`,
  `skills/eval-loop/tests/test_eval_loop.py`,
  `skills/eval-loop/examples/example-run-log.md`,
  `skills/eval-loop/SKILL.md`.
- **Approach:** Tested core = `decide(rounds)` where `rounds = [{"label","change","score"}, ...]`:
  round 0 is the baseline; each later round is `accept` if its score beats the best-so-far else
  `revert` (best-so-far unchanged); returns per-round verdicts (with the score delta) and the winning
  label. `render_run_log(decisions)` emits the article's 4-column markdown table + a "what the loop
  learned" line (the largest single accepted gain). CLI: a `log` mode (explicit scores → run-log,
  matches manual logging and is fully testable) and a `score-each` mode (artifact versions + a scorer
  choice → score each via U1/true-scorer/rag-eval-harness → decide → run-log). The run-log is written
  to a file = committed = git is the memory.
- **Patterns to follow:** the article's `autoresearch/run-log.md` shape (the 41%→90% trajectory with a
  reverted round); KTD2/KTD3 above.
- **Test scenarios:**
  - Baseline + improving rounds: scores `[0.41, 0.68, 0.90]` → all `accept`, winner = last, run-log
    has 3 rows.
  - Regression + revert: `[0.41, 0.90, 0.82]` → round 2 `accept`, round 3 `revert`, winner stays the
    0.90 version (reproduces the article's reverted experiment).
  - Tie: a score equal to best-so-far is `revert` (strict improvement to accept) — documented choice.
  - `render_run_log`: output is a valid 4-column markdown table; the "what the loop learned" line
    names the largest accepted gain (e.g. +0.27 in the article's case).
  - Determinism: same rounds → identical run-log text.
  - Integration: `score-each` over 2 fixture artifact versions using criteria-scorer (U1) produces a
    run-log whose verdicts match the underlying scores.
- **Verification:** `eval_loop.py log <rounds.json> --out run-log.md` writes the table; `score-each`
  scores real versions and logs them; the example run-log renders.

---

## Scope Boundaries

### In scope
The two skills above (criteria-scorer, eval-loop), tested + offline, picked up by the existing
`tests.yml` CI auto-discovery.

### Deferred to follow-up work
- A **Delta Field Manual / course lesson** naming the artifact lifecycle for FDEs, shipping eval-loop
  as its Field Kit (content; publish-gated like the rest of Stage 2).
- **Dogfooding eval-loop in CI** — running FDE-os's own artifact scores through a tracked run-log
  (nice-to-have once the tools exist).
- An **LLM-judge criterion type** for criteria-scorer (opt-in hook beyond the deterministic core).

### Outside this product's identity
- Cloning the reference repo's PM/Git **teaching scaffolding** — FDE-os is past it (critical eval).
- An **autonomous "runs while you sleep"** loop — the article's own implementation is manual +
  human-supervised; FDE-os's loop is assisted, humans own taste, gates own the floor.

## Risks & Dependencies

- **Deterministic criteria can't judge everything** (e.g. "is the tone right?"). Mitigation: the core
  covers mechanically-checkable criteria (which is most of the article's examples); subjective
  criteria are explicitly an opt-in LLM-judge hook, not promised in the core — no R4-style overclaim.
- **Over-building toward autonomy.** Mitigation: scope boundary above; the loop is assisted, logged,
  reversible — not autonomous.

## Sources & Research

- `docs/research/agent-loops-critical-eval.md` — the evaluation that scoped this (recommendations
  #1 and #2 map to U2 and U1).
- `docs/research/sources/2026-agent-loops-self-fixing.md` — the run-log 4-column format and the
  binary-criteria eval style this plan adopts.
- Existing `skills/true-scorer` and `skills/rag-eval-harness` — the gate/return shape U1 mirrors and
  the scorers U2 wires.
