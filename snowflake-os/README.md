# snowflake-os — the curriculum layer for Snowflake

**`learn.snowflake.com` → a provenance-pinned knowledge base → runnable, evidence-gated tooling.**

Snowflake's own org ships a strong agentic toolchain for *operating* a warehouse
(`Snowflake-Labs/mcp`, `cocoplus`, `coco-skills`, `snowflake-ai-kit`, `ai-ready-data`,
`subagent-cortex-code`). None of it touches the **curriculum**. The catalogue — 58 courses,
12 exams, 12 role journeys, 5 tracks — is not machine-readable anywhere, so no tool can answer:

> *Given where this person is going, what is the shortest ordered path through 58 courses,
> what does it cost, and how would I prove they actually got there?*

That is the layer snowflake-os occupies.

| layer | question | who |
|---|---|---|
| **doing** | run the query, ship the pipeline, deploy the agent | `Snowflake-Labs/*` — registered as SHA-pinned satellites, never forked |
| **becoming** | which courses make someone able to, in what order, proven how | **snowflake-os** |

## Quick start

```bash
python3 snowflake-os/scripts/catalog.py stats                            # what we know AND what we don't
python3 snowflake-os/scripts/pathfinder.py plan --role forward-deployed-engineer --free-only
python3 snowflake-os/scripts/readiness.py score snowflake-os/examples/fde-ready.json   # GO
python3 snowflake-os/scripts/gate.py                                     # 10 integrity checks
open knowledge/snowflake-catalog.html                                    # the navigable spine
```

Everything above is **offline, stdlib-only, deterministic**. `make snowflake-gate` is the finish line.

## Layout

```
snowflake-os/
├── data/                    SINGLE SOURCE OF TRUTH (human-authored YAML)
│   ├── sources.yml          the ingest spec: what to fetch, and by which stable anchors
│   ├── competencies.yml     the curated layer: competencies, alternatives, role→competency
│   └── satellites.yml       external Snowflake tooling: pointers + pinned SHAs + licence verdicts
├── snapshot/                GENERATED, committed, offline
│   ├── catalog.json         58 courses · 19 cert pages (12 exams) · 5 tracks · 12 roles, each with provenance
│   ├── competencies.json    compiled from the YAML (sha256-pinned to its source)
│   └── satellites.json      compiled from the YAML
├── scripts/
│   ├── sync.py              the ONLY networked component (fetch · drift)
│   ├── build.py             YAML → JSON, so the offline engines need no third-party parser
│   ├── catalog.py           the query engine (stats · find · show · competency · exams · satellites)
│   ├── pathfinder.py        goal → ordered, costed plan
│   ├── readiness.py         GO/NO-GO on verified evidence
│   ├── graph.py             → knowledge/snowflake-catalog.{graph.json,html}
│   └── gate.py              10 integrity checks; exit 1 on failure
├── examples/                a NO-GO contract and a GO contract — both branches proven in CI
└── tests/                   40 tests over behaviour, not over the snapshot's exact contents
```

Surfaces: `skills/snowflake-os/SKILL.md` (the `/snowflake-os` super tool),
`workflows/snowflake-enablement/` (the composition workflow), and three MCP tools in
`skills/fde-mcp-server` (`snowflake_plan`, `snowflake_readiness`, `snowflake_catalog`).

## The three rules that make it trustworthy

**1. Claimed never counts.** `readiness.py` credits a completion only when it carries a
`badge_url`, `completion_id` or `verifier`. A screenshot, a date, or "I did it" is reported in
full and scored **zero**. Someone who claims all 58 courses and can prove none scores 0.0 and
gets NO-GO. A learning plan that cannot fail is a brochure.

**2. No evidence means no.** Where Snowflake publishes nothing, the snapshot records
*not measured* rather than a plausible substitute. Concretely:

| what | status | why |
|---|---|---|
| course effort hours | measured, 58/58 | published on every course page |
| Core / Advanced exam price | measured | stated in the page's FAQ |
| **Specialty exam price** | **not measured** | every page repeats a $175/$375 FAQ that covers only Core and Advanced. The parser refuses to borrow the number sitting next to it |
| **role → course lists** | **not measured (0/12)** | all twelve role pages link the *catalogue*, not courses |
| **one track's sequence** | **not measured (1/5)** | `snowpro-core-study` links no courses |

**3. Curation is labelled and capped.** Because Snowflake publishes no role→course edge,
`competencies.yml` supplies it — every mapping tagged `title` (checkable in a title),
`objective` (checkable in a published exam objective) or `curated` (our judgment). Every plan
reports its curated share, and `gate.py` fails the build if curation exceeds **40%** of all
mappings (currently 31%). It is easy to "cover" a role by inventing mappings; the ceiling makes
that a build failure.

## Refreshing from Snowflake

`sync.py` is the only thing that touches the network, and it never runs in the gate:

```bash
make snowflake-sync          # fetch → rebuild spec → rebuild graph, then open a PR
python3 snowflake-os/scripts/sync.py drift    # is the committed snapshot still true? exit 3 on drift
```

Politeness and provenance: serial requests at 1/sec, read-only GETs of public unauthenticated
pages, and every record stores the URL, the sha256 of the exact bytes parsed, and the timestamp.

## Honest edges

- **`learn.snowflake.com` serves no `robots.txt`** (HTTP 530, probed 2026-08-03) and
  `www.snowflake.com` bot-walls `curl` entirely. There is no crawl directive to obey and none to
  claim cover from — so the sync is rate-limited, read-only and weekly at most, and this is
  recorded in `data/sources.yml` rather than glossed.
- **The DOM is hostile by construction.** It is a Gatsby build whose class names are
  styled-components hashes that rotate every deploy, so the parser anchors only on URL path
  codes and visible label text. A renamed *label* yields "not measured"; it never yields a guess.
- **Curated track pages link legacy slugs** (`uni-essdww101`) that 301 to the canonical page
  (`OD-ESS-DWW`). Matching the literal slug produced an empty track sequence — a silent,
  plausible-looking wrong answer. The sync follows the redirect and records the alias map.
- **Effort hours are Snowflake's estimates**, not measurements of anyone's real time.
- **No Snowflake account is under test.** Anything said here about the managed MCP server is
  cited, not verified.
- **Two satellites are quarantined**: `coco-skills` ships no licence at all and
  `subagent-cortex-code`'s is unidentified by GitHub. Default copyright applies — we link and
  describe, never copy. `gate.py` fails if anyone marks either vendorable.
