---
name: jd-compiler
description: Compile a Forward-Deployed-Engineer job description into structured competency knowledge — which FDE competency clusters it requires, the specific tools/frameworks it names, its seniority/level — and aggregate many JDs into a cross-company competency-demand matrix that feeds the knowledge base. Use to turn raw JDs (Google, Reflection, CVS, …) into a grounded, queryable picture of what the FDE market actually demands, and to grow the knowledge spine. Deterministic offline core; pairs with knowledgefy (notes → spine) and the course prep curricula.
---

# jd-compiler

> Idea **I1** from the FDE-os ideation, made runnable: *a JD is the input → competency knowledge.*
> The repo's knowledge base was thin and the demand signal was **locked inside prose JDs**; this
> unlocks it deterministically, then `knowledgefy` turns the output into a navigable competency spine.

## Why this exists

Real job descriptions are the ground truth for "what an FDE must be able to do" — but that signal sits
in prose, per-company, un-aggregated. `jd-compiler` extracts it: per JD, which of the FDE competency
clusters it requires and the **specific** tools it names; across JDs, **what recurs** (the load-bearing
core) versus **what's stack-specific** (e.g. GCP's Vertex/ADK shows up only in Google's posting).

## What it extracts (the FDE competency taxonomy)

Six clusters + a post-training stretch — the same spine the [course prep](../../course/prep/) uses:
`production_swe` · `enterprise_deploy` · `modern_ai_stack` · `agentic_design` · `fde_craft` ·
`leadership` · `post_training`. Plus a named-tool library (languages, agent frameworks, protocols
like **MCP**, vector DBs, LLM providers, deploy stack, eval/observability, ML, agent patterns) and
the role's years/level.

## Run it

```bash
# one JD -> a competency profile (prose note, or --json)
python3 scripts/jd_compile.py compile course/target-jds/google-cloud-fde.md
python3 scripts/jd_compile.py compile course/target-jds/reflection-ai-fde.md --json

# many JDs -> a cross-company demand matrix + a knowledgefy vault of prose notes
python3 scripts/jd_compile.py matrix course/target-jds/*.md --note knowledge/vault/jd-competencies

# then grow the knowledge base: vault -> competency spine
python3 ../knowledgefy/scripts/knowledgefy.py build knowledge/vault/jd-competencies/ \
  --out knowledge/jd-competency-spine.graph.json --html knowledge/jd-competency-spine.html
```

The `matrix --note` step writes one prose competency note per JD + a `_cross-company-synthesis.md`;
feeding that vault to `knowledgefy` is what literally **fills up the knowledge base** (the competency
spine grows as you add JDs).

## How an agent uses it

1. Capture a JD as markdown under `course/target-jds/` (reading a live web posting into clean markdown
   is the upstream step — this core scores the markdown, deterministically).
2. `compile` it to see the role's competency profile, or `matrix` a set to see cross-company demand.
3. `--note` + `knowledgefy` to grow the competency spine; the course prep curricula and the
   `reflection-lead-readiness-scorecard` consume the same competency vocabulary.

## Boundaries

Deterministic, offline — keyword extraction over a curated taxonomy, not an LLM read; it will miss a
competency a JD phrases unusually (extend the `CLUSTERS` / `TOOLS` tables in `scripts/jd_compile.py` as
the field teaches you new vocabulary — that's the flywheel). `knowledgefy` extracts *concepts* from the
note headings; add a JD's source **URL** to its note to also get grounded evidence nodes.
