# Snowflake for data scientists — the seven essential features

The user-provided feature list, grounded per feature against official documentation
(captured 2026-07-17). These are the working surface an AI data scientist lives in daily.

## Snowpark for Python

Run Python (DataFrame API + UDFs/UDTFs + stored procedures) inside Snowflake's engine — the
computation moves to the data, not the data to a laptop
([Snowpark docs](https://docs.snowflake.com/en/developer-guide/snowpark/python/index)).
Lazily-evaluated DataFrames compile to SQL; the pandas API (Snowpark pandas) covers the
exploratory idiom.

## Snowflake Notebooks

A managed notebook surface inside Snowflake — SQL + Python cells against live warehouse data,
Git-backed, schedulable as jobs
([Notebooks docs](https://docs.snowflake.com/en/user-guide/ui-snowsight/notebooks)). Unifies the
data-science and data-engineering workflow in one governed place instead of exporting to local
Jupyter.

## Snowflake Cortex AI

Managed LLM functions (COMPLETE, EMBED, TRANSLATE, SENTIMENT…), Cortex Search (hybrid retrieval),
and Cortex Analyst (text-to-SQL over semantic models) — models from Anthropic, OpenAI, Meta,
Mistral run inside the governance boundary
([Cortex docs](https://docs.snowflake.com/en/user-guide/snowflake-cortex/overview)). RAG without
data leaving the platform.

## Zero-Copy Cloning

Instant metadata-only clones of tables/schemas/databases — full-scale experiment sandboxes with no
storage copy and no pipeline
([cloning docs](https://docs.snowflake.com/en/user-guide/object-clone)). Clone prod, test the
feature pipeline, drop it; time travel underneath.

## Snowflake Feature Store

Managed feature views over Snowflake data: define once, backfill, serve consistently to training
and inference — the train/serve skew killer
([Feature Store docs](https://docs.snowflake.com/en/developer-guide/snowflake-ml/feature-store/overview)).
Pairs with the Model Registry for end-to-end ML lineage.

## Data Governance and Security

Horizon: RBAC, dynamic data masking, row-access policies, object tagging, column lineage, and
audit — governance as a property of the platform, not a wrapper
([Horizon docs](https://docs.snowflake.com/en/user-guide/security)). The reason regulated
industries can run AI on it at all.

## Data Sharing and the Marketplace

Live, governed data sharing without copying — provider grants, consumer queries, always-current
([sharing docs](https://docs.snowflake.com/en/user-guide/data-sharing-intro)); the Marketplace
adds third-party datasets (market data, alternative data) as native tables
([Marketplace](https://www.snowflake.com/en/data-cloud/marketplace/)).
