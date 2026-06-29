# FDE-os native skills

FDE-os-native agent skills — designed **only where existing skills leave a real gap** (KTD3/KTD9
in the [roadmap plan](../docs/plans/2026-06-20-001-feat-fde-os-staged-roadmap-plan.md)). Existing
skills (`living-knowledge`, `skillfy`, `dreammaketrue`, `knowledge-graph`, `living-repo`) are
reused as the production engine and are **not** vendored here.

| Skill | Purpose |
|---|---|
| `knowledgefy/` | Local-first, offline, deterministic: a prose research vault → navigable knowledge spine |
| `true-scorer/` | The TRUE 0–3 rubric as a runnable publish gate |
| `criteria-scorer/` | Score any artifact against binary, mechanically-checkable pass/fail criteria → 0–1 + gate |
| `rag-eval-harness/` | Score a RAG/agent eval set offline — retrieval metrics + grounding proxy + citation coverage |
| `eval-loop/` | Turn a sequence of scored versions into a kept winner + a run-log (the self-fixing loop) |
| `field-kit-generator/` | Thin wrapper over `skillfy` enforcing the Field Kit menu + convention |
| `invisible-workflow-mapper/` | Reconstruct an org's decision workflow from partial signals → adoption-readiness + archetype + probes |
| `jd-compiler/` | Compile JDs → FDE competency knowledge; aggregate many into a cross-company demand matrix that grows the knowledge spine |
| `fde-mcp-server/` | A minimal MCP server exposing these skills as callable tools to any MCP host |

Each skill ships a `SKILL.md` and, where it has a runnable core, a `scripts/` entrypoint + `tests/`.
