# Changelog

All notable changes to FDE-os are recorded here. Format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added
- Staged roadmap plan: `docs/plans/2026-06-20-001-feat-fde-os-staged-roadmap-plan.md`
  (6 stages, Delta-content-first spine), reviewed by 6 persona agents.
- **U1 — repo spine + CI:** `skills/`, `course/`, `flywheel/`, `knowledge/` homes;
  self-contained link-freshness CI (`scripts/check_freshness.py` +
  `.github/workflows/freshness.yml`) that fails only on 404/410/dns-failure and warns on
  bot-walled (403/429) links. _Why: keep the repo's external references honest automatically._
- **U2 — `knowledgefy` skill:** local-first, offline, deterministic prose-vault → knowledge
  spine (`skills/knowledgefy/`, stdlib only, 6 passing tests). Headings → `concept` nodes,
  inline + bare-URL citations → `evidence` nodes; `graph.json` + self-contained `file://` HTML.
  _Why: the verified gap living-repo (table-only) and kgfy (needs engine) leave._
- **U3 — FDE knowledge spine:** `knowledge/fde-spine.graph.json` + `.html` generated from
  `FDE-research-synthesis.md` — 12 concepts (all 7 research Parts), 39 evidence nodes, 51 edges.
  _Why: the canonical spine every Delta post and course lesson draws from._

### Investigated / Rejected
- **`living-repo` as the vault knowledge-graph builder** — rejected: its parser is GFM-table-only
  and extracted just 5 nodes from `FDE-research-synthesis.md`, missing all 12 headings and 40
  citations (the prose body). Measurement: `awesome_kg.py build` → 5 nodes / 4 edges.
- **`kgfy`/`dreammaketrue` as the vault builder** — rejected for the local-first base path: the
  graph store (Neo4j) is down and the skill needs a heavyweight engine running. Measurement:
  `dmt.py status` → `graph: down (ServiceUnavailable)`. This is the offline/local friction KTD3
  named; a lean stdlib `knowledgefy` fills the gap instead.
