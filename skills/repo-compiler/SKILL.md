---
name: repo-compiler
description: Compile every top-rated repo the hub cites into a knowledge graph + an agentic-tooling entry (skill contract with honest notGoodAt + an integration recipe as discovery-source / plugin-dependency / workflow-organ / course-citation), from a single repos.yml registry. GitHub-API-only (no clones), deterministic, SHA-pinned provenance, incremental refresh that exits non-zero on drift so CI can gate freshness. Use when the hub cites a new repo, when checking whether compiled knowledge is stale, or to regenerate the hub's knowledge+tooling layer from scratch.
---

# repo-compiler

> FDE-os is a hub of **knowledge · tooling · experts**. The repos it cites are load-bearing, so
> each top-rated one is compiled into both a **knowledge graph** and an **agentic-tooling entry**
> — by a factory, not by hand. Registry: [`knowledge/hub/repos.yml`](../../knowledge/hub/repos.yml).
> Deep-dive on the design: [field note](../../docs/field-notes/2026-07-19-hub-factory-deep-dive.md).

## Run it

```bash
# everything in the registry above the star bar (default 1000)
python3 skills/repo-compiler/scripts/repo_compile.py all

# one repo, ad hoc
python3 skills/repo-compiler/scripts/repo_compile.py compile langfuse/langfuse --why "eval-obs organ"

# freshness check — exit 3 on drift (CI/cron-able)
python3 skills/repo-compiler/scripts/repo_compile.py refresh

# progressive disclosure — retrieve toolsets on trigger (also the `hub_find` MCP tool)
python3 skills/repo-compiler/scripts/hub_query.py find LLM observability evals
python3 skills/repo-compiler/scripts/hub_query.py recipe fastmcp
python3 skills/repo-compiler/scripts/hub_query.py list
```

Outputs under `knowledge/hub/`: `<slug>.graph.json` per repo, `hub-skills.json` (the tooling
registry), `hub-index.json` (compile status + pinned SHAs — what `refresh` diffs against).

## What each repo becomes

- **Knowledge graph** — knowledgefy-shaped: the repo node (stars/license/kind/why-cited), topic
  nodes, concepts from README headings (nesting → `part_of`), evidence from README links
  (`cites`). Every node carries **SHA-pinned provenance** — blob URLs that can never drift.
- **Tooling entry** — a skill contract: `oneLine`, `useWhen` (why-cited + topics), a non-empty
  **`notGoodAt`** derived from the repo's kind (a curated index "can't run anything itself —
  popularity ≠ safety"; a platform "isn't zero-ops"; missing license ⇒ an extra honest edge), and
  an **integration recipe**: how the hub should consume it — `discovery-source`,
  `distribution-surface`, `workflow-organ`, `plugin-dependency`, `course-citation`, or
  `skill-candidate`.

## The five commitments (quality · fast · cheap · fresh · future-proof)

1. **Quality is enforced, not hoped for** — `validate_graph` rejects dangling edges and any node
   without http(s) provenance; compile aborts on violation. Empty READMEs are announced loudly
   (a 91k-star repo once produced a silently hollow graph because the JSON API returns empty
   content past 1MB — the fetcher now uses the raw media type and warns).
2. **Fast** — ~3 API calls per repo, no clone, no LLM. Full 7-repo hub compile: seconds.
3. **Cheap** — $0: `gh` auth, stdlib + pyyaml, deterministic.
4. **Up-to-date** — `refresh` costs 1 call/repo, reports exactly which repos drifted
   (old→new SHA), exits 3 so a weekly CI job turns staleness into a red build, and `all`
   rebuilds only what you choose.
5. **Future-proof** — the registry is spec-as-data; the `GitHubFetcher` seam is swappable
   (GitLab/local mirror) without touching extraction; outputs carry `contractVersion`;
   unreachable repos are reported stale (exit 4), never silently dropped or faked.

## Boundaries (honest edges)

- README-level knowledge only — it does **not** parse source code (that's `understand-anything`'s
  job; point it at a clone when code-level depth is worth the cost).
- The star bar ranks by popularity, which is *attention*, not correctness — `notGoodAt` says so
  on every curated-index entry.
- `hub-skills.json` entries are **candidates with recipes**, not installed tooling — a human (or
  an eval gate) still decides adoption per the supply-chain rule: read before you run.

## Verify

```bash
python3 -m pytest skills/repo-compiler/tests -q   # 16 tests, offline fixtures, no network
```
