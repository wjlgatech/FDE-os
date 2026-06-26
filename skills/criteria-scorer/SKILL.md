---
name: criteria-scorer
description: Score any text artifact against a list of binary pass/fail criteria, offline and deterministically — the simplest, most general artifact eval. Each criterion is a typed, mechanically-checkable rule (word count, required regex, forbidden buzzwords, "contains a concrete number", "has a citation"). Returns a 0–1 score + a pass/fail gate naming each failed criterion. Use to gate content/prompt/doc quality, or as a pluggable scorer inside eval-loop. Deterministic core, no network; subjective judgment is an opt-in LLM hook, not part of the core.
---

# criteria-scorer

> The third gate, alongside `true-scorer` (0–3 rubric) and `rag-eval-harness` (retrieval metrics).
> This one is the *general* artifact eval: a list of binary questions, each mechanically checkable.
> Principle (from the source article): the biggest single quality lever is often a checkable rule —
> *"force a concrete number"* is just `must_contain_number`.

## Criterion types (deterministic, offline)

| type | value | passes when |
|---|---|---|
| `min_words` | int | artifact has ≥ value words |
| `max_words` | int | artifact has ≤ value words |
| `must_match` | regex | artifact matches the regex (case-insensitive) |
| `must_not_match` | str or [str] | artifact matches none (e.g. a buzzword list) |
| `must_contain_number` | — | artifact contains a digit |
| `must_cite` | — | artifact has a `[bracket]` or `http(s)` citation |

An unknown `type` is an explicit error, never a silent pass. Subjective criteria ("is the tone
right?") are an **opt-in LLM-judge hook** beyond this core — not promised here (same posture as
`rag-eval-harness`).

## Run it

```bash
python3 skills/criteria-scorer/scripts/criteria_score.py score <artifact.md|-> <criteria.json> --threshold 0.8
```

Criteria file = a JSON list of `{"question","type","value"}`. See
`examples/launch-announcement-criteria.json`. Score = mean of pass/fail (0.00–1.00); the gate blocks
below the threshold and names each failed criterion.

## Use as a pluggable scorer

`score_artifact(text, criteria)` and `gate(score, threshold, results)` are pure functions —
`eval-loop` wires them (and `true-scorer` / `rag-eval-harness`) interchangeably behind one loop.

## Verify

```bash
python3 -m unittest discover -s skills/criteria-scorer/tests -p 'test_*.py'
```

11 tests: every criterion type (pass + fail), the number/citation/buzzword cases, unknown-type error,
the gate threshold, determinism, and the example criteria file scoring a crafted artifact.

## Provenance

Built for FDE-os (eval-loop plan, U1) from the binary pass/fail eval style in
`docs/research/sources/2026-agent-loops-self-fixing.md`. Gate shape mirrors `true-scorer`.
