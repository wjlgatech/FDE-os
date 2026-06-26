# FDE-os — Status

**The one-glance "where are we now."** Source of truth is **git** (commits + merged PRs); the
[roadmap plan](docs/plans/2026-06-20-001-feat-fde-os-staged-roadmap-plan.md) holds the *decisions*
(stable U-IDs) and stays immutable; [`CHANGELOG.md`](CHANGELOG.md) is the full build log. This file
is just the glance — update it in the same PR that lands a unit.

_Last updated: 2026-06-26._

## 🧰 Native skills shipped (Objective 2 tooling)

`knowledgefy` · `true-scorer` · `field-kit-generator` · `rag-eval-harness` · `fde-mcp-server` ·
**`criteria-scorer`** · **`eval-loop`** (the self-improving loop primitive — from the
[agent-loops critical eval](docs/research/agent-loops-critical-eval.md)). All offline, tested,
CI-gated.

## ✅ Done — on `main`

| Unit | What | Landed |
|---|---|---|
| U1 | Repo spine + link-freshness CI | PR #1 |
| U2 | `knowledgefy` skill (offline prose-vault → spine) | PR #1 |
| U3 | FDE knowledge spine (12 concepts / 39 evidence / 51 edges) | PR #1 |
| U4 | `true-scorer` skill (TRUE publish gate) | PR #1 |
| U5 | Owned-hub wiring — **code only** (ConvertKit/Kit endpoint) | PR #2 |
| U7 | Pipeline metrics ledger + Gate A/B thresholds | PR #2 |
| U8 | `field-kit-generator` skill (+ field-kits index-lint) | PR #3 |

## 📗 Objective 1 — prep material (user-directed, ungated)

- **Reflection AI FDE** — JD captured + dual-tier prep curriculum (human knowledge + agent tools per
  competency) + flagship `agentic-solution-architect` skill. (`course/target-jds/`, `course/prep/`.)
- **CVS Agentic AI Engineer** — JD captured + dual-tier prep; **eval cluster deepened** into a full
  RAG-evaluation lesson + the runnable **`rag-eval-harness`** skill (17 tests, offline gate).
- _Pattern for future JDs: drop a JD → I distill it into a target + prep curriculum + tools._

## 🔴 Blocked on you — Stage 1 go-live (ops, not code)

These are outward actions on your accounts; nothing here is a code task.
**→ Step-by-step: [`flywheel/go-live-runbook.md`](flywheel/go-live-runbook.md)** (a ~30-min checklist).

- **U5 go-live** — create the ConvertKit/Kit form, set `KIT_FORM_ID` in
  `index.html`; stand up the Delta Discord; create `r/ForwardDeployed`.
- **U6** — publish Post #1 (Signal + Newsletter), link the Field Kit, post the war-story prompt.
  Pre-publish gate: `true-scorer` (already passes 12/12).
- → then **read Gate A** together (Post #1 earned real traction, not just "the pipeline ran").

## ⏭️ Next — gated, do not start without the gate

- **Stage 2 content** (posts 2–4, U10) — **gated on Gate B** (a traction floor across posts 1–4).
- Buildable Stage 2 *tooling* that does not publish: U9 (`dreammaketrue` draft wiring — needs the
  engine/key), U11 (production runbook). U8 already shipped ahead.
- **Stages 3–5** (flywheel infra, course, cross-agent compiler) — gated on Gate B; Stages 4–5 each
  need their own `ce-plan` pass. See the plan's "Stage Gates & Kill Signals."

## How to keep this current

When a PR lands a unit: move its row to **Done** with the PR number, and re-bucket anything it
unblocks. Don't tick boxes in the roadmap plan — progress lives here + in git, the plan stays a
clean decision record. (To rebuild this from scratch, the U-ID → PR mapping is in the merged PR
titles and `CHANGELOG.md`.)
