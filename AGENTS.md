# AGENTS.md — FDE-os

Agent-facing guide for this repo. Humans: see [`README.md`](README.md).

## What this project is

FDE-os is an operating system for becoming a **Forward Deployed Engineer**. Three objectives —
(1) a JD-validated course, (2) cross-agent FDE tooling, (3) a field-practice feedback flywheel —
ignited by **Delta**, a public content series. The build follows a reviewed six-stage roadmap:
[`docs/plans/2026-06-20-001-feat-fde-os-staged-roadmap-plan.md`](docs/plans/2026-06-20-001-feat-fde-os-staged-roadmap-plan.md).

Spine: **Delta-content-first.** Each post ships a Field Kit (builds Objective 2) and a war-story
prompt (seeds Objective 3). Content production *is* product production.

## Repo map

| Path | Role |
|---|---|
| `skills/` | FDE-os-native skills. Built only where existing skills leave a verified gap. Each has `SKILL.md` + (where runnable) `scripts/` + `tests/`. |
| `knowledge/` | Generated spine (`fde-spine.*`). Regenerate with `knowledgefy`; don't hand-edit. |
| `flywheel/` | Objective-3 infra + production runbook/metrics. Security-sensitive (Stage 3 handles real customer data, born-clean redaction). |
| `course/` | Objective-1 course. Stage 4 — reserved, gated on Stage-2 traction. |
| `field-kits/` | Forkable Field Kits, one per post. Convention: `field-kits/<slug>/SKILL.md`, names its source article, marks unknowns as RISKS (never invent). |
| `scripts/` | Repo tooling (`check_freshness.py`). |
| `docs/plans/` | The roadmap. Decision artifact — do not encode progress here; progress lives in git. |

## Native skills (current)

- **`knowledgefy`** — local-first, offline, deterministic: prose vault → `graph.json` + `file://`
  HTML. Headings → `concept` nodes; inline + bare-URL citations → `evidence` nodes. No network on
  the base path; semantic/lineage edges are an opt-in NIM-enrich pass only.
  Run: `python3 skills/knowledgefy/scripts/knowledgefy.py build <vault> --out <g.json> --html <g.html>`
- **`true-scorer`** — the TRUE rubric (T/R/U/E, 0–3 each) as a publish gate. **Gate: total ≥ 10
  AND every letter ≥ 2** (the AND is the point — a perfect total with one weak letter blocks).
  Run: `python3 skills/true-scorer/scripts/score.py <draft.md>` or `--scores T=3,R=3,U=2,E=2`.

**Reuse vs design:** existing skills (`living-knowledge`, `skillfy`, `dreammaketrue`,
`knowledge-graph`, `living-repo`) are the production engine and are NOT vendored. Design a native
skill only when a spike shows the existing ones genuinely fall short (see KTD3 in the plan).

## Conventions

- **Tests:** stdlib `unittest`, per skill. Run: `python3 -m unittest discover -s skills/<name>/tests -p 'test_*.py'`. Python 3.11. No third-party deps — keep skills stdlib-only and offline-by-default.
- **Determinism:** generated artifacts (the spine) must be byte-reproducible (sorted keys, stable ids). There is a test for this; don't break it.
- **Security:** anything touching field/customer data (Stage 3+) is born-clean — redact at capture, allow-list what may persist, fail-closed. Never route journal/portfolio data into an external engine.
- **Branches:** never commit to `main`. One branch per stage (`feat/fde-os-stage-N`), stacked. PRs are per-stage and scoped.
- **Docs sync (required, same change):** any feature change updates `CHANGELOG.md` (with an `Investigated / Rejected` note when an approach was killed), `README.md`, and this `AGENTS.md`. A plan doc does not substitute for the README.

## Stage gates

The roadmap is gated, not automatic. **Gate A** (Stage 1→2): Post #1 earned real traction, not just
that the pipeline ran. **Gate B** (Stage 2→3/4): a quantified traction floor across posts 1–4 funds
the heavy stages; if missed, iterate content — don't proceed. Stages 4–5 are separate follow-on
initiatives needing their own `ce-plan` pass. See the plan's "Stage Gates & Kill Signals".
