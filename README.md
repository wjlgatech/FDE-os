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
- **`knowledge/fde-spine.*`** — the canonical FDE knowledge spine built from the research vault
  (12 concepts across all 7 research threads, 39 evidence nodes, 51 edges).
- **Link-freshness CI** (`scripts/check_freshness.py` + `.github/workflows/freshness.yml`) — keeps
  the repo's external references honest (fails only on dead links; bot-walls are warnings).
- **Owned-hub wiring + metrics** (Stage 1 infra) — `delta-community-landing.html` posts to a
  ConvertKit/Kit form (no client-side secret; GDPR/unsubscribe baseline), and `flywheel/metrics.md`
  holds the per-post funnel plus the **Gate A / Gate B** traction thresholds.

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
| [`delta-community-landing.html`](delta-community-landing.html) | The community door (landing page) |

## References

- **[ai-engineering-from-scratch](https://github.com/rohitg00/ai-engineering-from-scratch)** — the blueprint for *how* to build a curriculum-as-repo (lesson tree, Build-It/Use-It spine, every lesson ships a reusable artifact, generated site, CI invariants).
- **Interview Kickstart FDE program** — domain content reference (the 23-week FDE curriculum).
- **Google Cloud Forward Deployed Engineer (GenAI)** — a target-outcome job description the course validates against.
- **[wjlgatech/data-architecture](https://github.com/wjlgatech/data-architecture)** — the cloud/data track (medallion lakehouse, governance, FHIR case studies) and a plugin-of-skills packaging reference.

## Repository structure

| Path | What it is |
|---|---|
| `Delta-*.md`, `FDE-research-synthesis.md` | Content artifacts + the cited research vault (the spine's input) |
| `field-kits/` | Forkable Field Kits — one per Delta post (the "R" in TRUE) |
| `skills/` | FDE-os-native agent skills — built only where existing skills leave a gap (`knowledgefy`, `true-scorer`; `field-kit-generator` lands in Stage 2) |
| `knowledge/` | Generated knowledge spine (`fde-spine.graph.json` + `.html`) |
| `flywheel/` | Objective-3 infra + content-production runbook/metrics (mostly Stage 1–3) |
| `course/` | Objective-1 JD-validated course (Stage 4 — reserved home, not yet built) |
| `scripts/` | Repo tooling (`check_freshness.py`) |
| `docs/plans/`, `docs/ideation/` | The roadmap plan and the originating ideation doc |

## What's next

Stage 0 (foundation) is shipped. **Stage 1 — Prove the Loop**: stand up the owned hub (email list
+ Delta chat), publish Post #1 across the spine (gated by `true-scorer`), and instrument the
funnel. Stages 3–5 (flywheel infra, course, cross-agent compiler) are **gated on Stage-2
traction** (Gate B) — see the roadmap plan's "Stage Gates & Kill Signals".
