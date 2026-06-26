# FDE-os

An operating system for becoming — and staying — a **Forward Deployed Engineer (FDE)**: the
embedded builder who scopes, ships, and operates production-grade agentic systems *inside the
customer's environment*, not just in demos.

FDE-os has **three objectives**:

1. **A JD-validated, personalizable course.** A multi-mastery-level curriculum that upskills a
   person toward FDE roles, validated by one question: *given a job description, does this course
   train the person well enough to land that job?*
2. **Cross-agent FDE tooling.** Skills, plugins, dynamic workflows, and hooks for AI coding agents
   — Claude, Codex, Hermes, OpenClaw — authored once and run across runtimes.
3. **A field-practice feedback flywheel.** Real engineers run the Objective-2 tooling inside real
   engagements; the tooling auto-journals their real use cases, struggles, and problem-solving
   (privacy-redacted at capture); that field signal feeds back to improve Objectives 1 and 2.

## Status

**Stage 0 shipped** (the production foundation). A reviewed six-stage roadmap drives the build:
[`docs/plans/2026-06-20-001-feat-fde-os-staged-roadmap-plan.md`](docs/plans/2026-06-20-001-feat-fde-os-staged-roadmap-plan.md)
(Delta-content-first; each post ships a Field Kit + a war-story prompt, so writing the series
builds the toolkit and seeds the community).

What's live now:

- **`skills/knowledgefy`** — local-first, offline, deterministic: a prose research vault → a
  navigable knowledge spine (`graph.json` + self-contained `file://` HTML). No engine, no network.
- **`skills/true-scorer`** — the TRUE 0–3 rubric as a runnable publish gate (total ≥ 10 AND every
  letter ≥ 2). No Delta post ships un-scored.
- **`skills/field-kit-generator`** — scaffolds + lints a Delta Field Kit to convention (the Field
  Kit menu, names-its-source, marks-RISKS); delegates skill synthesis to `skillfy`. _Tooling for
  Stage 2 — the content (posts 2–4) stays gated on Stage-2 traction._
- **`skills/rag-eval-harness`** — offline, deterministic RAG/agent eval: retrieval metrics
  (precision@k, recall@k, MRR, hit-rate) + a grounding/hallucination proxy + citation coverage, with
  a CI-able pass/fail gate. _Built for the CVS prep's deepened eval cluster; reusable anywhere._
- **`skills/fde-mcp-server`** — a runnable, stdlib **Claude MCP server** (stdio JSON-RPC) exposing
  FDE-os's skills as MCP tools. _A real "1+ Claude MCP integrations" example; fork it for your own._
- **`knowledge/fde-spine.*`** — the canonical FDE knowledge spine built from the research vault
  (12 concepts across all 7 research threads, 39 evidence nodes, 51 edges).
- **CI** — `tests.yml` runs every skill's test suite + the Field Kit convention lint on each
  push/PR; `freshness.yml` (`scripts/check_freshness.py`) keeps external references honest (fails
  only on dead links; bot-walls are warnings).
- **Live landing page** → **https://wjlgatech.github.io/FDE-os/** — the Delta community door,
  served from `index.html` via GitHub Pages. This is the URL Post #1's first-comment link points at.
- **Owned-hub wiring + metrics** (Stage 1 infra) — `index.html` captures signups: set `KIT_FORM_ID`
  *or* `FORMSPREE_ID` for automated capture (no client-side secret; GDPR/unsubscribe baseline), and
  until then a signup routes to `OWNER_EMAIL` via the visitor's mail app (no lead dropped). The funnel
  + **Gate A / Gate B** thresholds live in `flywheel/metrics.md`.

The discovery artifact that started it all — a ranked, critiqued **ideation document** (12
directions across 6 axes) — is at
➡️ **[docs/ideation/2026-06-17-fde-os-ideation.html](docs/ideation/2026-06-17-fde-os-ideation.html)**.

## Delta — the content flywheel

**Delta** is FDE-os's public content layer: a blog/essay series ("The Last Mile") that ignites the three objectives rather than being a fourth. Articles win attention → the **Course** builds skill → the **Toolkit** gives leverage → the **Community** retains people and generates the next field stories → which become the next articles.

Every post is two tiers and must be **TRUE**:
- **T**ransferable — a mental model a human can re-teach (feeds Objective 1, the course)
- **R**eusable for agents — ships a forkable **Field Kit** asset (feeds Objective 2, the tooling)
- **U**nderstandable — a sharp 15-year-old follows it (concrete-first)
- **E**xperience-able — a sub-10-min "try this" that produces conviction (feeds Objective 3, the flywheel)

Because each article ships a Field Kit, **writing the series builds the toolkit** — content production *is* product production.

### Delta artifacts (in this repo)

| File | What it is |
|---|---|
| [`FDE-research-synthesis.md`](FDE-research-synthesis.md) | The cited research vault (7 threads: labs, Palantir origin, YC, analysts, the debate, tooling, community) |
| [`Delta-01-field-manual.md`](Delta-01-field-manual.md) | **Post #1** — long-form TRUE article (scored 12/12): *The Delta Loop* |
| [`field-kits/delta-discovery-protocol/SKILL.md`](field-kits/delta-discovery-protocol/SKILL.md) | **Field Kit #1** — a forkable agent skill that runs FDE-style discovery |
| [`Delta-01-linkedin.md`](Delta-01-linkedin.md) | Post #1 viral feed-post ("Signal") version |
| [`Delta-TRUE-article-spec.md`](Delta-TRUE-article-spec.md) | The TRUE article template + Field Kit menu + 0–3 eval rubric |
| [`Delta-viral-playbook.md`](Delta-viral-playbook.md) | Hook templates, post skeleton, stat bank, do/don't |
| [`Delta-community-strategy.md`](Delta-community-strategy.md) | Hub-and-spoke community topology + participation ladder |
| [`index.html`](index.html) | The community door (landing page) |

## References

- **[ai-engineering-from-scratch](https://github.com/rohitg00/ai-engineering-from-scratch)** — the blueprint for *how* to build a curriculum-as-repo (lesson tree, Build-It/Use-It spine, every lesson ships a reusable artifact, generated site, CI invariants).
- **Interview Kickstart FDE program** — domain content reference (the 23-week FDE curriculum).
- **Google Cloud Forward Deployed Engineer (GenAI)** — a target-outcome job description the course validates against.
- **[Reflection AI — Forward Deployed Engineer](course/target-jds/reflection-ai-fde.md)** — a second JD target, with a worked dual-tier prep curriculum ([`course/prep/reflection-ai-fde-prep.md`](course/prep/reflection-ai-fde-prep.md)): every competency ships human knowledge **and** a forkable agent tool.
- **[CVS Health — Agentic AI Engineer](course/target-jds/cvs-agentic-ai-engineer.md)** — a third JD target ([prep](course/prep/cvs-agentic-ai-engineer-prep.md)), with one cluster deepened into a full [RAG-evaluation lesson](course/prep/lessons/rag-evaluation.md) + the runnable `rag-eval-harness` skill.
- **[wjlgatech/data-architecture](https://github.com/wjlgatech/data-architecture)** — the cloud/data track (medallion lakehouse, governance, FHIR case studies) and a plugin-of-skills packaging reference.

## Repository structure

| Path | What it is |
|---|---|
| `Delta-*.md`, `FDE-research-synthesis.md` | Content artifacts + the cited research vault (the spine's input) |
| `field-kits/` | Forkable Field Kits — one per Delta post (the "R" in TRUE) |
| `skills/` | FDE-os-native agent skills — built only where existing skills leave a gap (`knowledgefy`, `true-scorer`; `field-kit-generator` lands in Stage 2) |
| `knowledge/` | Generated knowledge spine (`fde-spine.graph.json` + `.html`) |
| `flywheel/` | Objective-3 infra + content-production runbook/metrics (mostly Stage 1–3) |
| `course/` | Objective-1 JD-validated course. `target-jds/` = JD validation targets; `prep/` = worked dual-tier prep curricula (human knowledge + agent tools). The full Stage-4 course engine is still gated. |
| `scripts/` | Repo tooling (`check_freshness.py`) |
| `docs/plans/`, `docs/ideation/` | The roadmap plan and the originating ideation doc |

## What's next

**Where are we right now? → [`STATUS.md`](STATUS.md)** — the one-glance done / blocked / next board.
(The roadmap plan holds the *decisions* and stays immutable; `CHANGELOG.md` is the full build log;
`STATUS.md` is the glance. Progress lives in git, never as checkboxes in the plan.)

In short: Stage 0 (foundation) is shipped and most of Stage 1's *code* is in. **Stage 1 — Prove the
Loop** now needs the go-live ops (publish Post #1, wire the Kit form) before **Gate A** can be read.
Stages 3–5 are **gated on Stage-2 traction** (Gate B) — see the roadmap plan's "Stage Gates & Kill
Signals".
