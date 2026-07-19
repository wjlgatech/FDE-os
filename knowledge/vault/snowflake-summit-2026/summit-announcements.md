# Snowflake Summit 2026 — the agentic enterprise announcements

Source note (user-provided summary + verified web sources, captured 2026-07-17). The organizing
thesis across 26+ new capabilities: **agentic AI requires a governed enterprise context layer, not
just compute** ([Atlan summit recap](https://atlan.com/know/snowflake/summit-2026-announcements/),
[Flexera recap](https://www.flexera.com/blog/perspectives/snowflake-summit-2026/)).

## CoWork — the personal work agent

Formerly Snowflake Intelligence. A work agent for every knowledge worker: proactive insights,
workflow automation, generated deliverables (PDFs, decks) inside existing tools
([Snowflake builders blog](https://medium.com/snowflake/snowflake-summit-2026-summary-of-new-features-09f3d5ffeefe)).
Paired with CoCo (formerly Cortex Code) as the agent surfaces.

## Cortex Sense — enterprise memory

Automatically learns how the organization defines its business from query history, metadata, and
dashboards. Reported result: **83% agent accuracy with it vs 24% without** — the context layer, not
the model, is the accuracy lever
([Atlan](https://atlan.com/know/snowflake/summit-2026-announcements/)).

## AI Agent Identity (GA) — the security baseline

Every agent gets a cryptographic identity, per-agent RBAC, and a complete audit trail
([Futurum analysis](https://futurumgroup.com/insights/snowflake-summit-2026-four-infrastructure-bets-that-determine-whether-the-agentic-enterprise-delivers/)).
An agent is a principal, not a script: authenticate it, scope it, audit it.

## Horizon Context — governed metadata beyond Snowflake

Private preview. Collects metadata from outside systems (PostgreSQL, SQL Server, Tableau, Power BI,
dbt), enriches with column-level lineage and AI-generated documentation, activates via hybrid
semantic search ([Constellation Research](https://www.constellationr.com/insights/news/snowflake-summit-2026-context-custom-model-training-iceberg-v3)).

## Adaptive Compute — workload-aware engine

Automatically sizes, scales, and optimizes compute per query; no more hand-tuned warehouse sizes,
multi-cluster settings, or auto-suspend
([select.dev recap](https://select.dev/posts/snowflake-summit-2026-product-announcement-recap)).

## Openflow, Datastream, Iceberg v3 — the substrate

Openflow orchestrates data/AI pipelines; Apache Iceberg v3 hits GA; Datastream handles ingestion —
the infrastructure the agentic layer runs on
([Perficient takeaways](https://blogs.perficient.com/six-takeaways-from-snowflake-summit-2026/)).

## OpenAI models in Cortex

Snowflake and OpenAI signed a ~$200M partnership bringing frontier models directly to enterprise
data under Snowflake governance ([OpenAI announcement](https://openai.com/index/snowflake-partnership/)),
alongside Anthropic, Meta, Mistral models already in Cortex AI
([Snowflake AI](https://www.snowflake.com/en/product/ai/)).
