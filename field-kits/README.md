# Field Kits

**Field Kits are the reusable, forkable assets that ship with every Delta article** — the "R" in [TRUE](../Delta-TRUE-article-spec.md). Each one turns a mental model from the writing into something an AI agent (or a human + agent) can actually *run*. Together they accumulate into FDE-os's cross-agent tooling layer (Objective 2).

The rule: **every Delta Field Manual ships exactly one Field Kit.** Writing the series builds the toolkit.

## What a Field Kit is

A small, self-contained, runnable artifact — drawn from this menu:

- **Agent skill** (`SKILL.md`) — a forkable skill for Claude / agents
- **Prompt** / mega-prompt — a runnable prompt for a specific FDE task
- **MCP server spec** — a small, named server definition
- **Checklist / SOP** — e.g. a deployment pre-flight, a discovery checklist
- **Decision tree / framework canvas** — e.g. "Dev vs Delta: which is this work?"
- **Eval rubric** — a scoring rubric an agent can apply
- **Template** — Site Survey, Technical Scoping/PRD, Weekly Exec Summary
- **Workflow / runbook** — a multi-step repeatable procedure

## Convention

```
field-kits/
  <kit-slug>/
    SKILL.md          # or PROMPT.md / TEMPLATE.md / RUBRIC.md, per type
    (optional) examples/, assets/
```

Each kit names its **source article**, its **type**, and **how to run it**. Mark unknowns as RISKS — never invent.

## Index

| Kit | Type | From | Use it when |
|---|---|---|---|
| [`delta-discovery-protocol`](delta-discovery-protocol/SKILL.md) | Agent skill | [Field Manual 01 — The Delta Loop](../Delta-01-field-manual.md) | Starting a new deployment/engagement; requirements feel thin or too clean; before writing production code. Outputs a structured **Site Survey**. |

*More kits land as the Delta series ships. Each post → one kit.*

## How to fork

1. Copy the kit folder into your own agent stack (Claude skills dir, repo, etc.).
2. Adapt the slugs/prompts to your domain.
3. Run it on a real engagement — then feed what breaks back here (Objective 3, the flywheel).
