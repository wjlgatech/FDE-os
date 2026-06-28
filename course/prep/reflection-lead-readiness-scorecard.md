# Readiness Scorecard — Reflection AI · FDE **Lead** – AI Engineer

A personal, JD-anchored readiness instrument for the exact posting
([target JD](../target-jds/reflection-ai-fde.md) · Ashby `56fbaa8a…`, team **Applied AI**, NYC).
This is the **Lead** tier, not the IC "AI Engineer" variant — the bar adds **technical leadership +
playbook-authoring** on top of the agentic-FDE craft.

**Profile assumption (set 2026-06-27):** *seasoned, leadership-ready* — 6+ yrs SWE, has led, has
shipped AI to production. So the operative gap is **evidence & packaging, not capability**. This
scorecard is therefore biased toward *proof you can point to in an interview*, not toward learning.

> **The one honest test, per cluster:** can you point to **(a) a deployed/used artifact** AND **(b) a
> forkable agent tool** AND — for the Lead tier — **(c) a story where you set the standard others
> followed**? If not all three, you're ≤2 there, however strong the underlying skill.

---

## Rubric (0–3)

| Score | Meaning |
|---|---|
| 0 | Never touched it. |
| 1 | Know it / read it — no artifact. |
| 2 | Built one real thing; could discuss it credibly in an interview. |
| 3 | Shipped + deployed + **evaluated** it, have a portfolio artifact **and** an agent tool — and (Lead) **codified it for others**. |

**Gate:** apply when **total ≥ 18/24** AND **no required cluster (1–6) below 2** AND **Cluster 6
(leadership) ≥ 2**. A **3 across Clusters 4 + 5 + 6** (architect agentic solutions from a real
discovery *and* show you can scale the practice) is the single strongest signal for *this* role.

---

## The scorecard — fill the two right columns

For each row: (1) write your **self-score**, (2) name the **one undeniable proof** you'd show. FDE-os
artifacts are pre-listed as evidence *you already built* — they count. `[external]` = a proof from
your own career to slot in.

### Cluster 1 — Production SWE (Python + TypeScript)
*JD: "shipping production-grade systems (Python, Typescript)."*
- **Evidence you already have:** this repo's tested skills + CI (`tests.yml`, `freshness.yml`); the
  `fde-mcp-server` (runnable). `[external]` a production Python **and** a production TS service.
- **Lead bar (a 3):** code others ship on — a service with real users + the standard (CI, review,
  observability) you set for a team.
- **Self-score:** ___  · **Proof to show:** ______________________

### Cluster 2 — Enterprise / hybrid deploy + DevOps (Docker, K8s, CI/CD)
*JD: "deploying enterprise software in cloud or hybrid environments … Docker, Kubernetes, CI/CD … public cloud, VPC, on-premises."*
- **Evidence you already have:** GitHub Actions CI in this repo. `[external]` a Dockerized/K8s
  deploy; **bonus that's rare and on-point:** a deploy into a constrained perimeter (VPC/on-prem/air-gapped).
- **Lead bar (a 3):** owned an end-to-end hybrid deployment *and* wrote the deployment-preflight
  standard others run. **Gap-fill tool:** a Deployment-Preflight skill (scaffold via `field-kit-generator`).
- **Self-score:** ___  · **Proof to show:** ______________________

### Cluster 3 — Modern AI stack (RAG · vector DBs · evals · fine-tuning)
*JD: "vector databases, RAG pipelines, … evaluations, and fine-tuning."*
- **Evidence you already have:** `rag-eval-harness` skill (17 tests, offline gate); `true-scorer` /
  `criteria-scorer` / `eval-loop` (the eval-as-gate spine — evaluation is the load-bearing skill here).
  `[external]` a RAG system with a **published eval scoreboard** + one fine-tune/adapter.
- **Lead bar (a 3):** a RAG/eval system in production with a before/after metric delta you drove.
- **Self-score:** ___  · **Proof to show:** ______________________

### Cluster 4 — Agentic system design
*JD: "architect and build complex agentic systems … orchestrating sophisticated LLM workflows and integrating deeply with enterprise infrastructure."*
- **Evidence you already have:** `agentic-solution-architect` skill (Site Survey → proposed
  architecture); `fde-mcp-server` (an MCP capability surface). `[external]` a multi-tool agent doing a
  real task across ≥2 systems, with an eval + a deploy story.
- **Lead bar (a 3):** a deployed agent solving a real business task end-to-end. **Gap-fill tool:** a
  dynamic workflow chaining *discovery → architecture → eval* (you have all three pieces; wire them).
- **Self-score:** ___  · **Proof to show:** ______________________

### Cluster 5 — The FDE craft (customer-facing · discovery · high agency)
*JD: "Partner with Deployment Strategists and Sales … customer-facing … self-starter with high agency, where playbooks are still being written."*
- **Evidence you already have:** the **Delta Discovery Protocol** field kit → Site Survey; the whole
  FDE-os thesis. `[external]` a real engagement where you walked in under ambiguity and shipped the
  smallest end-to-end win.
- **Lead bar (a 3):** a discovery → architecture → delivery you ran with a customer, and can defend
  the smallest-first scoping call.
- **Self-score:** ___  · **Proof to show:** ______________________

### Cluster 6 — Technical leadership & playbooks  ⟵ *the Lead delta; your differentiator*
*JD: "own the end-to-end technical strategy … define playbooks, best practices, technical standards, and mentorship … build and scale the Forward Deployed Engineering organization … 2+ yrs in a technical leadership capacity."*
- **Evidence you already have — and it's strong:** **FDE-os is itself a playbook system.** You built
  an *evolving-playbooks* flywheel (field signal → codified best practice), eval-gated standards
  (`true-scorer`/`criteria-scorer` as "technical standards" made mechanical), a staged roadmap with
  stable U-IDs, and a curriculum that *teaches the craft to others*. That is a literal demonstration
  of "define playbooks + scale the practice." `[external]` team(s) you led, people you mentored,
  standards you set that outlived you.
- **Lead bar (a 3):** you can tell the story — "I defined how a team did X, here's the artifact, here's
  who followed it" — and FDE-os is the working proof you do this reflexively.
- **Self-score:** ___  · **Proof to show:** ______________________

*(Cluster on the post-training variant — RL envs / reward modeling / 50B+ — is **out of scope** for
this AI-Engineer Lead posting; ignore unless you also chase the post-training Lead.)*

---

## Score it, then read the gap

`Total ___ / 24.`  Lowest required cluster: ___.

- **Total ≥ 18 and Cluster 6 ≥ 2 → you're interview-ready;** the work is sequencing your proofs.
- **Any required cluster at 0–1 → that's a packaging gap, not a learning gap** (per your profile):
  there's almost certainly real capability behind it that you simply haven't turned into a pointable
  artifact. Fix by *producing the proof*, not re-studying.

## Prioritized gap-fill plan (tuned for "leadership-ready, evidence-gap")

Highest leverage first — each step is a **packaging move**, sized in days not months:

1. **Mint your two flagship case studies (Clusters 4 + 5).** One real engagement, written as a
   one-page case: the ambiguity → your Site Survey → the architecture → the smallest win → the eval
   that proved it. This single artifact lights up the two clusters that matter most for the role.
2. **Write the leadership narrative (Cluster 6) with FDE-os as Exhibit A.** A short "how I set
   technical standards" piece: point at the eval-gated playbook system + the flywheel as proof you
   *build the playbooks the JD asks the Lead to build.* Pair it with one `[external]` team story.
3. **Close the two tool gaps so the toolkit is whole:** the **Deployment-Preflight** skill (Cluster 2)
   and the **discovery→architecture→eval** dynamic workflow (Cluster 4). Both are short — you already
   own the pieces. (Say the word and I'll build these now; it's pure-agent silicon I can drive to green.)
4. **Publish the eval scoreboard (Cluster 3).** Take an existing RAG/agent artifact, run
   `rag-eval-harness`, show a before/after delta. Evaluation is the load-bearing skill for this team —
   a public scoreboard is disproportionately convincing.
5. **One hybrid-deploy proof (Cluster 2).** Deploy the *same* app to public cloud **and** a simulated
   VPC/on-prem target; document what changed. Rare, on-point, and the JD names it explicitly.

**Your portfolio is then the interview:** two case studies, a leadership narrative anchored on a real
playbook system, a published eval scoreboard, a hybrid-deploy writeup — plus the forkable agent tool
behind each. For a leadership-ready candidate, steps 1–2 alone likely move you over the gate.
