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
| `skills/` | FDE-os-native skills. Built only where existing skills leave a verified gap. Each has `SKILL.md` + (where runnable) `scripts/` + `tests/`. |
| `knowledge/` | Generated spine (`fde-spine.*`). Regenerate with `knowledgefy`; don't hand-edit. |
| `flywheel/` | Objective-3 infra + production runbook/metrics. `metrics.md` is the per-post funnel + the Gate A/B thresholds (the only owned metric is email conversions). Security-sensitive (Stage 3 handles real customer data, born-clean redaction). |
| `course/` | Objective-1 course. `target-jds/` = JD validation targets; `prep/` = worked dual-tier prep curricula (each competency = human knowledge + a forkable agent tool + an eval gate). The full Stage-4 course *engine* is still gated; per-JD prep material is built on request. |
| `field-kits/` | Forkable Field Kits, one per post. Convention: `field-kits/<slug>/SKILL.md`, names its source article, marks unknowns as RISKS (never invent). |
| `scripts/` | Repo tooling (`check_freshness.py`). |
| `index.html` | The Delta community landing page — served live via GitHub Pages at https://wjlgatech.github.io/FDE-os/. `.nojekyll` keeps Pages from running Jekyll. **Design system (keep new UI consistent):** Anthropic-style — ivory paper `#F0EDE4`, ink `#1A1915`, single clay accent `#CC785C`, `Newsreader` serif display + `Hanken Grotesk` body, flat surfaces + hairline borders, reduced-motion-safe hero fade-up. Matches the README infographics. Email capture: set `KIT_FORM_ID` **or** `FORMSPREE_ID` to automate; until then signups route to `OWNER_EMAIL` via a `mailto:` fallback (a static site has no backend, so capture needs an owned endpoint — never a false "you're in"). |
| `contribute.html` | The **agentic contributor page** (linked from `index.html` nav + the Community card). Two no-login, no-backend capabilities: (1) a **Delta guide** chat grounded in an in-page `KB` of FDE-os facts — keyword-retrieval with an honest refusal+human-handoff fallback, *never* invents; (2) a 5-step **field-note intake** that structures a war-story into `{problem, context, tried, outcome, tags}` and posts it as a **prefilled GitHub issue** (`/issues/new?labels=field-note&…`), with copy/Discord fallbacks. Same Anthropic design system as `index.html`. To extend the guide, edit the `KB` array; to change the contribution sink, edit `REPO`/`postIssue()`. Pure client-side so it runs on GitHub Pages with no exposed key. **Optional "⚡ Power mode":** a visitor can supply their OWN free LLM key (Gemini/Groq/custom OpenAI-compatible or a NIM proxy) to get RAG-grounded conversational answers — `askLLM()` retrieves top-`scored()` KB facts and feeds them as the ONLY context with a "never invent" system prompt, falling back to the keyword guide on any error. Key is stored in `localStorage` (`delta_llm`) only — never committed, never in source. Add providers via the `PRESETS` map; default model `gemini-2.5-flash` (probe ids + CORS before changing, per the `free-llm` skill). **Hosted default:** `GUIDE_PROXY` points at the deployed `proxy/delta-guide/` (Vercel), so every visitor gets the model with no key — `activeLLM()` resolves visitor-key → hosted proxy → offline, in that order. |
| `proxy/delta-guide/` | **Deployable** Vercel serverless function (`api/guide.js`) backing the guide with a SHARED free key (server-side env var, never shipped) + fallback chain (NIM→Groq→Gemini), `ALLOW_ORIGIN` allow-list, and token/size caps. The page does the RAG; the proxy only forwards `{messages}`. Deploy: `cd proxy/delta-guide && vercel deploy --prod --yes --scope <team>`, then set `GEMINI_API_KEY`/`ALLOW_ORIGIN` env vars + redeploy, then set `GUIDE_PROXY` in `contribute.html`. `.vercel/`, `.env` gitignored. |
| `docs/plans/` | The roadmap. Decision artifact — do not encode progress here; progress lives in git. |
| `docs/research/` | External sources (`sources/`) + critical evals. Honesty rule: a repost is not independent corroboration — note it (same R4 discipline as the vault). |
| `ARCHITECTURE.md`, `docs/assets/` | System-design doc + the README infographics (hand-authored SVG, cream/ink/rust Anthropic-style; self-contained backgrounds so they render in GitHub light AND dark mode; no `<script>`/external refs so the GitHub sanitizer keeps them). |
| `docs/marketing/` | Copy *about the project* (long-form article + short posts). House rule: 15-yo-legible, director-deep, funny — and gate each piece with `true-scorer`/`criteria-scorer` before shipping (we dogfood our own marketing). |

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
  (`true_score`, `rag_eval`). `handle_request` is pure (testable); add a tool via the `TOOLS` registry.
  A runnable "1+ Claude MCP integrations" reference. Spawned by an MCP host; see SKILL.md for config.
- **`criteria-scorer`** — binary pass/fail criteria scorer (typed predicates: word count, regex,
  buzzword list, has-number, has-citation) → 0–1 + `gate()`. Pure `score_artifact`/`gate` for reuse.
- **`eval-loop`** — keep/revert loop + run-log (Round │ Change │ Score │ Verdict). Tested core is
  `decide(rounds)`/`render_run_log`; scoring is pluggable (`score-each` wires any scorer via `{file}`).
  Assisted, not autonomous — humans own taste, gates own the floor.

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
