---
name: snowflake-os
description: "The Snowflake curriculum operating system — turns learn.snowflake.com (58 courses, 12 exams, 12 role journeys, 5 tracks) into a provenance-pinned knowledge base plus runnable tooling: search the catalogue, plan the shortest costed path to a role or exam, and GO/NO-GO someone's readiness on verified evidence. Offline, stdlib-only, CI-gated. Use for any 'what should I learn / is this person ready / what does this cost' question about Snowflake."
---

# /snowflake-os — the curriculum layer for Snowflake

Every agentic Snowflake tool that exists operates on the **warehouse**: Snowflake's own
`Snowflake-Labs/mcp` runs Cortex tools, `cocoplus` orchestrates data-engineering agents,
`coco-skills` ships Cortex Code skills. None of them operates on the **curriculum**.

So `/snowflake-os` takes the layer nobody occupies:

| layer | question | who |
|---|---|---|
| **doing** | run the query, ship the pipeline, deploy the agent | `Snowflake-Labs/*` (registered here as satellites) |
| **becoming** | which of 58 courses makes someone able to, in what order, at what cost, proven how | **snowflake-os** |

It is not a competitor to `cocoplus` (which already calls itself an agentic OS for Snowflake) —
it is the layer underneath the one that repo works on. Every external tool is a **pointer with a
pinned SHA**, never a fork.

**The contract:** claimed ≠ measured · no evidence ⇒ no · an honest ❌ beats a fake ✅ · every gate
exits non-zero so CI can enforce it. The knowledge base carries the URL and sha256 of the page
each fact came from. Every fenced command below is executed by
`skills/snowflake-os/tests/test_snowflake_os_examples.py` — a rotted demo turns the build red.

## 0. Get it

```text
Claude Code plugin:  /plugin marketplace add wjlgatech/FDE-os  →  /plugin install fde-os@fde-os
Any agent w/ shell:  git clone https://github.com/wjlgatech/FDE-os && cd FDE-os && make check
MCP (any client):    python3 skills/fde-mcp-server/scripts/server.py
                     tools: snowflake_plan · snowflake_readiness · snowflake_catalog
```

## 1. Route the ask

| You want… | Run |
|---|---|
| **What's in the catalogue, and what do we NOT know** | `catalog.py stats` |
| **Find a course** (deterministic term overlap; zero results names the vocabulary) | `catalog.py find <terms> [--free]` |
| **One course with its provenance** | `catalog.py show <CODE>` |
| **The distinct exams** (localised pages collapsed to real exams) | `catalog.py exams` |
| **What builds a competency, and how much is our judgment** | `catalog.py competency <id>` |
| **The shortest ordered path to a role / exam** | `pathfinder.py plan --role <slug>` · `--exam <CODE>` |
| **Is this person ready?** GO/NO-GO on verified evidence | `readiness.py score <contract.json>` |
| **Can I staff them, and if not what's the fix** | `workflows/snowflake-enablement/run.py <bundle.json>` |
| **Is the knowledge base itself sound** (10 checks) | `gate.py` |
| **External Snowflake tooling** (pointers, licences, quarantine) | `catalog.py satellites` |
| **Refresh from Snowflake** (the ONLY networked command) | `sync.py fetch` · `sync.py drift` |
| **Rebuild the curated spec / the graph** | `build.py` · `graph.py build --out … --html …` |

## 2. Verified demos (run from the repo root — each is CI-tested)

### The knowledge base — and what it admits it doesn't know

```bash
# 58 courses, 12 exams, 5 tracks, 12 roles — with an UNMEASURED tally, not a clean lie
python3 snowflake-os/scripts/catalog.py stats  # exit 0
# 10 integrity checks over provenance, references, fake passes and curated share
python3 snowflake-os/scripts/gate.py  # exit 0
# The compiled spec still matches its YAML source (sha256), or the build is stale
python3 snowflake-os/scripts/build.py --check  # exit 0
```

### Search — and an honest zero

```bash
# Free Snowpark courses, cheapest first
python3 snowflake-os/scripts/catalog.py find snowpark --free  # exit 0
# One course, with the URL and page-hash it was parsed from
python3 snowflake-os/scripts/catalog.py show OD-ESS-DWW  # exit 0
# Zero matches NEVER fail silent: a diagnostic names the real vocabulary — exit 2
python3 snowflake-os/scripts/catalog.py find quantum knitting  # exit 2
```

### Plan — a goal becomes an ordered, costed path

```bash
# The FDE path, free courses only: ordered by Snowflake's OWN published track order where it exists
python3 snowflake-os/scripts/pathfinder.py plan --role forward-deployed-engineer --free-only  # exit 0
# Target an exam instead of a role, skipping what you've already done
python3 snowflake-os/scripts/pathfinder.py plan --exam GES-C02 --have OD-SXGA,OD-SXGA2  # exit 0
# A 12-hour budget truncates the plan and SAYS what it dropped
python3 snowflake-os/scripts/pathfinder.py plan --role ml-engineer --free-only --max-hours 12  # exit 0
```

### Prove it — claimed completions score zero

```bash
# Mixed evidence: 10 badges, 2 screenshots, 2 intentions. Only badges count -> NO-GO, exit 2
python3 snowflake-os/scripts/readiness.py score snowflake-os/examples/fde-readiness.json  # exit 2
# Every core competency covered by verifiable evidence -> GO, exit 0
python3 snowflake-os/scripts/readiness.py score snowflake-os/examples/fde-ready.json  # exit 0
```

### Compose — the staffing verdict, with the remediation attached

```bash
# KB integrity AND readiness; a NOT-YET ships the shortest path to yes — exit 2
python3 workflows/snowflake-enablement/run.py workflows/snowflake-enablement/examples/candidate.json  # exit 2
```

### The satellites and the graph

```bash
# 6 Snowflake-Labs repos as SHA-pinned pointers; 2 quarantined on licence grounds
python3 snowflake-os/scripts/catalog.py satellites  # exit 0
# Recompile the navigable spine (deterministic — byte-identical on rebuild)
python3 snowflake-os/scripts/graph.py build --out /tmp/sfos-graph.json  # exit 0
```

### MCP — the curriculum as callable tools

```bash
printf '{"jsonrpc":"2.0","id":1,"method":"tools/list"}\n' | python3 skills/fde-mcp-server/scripts/server.py  # exit 0
```

## 3. Report results faithfully

Relay each engine's verdict verbatim — **NO-GO, NOT-YET and exit 2 are working features**, not
errors to apologise for. Three habits specifically:

- When you quote a plan, quote its **curated share** too. A large part of the role→course map is
  snowflake-os judgment, because Snowflake publishes none — say so rather than implying authority.
- When a field is **not measured** (Specialty exam pricing, role course lists, one track's
  sequence), say "not measured". Never substitute a plausible number sitting nearby on the page.
- The snapshot has a `fetched_at`. If it looks old, run `sync.py drift` and report what it says
  instead of assuming the catalogue is unchanged.

If an ask routes to no engine here, say so and point at `catalog.py satellites` (the warehouse-layer
tools) — never improvise a capability.

## 4. Honest edges

- **The role→course map is ours.** All 12 of Snowflake's role-journey pages describe the role in
  prose and link the catalogue, not courses. `data/competencies.yml` supplies the missing edge as
  labelled judgment; `gate.py` caps the curated share at 40% so it cannot quietly become opinion.
- **Specialty exam pricing is unknown.** Each exam page repeats a boilerplate FAQ quoting $175
  (Core) and $375 (Advanced). Specialty prices appear nowhere, so they are recorded as unmeasured
  rather than borrowing the number next to them.
- **Effort hours are Snowflake's estimate**, not a measurement of anyone's actual time.
- **`coco-skills` ships no licence** and `subagent-cortex-code`'s is unidentified — both are
  index-only and marked unvendorable; the gate fails if anyone flips that.
- **No Snowflake account is under test.** Claims about the managed MCP server are cited, not verified.

## 5. See also

`snowflake-os/data/sources.yml` (the ingest spec) · `snowflake-os/data/competencies.yml` (the
curated layer) · `snowflake-os/data/satellites.yml` (the boundary) ·
`knowledge/snowflake-catalog.html` (the navigable spine) · `skills/fde-os/SKILL.md` (the wider
FDE-os toolkit this plugs into).
