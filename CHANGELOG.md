# Changelog

All notable changes to FDE-os are recorded here. Format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added
- Staged roadmap plan: `docs/plans/2026-06-20-001-feat-fde-os-staged-roadmap-plan.md`
  (6 stages, Delta-content-first spine), reviewed by 6 persona agents.
- **Test CI** (`.github/workflows/tests.yml`) — auto-discovers and runs every `skills/*/tests`
  suite + the Field Kit convention lint on each push/PR. _Why: 23 tests existed but nothing ran
  them automatically; closes U8's "wire the lint into CI" loose end and the no-test-CI gap._
- **`STATUS.md`** — the one-glance "where are we now" board (done / blocked / next, keyed by U-ID
  + PR). Establishes the 3-layer convention: CHANGELOG = what shipped, plan = decisions (immutable),
  STATUS = the glance. _Why: track progress without turning the plan into a drift-prone checklist._
- **`flywheel/go-live-runbook.md`** — the ~30-min human checklist that unblocks Stage 1 (wire the
  Kit form, stand up the rooms, publish Post #1) and the exact Gate-A criteria to record. _Why:
  every remaining roadmap unit is gated behind these owner-only ops actions; this makes them
  frictionless instead of a vague "blocked on you."_
- **U8 — `field-kit-generator` skill:** scaffolds + lints a Delta Field Kit to convention
  (Field Kit menu, names-source, marks-RISKS, folder layout); delegates synthesis to `skillfy`
  (thin wrapper, KTD5). 9 passing tests; lint passes the real Post #1 kit and fails malformed
  ones. Its `lint` subcommand is the field-kits index-lint U1 referenced but hadn't shipped.
  _Why: every post ships exactly one convention-correct Field Kit (R1). Tooling built ahead;
  Stage 2 content (posts 2–4) stays gated on Gate B._
- **`AGENTS.md`** — agent-facing guide (repo map, native skills, conventions, stage gates);
  `README.md` synced with what Stage 0 shipped + a repository-structure table.
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
- **U4 — `true-scorer` skill:** the TRUE 0–3 rubric as a runnable publish gate
  (`skills/true-scorer/`, 8 passing tests). Deterministic gate (total ≥ 10 AND every letter ≥ 2)
  + structural heuristic baseline an agent refines; scores Post #1 at 12/12. _Why: no Delta post
  ships un-scored (R2)._
- **U5 — owned-hub wiring (code):** `delta-community-landing.html` CTA now POSTs to ConvertKit/Kit's
  public form-action endpoint (no secret exposed client-side); async success/error handling +
  GDPR/unsubscribe footer note. Form id is a stub (`KIT_FORM_ID`) pending go-live; unconfigured
  state confirms locally so the page stays testable. _Why: own the list (KTD2); subscriber PII
  needs a compliant baseline (R3)._
- **U7 — pipeline metrics ledger:** `flywheel/metrics.md` — per-post funnel (reach, saves,
  read-through, owned-list conversions, kit forks, war-story replies, kit-usefulness) plus the
  encoded **Gate A** (Stage 1→2) and **Gate B** (Stage 2→3/4) thresholds. _Why: make the
  traction-funds-heavy-stages bet falsifiable, not automatic._

### Changed
- Added `.gitignore` (Python `__pycache__`/`*.pyc`, OS cruft, `.env` secrets) and untracked the
  `__pycache__/*.pyc` files that slipped into the Stage 0 merge.

- **Objective-1 prep material (JD-validated):** `course/target-jds/reflection-ai-fde.md` (the
  Reflection AI FDE JD as a structured course-validation target) + `course/prep/reflection-ai-fde-prep.md`
  (a dual-tier prep curriculum: every competency ships human knowledge **and** a forkable agent tool,
  plus an eval-as-gate readiness rubric) + a flagship agent tool
  `course/prep/tools/agentic-solution-architect/SKILL.md` (Site Survey → agent architecture, composes
  with the Delta Discovery Protocol). _Why: makes Objective 1 concrete against a real JD; the TRUE
  model means prepping for the role also builds the applicant's cross-agent toolkit (Objective 2)._

### Fixed
- **Two truncated citations in the research vault** — the freshness CI flagged two
  `newsroom.accenture.com/news/2026/...` URLs as 404. Web-verified the underlying claim: it is
  **real and well-sourced** (Accenture+Microsoft FDE Practice, Mar 18 2026; ServiceNow+Accenture
  FDE Program, Knowledge 2026 May 6 2026 — corroborated by Businesswire/Nasdaq/ServiceNow). Root
  cause was a URL **truncated mid-slug with `...`** in the vault, not a bad claim. Restored the
  full canonical URLs (both 200 OK) and regenerated the spine (evidence back to 39). _Why: R4 —
  keep the vault's facts live-sourced, but don't cut a true claim over a typo'd link._

### Investigated / Rejected
- **`living-repo` as the vault knowledge-graph builder** — rejected: its parser is GFM-table-only
  and extracted just 5 nodes from `FDE-research-synthesis.md`, missing all 12 headings and 40
  citations (the prose body). Measurement: `awesome_kg.py build` → 5 nodes / 4 edges.
- **`kgfy`/`dreammaketrue` as the vault builder** — rejected for the local-first base path: the
  graph store (Neo4j) is down and the skill needs a heavyweight engine running. Measurement:
  `dmt.py status` → `graph: down (ServiceUnavailable)`. This is the offline/local friction KTD3
  named; a lean stdlib `knowledgefy` fills the gap instead.
