# AGENTS.md — FDE-os

Agent-facing guide for this repo. Humans: see [`README.md`](README.md).

## What this project is

FDE-os is an operating system for becoming a **Forward Deployed Engineer**. Three objectives —
(1) a JD-validated course, (2) cross-agent FDE tooling, (3) a field-practice feedback flywheel —
ignited by **Delta**, a public content series. The build follows a reviewed six-stage roadmap:
[`docs/plans/2026-06-20-001-feat-fde-os-staged-roadmap-plan.md`](docs/plans/2026-06-20-001-feat-fde-os-staged-roadmap-plan.md).

Spine: **Delta-content-first.** Each post ships a Field Kit (builds Objective 2) and a war-story
prompt (seeds Objective 3). Content production *is* product production.

## Repo map

| Path | Role |
|---|---|
| `skills/` | FDE-os-native skills (12: `knowledgefy`, `true-scorer`, `criteria-scorer`, `rag-eval-harness`, `eval-loop`, `field-kit-generator`, `invisible-workflow-mapper`, `jd-compiler`, `fde-mcp-server`, `doc-understanding`, `outcome-contract`, `repo-compiler`). `outcome-contract` gates an engagement on measured outcomes (GO/NO-GO; claimed ≠ measured). `repo-compiler` compiles every top-rated cited repo into a knowledge graph + tooling entry (see "External toolsets" below). `jd-compiler` compiles JDs (`course/target-jds/`) → competency knowledge + a cross-company matrix; `matrix --note` writes `knowledge/vault/jd-competencies/`, then `knowledgefy` builds `knowledge/jd-competency-spine.*` (extend its `CLUSTERS`/`TOOLS` tables as vocabulary grows). Built only where existing skills leave a verified gap. Each has `SKILL.md` + (where runnable) `scripts/` + `tests/`. `invisible-workflow-mapper` reconstructs an org's decision workflow from signals (adoption-readiness + archetype + probes, deterministic + gated) — deepens the `delta-discovery-protocol` field kit. To extend it, edit the `ARCHETYPES`/`PROBES`/`DIMENSIONS` tables in `scripts/workflow_map.py`. |
| `knowledge/` | Generated spine (`fde-spine.*`). Regenerate with `knowledgefy`; don't hand-edit. |
| `flywheel/` | Objective-3 infra + production runbook/metrics. `metrics.md` is the per-post funnel + the Gate A/B thresholds (the only owned metric is email conversions). Security-sensitive (Stage 3 handles real customer data, born-clean redaction). |
| `docs/field-notes/` | The flywheel's journal — real FDE engagements distilled into **transferable vs domain-specific** lessons + 3-pillar impact + tooling gaps. The synthesized counterpart to live war-stories in `contribute.html`. When a pattern recurs across notes, it's a candidate for a new skill/course module. Add a note as `docs/field-notes/<date>-<slug>.md` and index it in that dir's README. Redact client specifics (Objective-3 privacy rule). |
| `course/` | Objective-1 course. `target-jds/` = JD validation targets; `prep/` = worked dual-tier prep curricula (each competency = human knowledge + a forkable agent tool + an eval gate). The full Stage-4 course *engine* is still gated; per-JD prep material is built on request. |
| `field-kits/` | Forkable Field Kits, one per post. Convention: `field-kits/<slug>/SKILL.md`, names its source article, marks unknowns as RISKS (never invent). |
| `.claude-plugin/`, `.codex-plugin/` | Plugin packaging — the repo root **is** the plugin, for **two** runtimes off **one** `skills/` tree. `.claude-plugin/plugin.json` (+ `marketplace.json`, `source: "."`, wires `fde-mcp-server` via `${CLAUDE_PLUGIN_ROOT}`) → Claude Code; `.codex-plugin/plugin.json` (`"skills": "./skills/"` + `interface`) → Codex. Both point at the same `skills/`; CI (`tests/test_plugin_manifest.py`) keeps name/version/skills-target in lockstep. Skills auto-discover — adding one needs no manifest change. Hermes reads the same `SKILL.md` dirs directly (drop-in). OpenClaw needs a TS adapter (deferred). Cross-runtime map: `docs/RUNTIMES.md`; Claude install: `docs/PLUGIN.md`. |
| `tests/` | Repo-level invariants (not skill-specific) — currently the plugin-manifest validator. Discovered by CI (`tests.yml` globs `skills/*/tests workflows/*/tests tests`). |
| `workflows/` | **Composition** tools — a workflow chains skills (vs a skill = one capability). `engagement-readiness/run.py` lazy-imports `invisible-workflow-mapper` + `rag-eval-harness` cores and AND-s their gates into a GO/NO-GO (adds no new scoring). CI discovers `workflows/*/tests` (added to `tests.yml`). New workflows: import skill cores by repo-relative path, never re-implement their logic. |
| `take-home/` | **Interview-grade end-to-end builds** — each dir is a realistic take-home answered head-to-head against a real JD, with its own eval gate. `deloitte-agentic-triage/` = the six JD "thinking layer" terms as one durable agent graph (checkpoints, HITL interrupt/resume, hybrid retrieval + verifiable citations, session memory, budget-receipted context, monotonic guardrails, task-based eval vs ground truth). CI discovers `take-home/*/tests` (same finish line as skills). Its `graph.py`/`tools.py`/`retrieval.py`/`memory.py` are candidate cores for future skills — import, don't re-implement. |
| `web/`, `docs/reportcards/` | The **Journey webapp** (live: https://fde-os-journey.vercel.app) + its canonical card store. The anyagent accountability loop: every `/anyagent` turn records an evidence-backed report card into `docs/reportcards/collection.json`, syncs it (`anyagent report sync --to web`), and lands it via PR; redeploy with `cd web && vercel deploy --prod --yes` until git integration is wired. No evidence ⇒ no score. |
| `scripts/` | Repo tooling (`check_freshness.py`). |
| `index.html` | The Delta community landing page — served live via GitHub Pages at https://wjlgatech.github.io/FDE-os/. `.nojekyll` keeps Pages from running Jekyll. **Design system (keep new UI consistent):** Anthropic-style — ivory paper `#F0EDE4`, ink `#1A1915`, single clay accent `#CC785C`, `Newsreader` serif display + `Hanken Grotesk` body, flat surfaces + hairline borders, reduced-motion-safe hero fade-up. Matches the README infographics. Email capture: set `KIT_FORM_ID` **or** `FORMSPREE_ID` to automate; until then signups route to `OWNER_EMAIL` via a `mailto:` fallback (a static site has no backend, so capture needs an owned endpoint — never a false "you're in"). |
| `course.html`, `toolkit.html` | The other two "doors" (Door 01 Learn, Door 02 Build), linked from the `index.html` cards. Static hubs in the same Anthropic design system that surface real repo content — `course.html` the six-cluster competency map + prep curricula + readiness scorecard + lessons; `toolkit.html` the seven skills + field kit + MCP server — each item linking to the rendered source on GitHub (`/blob/main/…` or `/tree/main/…`). The three `index.html` cards are now `<a class="card">` links (Course→`course.html`, Toolkit→`toolkit.html`, Community→`contribute.html`) with a `.card-go` bottom CTA. To add a curriculum item or skill, add a list `<a class="item">` row pointing at its GitHub path. |
| `contribute.html` | The **agentic contributor page** (linked from `index.html` nav + the Community card). Two no-login, no-backend capabilities: (1) a **Delta guide** chat grounded in an in-page `KB` of FDE-os facts — keyword-retrieval with an honest refusal+human-handoff fallback, *never* invents; (2) a 5-step **field-note intake** that structures a war-story into `{problem, context, tried, outcome, tags}` and posts it as a **prefilled GitHub issue** (`/issues/new?labels=field-note&…`), with copy/Discord fallbacks. Same Anthropic design system as `index.html`. To extend the guide, edit the `KB` array; to change the contribution sink, edit `REPO`/`postIssue()`. Pure client-side so it runs on GitHub Pages with no exposed key. **Optional "⚡ Power mode":** a visitor can supply their OWN free LLM key (Gemini/Groq/custom OpenAI-compatible or a NIM proxy) to get RAG-grounded conversational answers — `askLLM()` retrieves top-`scored()` KB facts and feeds them as the ONLY context with a "never invent" system prompt, falling back to the keyword guide on any error. Key is stored in `localStorage` (`delta_llm`) only — never committed, never in source. Add providers via the `PRESETS` map; default model `gemini-2.5-flash` (probe ids + CORS before changing, per the `free-llm` skill). **Hosted default:** `GUIDE_PROXY` points at the deployed `proxy/delta-guide/` (Vercel), so every visitor gets the model with no key — `activeLLM()` resolves visitor-key → hosted proxy → offline, in that order. |
| `proxy/delta-guide/` | **Deployable** Vercel serverless function (`api/guide.js`) backing the guide with a SHARED free key (server-side env var, never shipped) + fallback chain (NIM→Groq→Gemini), `ALLOW_ORIGIN` allow-list, and token/size caps. The page does the RAG; the proxy only forwards `{messages}`. Deploy: `cd proxy/delta-guide && vercel deploy --prod --yes --scope <team>`, then set `GEMINI_API_KEY`/`ALLOW_ORIGIN` env vars + redeploy, then set `GUIDE_PROXY` in `contribute.html`. `.vercel/`, `.env` gitignored. |
| `docs/plans/` | The roadmap. Decision artifact — do not encode progress here; progress lives in git. |
| `docs/research/` | External sources (`sources/`) + critical evals. Honesty rule: a repost is not independent corroboration — note it (same R4 discipline as the vault). |
| `ARCHITECTURE.md`, `docs/assets/` | System-design doc + the README infographics (hand-authored SVG, cream/ink/rust Anthropic-style; self-contained backgrounds so they render in GitHub light AND dark mode; no `<script>`/external refs so the GitHub sanitizer keeps them). |
| `docs/marketing/` | Copy *about the project* (long-form article + short posts). House rule: 15-yo-legible, director-deep, funny — and gate each piece with `true-scorer`/`criteria-scorer` before shipping (we dogfood our own marketing). |

## External toolsets (the hub) — query on trigger, don't carry in context

Every top-rated repo FDE-os cites is compiled into a knowledge graph + a tooling entry under
`knowledge/hub/` (registry: `repos.yml` · factory: `skills/repo-compiler` · viewers: `<slug>.html`).
When you need an external capability (observability, MCP framework, tool discovery, MLOps, …),
**query the hub first** instead of reaching for memory or the web:

```bash
python3 skills/repo-compiler/scripts/hub_query.py find <capability words>   # or MCP tool `hub_find`
python3 skills/repo-compiler/scripts/hub_query.py recipe <repo>             # full entry
```

Each hit returns the **integration recipe** (discovery-source / plugin-dependency / workflow-organ /
distribution-surface / course-citation), the honest **`notGoodAt`** edges, and a SHA-pinned source.
Rules: adopt only via the recipe; read before you run (popularity ≠ safety); staleness is checked by
`repo_compile.py refresh` (exit 3 = drift → re-run `all`). New citation → one entry in `repos.yml`.

## Native skills (current)

- **`knowledgefy`** — local-first, offline, deterministic: prose vault → `graph.json` + `file://`
  HTML. Headings → `concept` nodes; inline + bare-URL citations → `evidence` nodes. No network on
  the base path; semantic/lineage edges are an opt-in NIM-enrich pass only.
  Run: `python3 skills/knowledgefy/scripts/knowledgefy.py build <vault> --out <g.json> --html <g.html>`
- **`true-scorer`** — the TRUE rubric (T/R/U/E, 0–3 each) as a publish gate. **Gate: total ≥ 10
  AND every letter ≥ 2** (the AND is the point — a perfect total with one weak letter blocks).
  Run: `python3 skills/true-scorer/scripts/score.py <draft.md>` or `--scores T=3,R=3,U=2,E=2`.
- **`field-kit-generator`** — scaffolds + lints a Field Kit to convention (menu / names-source /
  marks-RISKS); the actual synthesis is `skillfy`'s job (thin wrapper, KTD5). The `lint` subcommand
  is the field-kits index-lint U1 referenced. Run: `… field_kit_generator.py generate <slug> --type … --source … --summary …` or `… lint field-kits/`.
- **`rag-eval-harness`** — offline/deterministic RAG eval: retrieval metrics + grounding/hallucination
  proxy + citation coverage + a pass/fail gate (the true-scorer pattern). Run: `… rag_eval.py score <eval_set.json> --k 5 --thresholds "recall@k=0.7,grounding=0.8"`. Deterministic core, no network; LLM-judge is an opt-in layer.
- **`fde-mcp-server`** — a stdlib MCP server (stdio JSON-RPC) exposing FDE-os skills as MCP tools
  (7: `true_score`, `rag_eval`, `criteria_score`, `eval_loop`, `invisible_workflow_map`, `jd_compile`,
  `doc_gate`). `handle_request` is pure (testable); add a tool via the `TOOLS` registry.
  A runnable "1+ Claude MCP integrations" reference. Spawned by an MCP host; see SKILL.md for config.
- **`criteria-scorer`** — binary pass/fail criteria scorer (typed predicates: word count, regex,
  buzzword list, has-number, has-citation) → 0–1 + `gate()`. Pure `score_artifact`/`gate` for reuse.
- **`doc-understanding`** — messy enterprise docs → canonical structured rep + parse-quality gate.
  DOCX (gridSpan/vMerge merges, w:ins/w:del track-changes), XLSX (sharedStrings, dense grids), md/csv.
  Gate: NO-GO on zero blocks, overall < threshold, or unresolved revisions. Pure stdlib.
  Run: `python3 skills/doc-understanding/scripts/doc_understand.py parse <f> [--json]` / `gate <f> [--threshold 0.7]`.
- **`eval-loop`** — keep/revert loop + run-log (Round │ Change │ Score │ Verdict). Tested core is
  `decide(rounds)`/`render_run_log`; scoring is pluggable (`score-each` wires any scorer via `{file}`).
  Assisted, not autonomous — humans own taste, gates own the floor.

- **`course/prep/tools/coding-drill-kit`** — not a skill: an eval-as-gate drill harness for the
  Google-FDE-loop case study (blank-page template recall, scored + tracked). `attempts/` and
  `problems.md` are personal artifacts, gitignored — never commit them.
- **`playground.html` + `assets/toolkit-brain.json`** — the browser playground runs three skill
  cores client-side. The brain JSON is **generated, never hand-edited**: after changing `CLUSTERS`/
  `TOOLS` (jd-compiler), `DIMENSIONS`/`PROBES`/`ARCHETYPES` (workflow-mapper), or the TRUE gate
  constants, run `python3 scripts/export_brain.py` — `tests/test_brain_export.py` fails the build
  if the committed JSON is stale.

**Reuse vs design:** existing skills (`living-knowledge`, `skillfy`, `dreammaketrue`,
`knowledge-graph`, `living-repo`) are the production engine and are NOT vendored. Design a native
skill only when a spike shows the existing ones genuinely fall short (see KTD3 in the plan).

## Conventions

- **Tests:** stdlib `unittest`, per skill. Run: `python3 -m unittest discover -s skills/<name>/tests -p 'test_*.py'`. Python 3.11. No third-party deps — keep skills stdlib-only and offline-by-default. **CI (`.github/workflows/tests.yml`) auto-discovers every `skills/*/tests` suite + runs the Field Kit lint on each push/PR** — a new skill is covered automatically if it follows the `skills/<name>/tests/test_*.py` layout.
- **Determinism:** generated artifacts (the spine) must be byte-reproducible (sorted keys, stable ids). There is a test for this; don't break it.
- **Security:** anything touching field/customer data (Stage 3+) is born-clean — redact at capture, allow-list what may persist, fail-closed. Never route journal/portfolio data into an external engine.
- **Branches:** never commit to `main`. One branch per stage (`feat/fde-os-stage-N`), scoped PRs. After a squash-merge, rebuild the next stage's branch fresh from `main` (cherry-picking replayed commits fights the squash).
- **Secrets:** the owned-hub provider (ConvertKit/Kit) form id / keys live in env or the form's public action URL — never commit a secret. `.gitignore` excludes `.env`.
- **Docs sync (required, same change):** any feature change updates `CHANGELOG.md` (with an `Investigated / Rejected` note when an approach was killed), `README.md`, and this `AGENTS.md`. A plan doc does not substitute for the README.
- **Progress tracking:** the roadmap plan is a **decision artifact — never edit it to record progress** (no `[x]` boxes; it drifts and creates merge noise). Three layers instead: `CHANGELOG.md` = what shipped, the plan = decisions/U-IDs, **`STATUS.md` = the one-glance "where are we now"**. When a PR lands a unit, move its row in `STATUS.md` to Done with the PR number; git stays the source of truth.

## Stage gates

The roadmap is gated, not automatic. **Gate A** (Stage 1→2): Post #1 earned real traction, not just
that the pipeline ran. **Gate B** (Stage 2→3/4): a quantified traction floor across posts 1–4 funds
the heavy stages; if missed, iterate content — don't proceed. Stages 4–5 are separate follow-on
initiatives needing their own `ce-plan` pass. See the plan's "Stage Gates & Kill Signals".
