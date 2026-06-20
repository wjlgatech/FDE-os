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

Greenfield. The first artifact is a ranked, critiqued **ideation document** — 12 surviving
directions across 6 axes, each with a verifiable basis and known downsides.

➡️ **[docs/ideation/2026-06-17-fde-os-ideation.html](docs/ideation/2026-06-17-fde-os-ideation.html)** — open in a browser.

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

## What's next

The ideation doc is a discovery artifact, not a plan. The next step is to commit one direction to a
requirements doc (`ce-brainstorm`), then plan and build it. Suggested first build order for the
flywheel: privacy-redacted capture (I9) + the engineer-owned portfolio incentive (I11) → the
field-journal hub (I8) → the pain-to-ticket back half (I10).
