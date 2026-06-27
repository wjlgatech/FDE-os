# Changelog

All notable changes to FDE-os are recorded here. Format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Changed
- **Redesigned the landing page (`index.html`) in Anthropic's house style.** Replaced the dark
  ink/amber/green gradient theme with a warm-ivory editorial system: `Newsreader` serif display
  headlines + `Hanken Grotesk` body, a single clay accent (`#CC785C`), flat surfaces, hairline
  borders, generous whitespace, and a staggered hero fade-up (reduced-motion–safe). All copy, the
  signup form logic, and the JS config block (`OWNER_EMAIL`/`KIT_FORM_ID`/`FORMSPREE_ID`/
  `DISCORD_INVITE`) are unchanged — purely a visual reskin, verified via headless-Chrome screenshot.
  _Why: the previous design read as generic dark-SaaS; the site is the project's first impression and
  the front door of the go-live flywheel, so it should look like the calm, credible thing it is._
- **Folded the published long-form's human edits back into the repo (the flywheel closing).** After
  the article was published on LinkedIn, captured the editing taste it revealed — data-led title, an
  operational `Deploy → Observe → Build → Validate → Productize → Repeat` loop, and a probabilistic-
  nature "why now" framing — into `docs/marketing/fde-os-longform-article.md` (re-scored 11/12, still
  PASS) and systematized it as reusable defaults in `Delta-viral-playbook.md`. _Why: the human's 10%
  taste is exactly the field signal the flywheel is meant to capture and reuse._

### Added
- **`docs/marketing/` — copy about the project, gated by its own tools.** A long-form (~7 min)
  article + two ~185-word feed posts about FDE-os: 15-yo-legible, director-deep, with a sense of
  humor. Dogfooded through the project's own gates before shipping — the article scores **11/12**
  via `true-scorer`, both short posts **4/4** via `criteria-scorer` (+ a reusable `viral-post-criteria.json`).
  _Why: a project about eval-gated honesty should gate its own marketing; the scores are the proof._
- **`ARCHITECTURE.md` + three Anthropic-style README infographics.** New system-design doc, and
  hand-authored SVG infographics (`docs/assets/flywheel.svg`, `architecture.svg`, `roadmap.svg`) in a
  cream/ink/rust palette, embedded in README. Self-contained backgrounds (render in GitHub light AND
  dark mode), no scripts/external refs (survive GitHub's SVG sanitizer); verified via screenshot.
  _Why: the repo grew to 7 skills + CI + site + course + research with no single visual/system
  overview; the roadmap plan stays immutable, so the architecture doc is the right home for it._
- **`skills/criteria-scorer` + `skills/eval-loop` — the self-improving artifact primitive.** From the
  agent-loops critical eval: `criteria-scorer` scores any artifact against binary pass/fail criteria
  (typed, mechanically-checkable predicates) → 0–1 + a gate (11 tests); `eval-loop` turns scored
  versions into a kept winner + a run-log (Round │ Change │ Score │ Verdict), keeping only strict
  improvements and reverting regressions, git as memory (8 tests). Plan:
  `docs/plans/2026-06-26-001-feat-eval-loop-and-criteria-scorer-plan.md`. _Why: FDE-os had the scorers
  and the memory but not the explicit eval-loop; now it does — deterministic, offline, dogfoodable._
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

- **CVS Agentic AI Engineer JD prep + deepened eval cluster:**
  `course/target-jds/cvs-agentic-ai-engineer.md` (structured JD target, honestly framed as
  FDE-adjacent) + `course/prep/cvs-agentic-ai-engineer-prep.md` (dual-tier curriculum) +
  `course/prep/lessons/rag-evaluation.md` (a full concept-first lesson on evaluating RAG/agent
  systems) + **`skills/rag-eval-harness`** — a runnable, offline, deterministic eval skill (17
  tests): retrieval metrics (precision@k, recall@k, MRR, hit-rate) + grounding/hallucination proxy
  + citation coverage + a CI-able pass/fail gate. _Why: makes the JD→prep pattern repeatable and
  deepens one cluster from spec into shipped lessons + a real tool (eval is the load-bearing
  applied-AI skill, doubly so for healthcare)._

- **`skills/fde-mcp-server`** — a minimal, dependency-free **Claude MCP server** (stdio JSON-RPC 2.0)
  exposing FDE-os's skills as MCP tools (`true_score`, `rag_eval`). Implements
  initialize/tools/list/tools/call with a pure, unit-tested `handle_request` (11 tests); verified
  end-to-end over real stdio. _Why: a runnable answer to the common JD hard-requirement "1+ Claude
  MCP integrations", and it dogfoods the repo (skills become callable tools)._

- **Live website (GitHub Pages):** renamed the landing page `delta-community-landing.html` →
  `index.html`, added `.nojekyll`, and enabled GitHub Pages so the Delta community door is live at
  **https://wjlgatech.github.io/FDE-os/**. Updated all mutable references to the new path. _Why: the
  viral Post #1's first-comment link needs a real public URL to point at — the page existed only
  locally before, which blocked publishing._

- **`docs/research/` — external-source vault + critical evals.** Saved + deep-researched the 2026
  "Agent Loops that fix themselves" guide (Aakash Gupta et al.; reposted verbatim by Ng & Saboo —
  flagged as one source, not two) and its reference repo `aakashg/pm-github-workflow-repo`. Wrote a
  critical evaluation vs. FDE-os: core is real + tri-objective-aligned, framing is hype; identified
  the one missing primitive (an explicit eval-loop with a keep/revert run-log). _Why: methodology
  input that directly informs the roadmap; kept separate from the FDE-domain vault._

### Fixed
- **Landing-page signup now actually captures + never lies.** The unwired form previously told a
  live visitor "You're in" while saving nothing. Reworked the handler: set `KIT_FORM_ID` *or*
  `FORMSPREE_ID` for automated capture; until then a signup opens the visitor's mail app addressed to
  `OWNER_EMAIL` (no lead dropped, honest copy). _Why: the page is publicly live — a false success on
  a static page with no backend silently loses real founding-member leads._
- **Freshness checker stripped markdown emphasis from bare URLs** — a `**https://…**` (bold) link
  was captured with its trailing `**`, producing a false 404. Added `*` and `_` to the trailing-strip
  set. Caught by the checker flagging its own README URL.
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
