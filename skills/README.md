# FDE-os native skills

FDE-os-native agent skills — designed **only where existing skills leave a real gap** (KTD3/KTD9
in the [roadmap plan](../docs/plans/2026-06-20-001-feat-fde-os-staged-roadmap-plan.md)). Existing
skills (`living-knowledge`, `skillfy`, `dreammaketrue`, `knowledge-graph`, `living-repo`) are
reused as the production engine and are **not** vendored here.

| Skill | Purpose | Status |
|---|---|---|
| `knowledgefy/` | Local-first, offline, deterministic: a prose research vault → navigable knowledge spine | building (U2) |
| `true-scorer/` | The TRUE 0–3 rubric as a runnable publish gate | building (U4) |
| `field-kit-generator/` | Thin wrapper over `skillfy` enforcing the Field Kit menu + convention | Stage 2 (U8) |

Each skill ships a `SKILL.md` and, where it has a runnable core, a `scripts/` entrypoint.
