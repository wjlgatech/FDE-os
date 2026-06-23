# Prep Curriculum — Reflection AI Forward Deployed Engineer

A JD-validated study plan for the [Reflection AI FDE role](../target-jds/reflection-ai-fde.md).
**Validation question:** *would someone who finishes this be ready to land the role?*

Every cluster ships **both halves** (the FDE-os TRUE model):

- 📘 **Learn (human, T):** the knowledge a person internalizes — concept-first, with a build-it project.
- 🛠️ **Tool (agent, R):** a forkable agent asset (skill / prompt / dynamic workflow / hook) you
  **build as you learn** and keep — it does the work *and* becomes a portfolio artifact that proves
  the competency. (Building the tool *is* the deepest version of learning it — the FDE-os
  Build-It → Deploy-It spine.)
- ✅ **Prove (Deploy-It gate, E):** a concrete, JD-anchored artifact + self-score that says "ready."

Sequence: do the FDE craft (Cluster 5) **first** — it's the role's spine and FDE-os already
teaches it — then the technical clusters, which the customer reality makes concrete.

---

## Cluster 5 — The FDE craft (do this first)

*JD anchor: "Partner with strategists and sales to understand enterprise needs and architect
agentic solutions" · "customer-facing" · "high agency."*

- 📘 **Learn:** The Delta Loop (deploy → learn → build → codify), discovery, mapping the political
  terrain, finding the data reality, scoping the smallest end-to-end win. Read
  [`Delta-01-field-manual.md`](../../Delta-01-field-manual.md); internalize *"context is what's
  scarce — a requirements doc is a lossy compression of a reality the customer can't articulate."*
- 🛠️ **Tool:** the **[Delta Discovery Protocol](../../field-kits/delta-discovery-protocol/SKILL.md)**
  (already in this repo — fork it) → produces a **Site Survey**. Then the flagship bridge tool,
  **[agentic-solution-architect](tools/agentic-solution-architect/SKILL.md)**, turns a Site Survey
  into a proposed agent architecture — exactly the JD's "architect agentic solutions."
- ✅ **Prove:** run a real discovery on any messy problem (a friend's startup, your own team) →
  produce a Site Survey → run the architect skill → defend the smallest-first-build choice.

## Cluster 1 — Production software engineering (Python + TypeScript)

*JD anchor: "Strong software engineering background shipping production systems (Python, TypeScript)."*

- 📘 **Learn:** ship one real service in **each** language (an API + a small typed frontend or CLI);
  tests, types, CI, code review, error handling, observability. The bar is *production*, not toy.
- 🛠️ **Tool:** a **pre-commit / pre-push hook + test-CI** that gates your repos (this very repo's
  [`tests.yml`](../../.github/workflows/tests.yml) + freshness CI are a working reference to fork).
  Bonus agent tool: a code-review skill that runs your linters/tests and reports a verdict.
- ✅ **Prove:** a deployed service in each language, CI green, with a README a stranger can run.

## Cluster 2 — Enterprise / hybrid deployment + DevOps

*JD anchor: "deploying enterprise software in cloud/hybrid environments (public cloud, VPC,
on-premises) with DevOps practices."*

- 📘 **Learn:** containers (Docker), orchestration basics (K8s), IaC, secrets management, and the
  *constraints that define FDE work* — data residency, air-gapped/VPC, on-prem, "what can't leave
  the customer's perimeter." This is the integration truth that's almost always the hidden bottleneck.
- 🛠️ **Tool:** a **Deployment Preflight checklist** agent skill/SOP (Field Kit menu: Checklist/SOP) —
  perimeter constraints, access timelines, rollback, monitoring. Scaffold it with
  [`field-kit-generator`](../../skills/field-kit-generator/SKILL.md).
- ✅ **Prove:** deploy the *same* app to a public cloud **and** a locally-simulated VPC/on-prem
  target; document what changed and why.

## Cluster 3 — Modern AI stack (RAG, vector DBs, evaluations, fine-tuning)

*JD anchor: "vector databases, RAG, agents, evaluations, fine-tuning."*

- 📘 **Learn:** build a RAG pipeline end-to-end (chunk → embed → retrieve → generate); a vector DB;
  an **eval harness** with real metrics (not vibes); one fine-tune / adapter on a small model.
  Evaluation is the load-bearing skill — *"how do we know it works to the operator at 5pm?"*
- 🛠️ **Tool:** a **RAG/agent eval-harness** skill — a rubric an agent runs over outputs and returns
  pass/fail with evidence (mirror the [`true-scorer`](../../skills/true-scorer/SKILL.md) gate
  pattern: a deterministic threshold + structured findings).
- ✅ **Prove:** a RAG system with a published eval scoreboard; show a before/after from one change.

## Cluster 4 — Agentic system design

*JD anchor: "Build agentic systems... orchestrating LLM workflows and integrating with enterprise
infrastructure."*

- 📘 **Learn:** agent loops, tool-use, multi-step orchestration, MCP servers, guardrails, failure
  modes, cost/latency. Build a multi-tool agent that does a real task against real infra (a DB, an
  API, a ticket system).
- 🛠️ **Tool:** an **MCP server** exposing one enterprise capability (Field Kit menu: MCP server spec),
  + a **dynamic workflow** that chains discovery → architecture → eval. The
  [agentic-solution-architect](tools/agentic-solution-architect/SKILL.md) skill is the design half.
- ✅ **Prove:** a working agent solving a real task across ≥2 tools, with an eval (Cluster 3) and a
  deploy story (Cluster 2).

## Cluster 6 — Post-training (stretch, for the Lead/Post-training variant)

*JD anchor: "RL training environments, reward modeling, preference optimization, 50B+ param models,
distributed training."*

- 📘 **Learn:** post-training methodology (SFT → preference optimization/RLHF/RLAIF), reward models,
  verifiers, synthetic data pipelines, eval design, multi-node GPU/distributed training.
- 🛠️ **Tool:** a **synthetic-data + reward-eval pipeline** (script/runbook) over a small open model —
  the small-scale rehearsal of the real job.
- ✅ **Prove:** a documented post-training run (even tiny) with a reward model + eval deltas.

---

## Readiness gate (eval-as-gate — the I4 pattern)

Self-score each cluster 0–3. **Apply when total ≥ 12/18 AND no required cluster (1–5) below 2.**
(Cluster 6 is only required for the Post-training Lead variant.)

| Score | Meaning |
|---|---|
| 0 | never touched it |
| 1 | read about it, no artifact |
| 2 | built one real thing; could discuss it in an interview |
| 3 | shipped + deployed + evaluated it; have a portfolio artifact + an agent tool to show |

The honest test, per cluster: *can you point to a deployed artifact AND a forkable agent tool?* If
not, you're at ≤1 there. A 3 across Clusters 4 + 5 (architect agentic solutions from a real
discovery) is the single strongest signal for this specific role.

## Your portfolio (the by-product that gets you hired)

Finishing this leaves you with: a Site Survey, an agent architecture, a deployed service ×2, a RAG
system + eval scoreboard, a working multi-tool agent + MCP server, a deployment preflight, and a
small CI/hook stack — **plus the agent tools you built for each**, which together are a cross-agent
FDE toolkit. That toolkit *is* the interview.
