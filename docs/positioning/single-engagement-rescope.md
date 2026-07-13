# Re-scope: FDE-os as a Single-Engagement Knowledge-Artifact Factory

> **Decision artifact (branch `feat/rescope-single-engagement`).** Narrows FDE-os from a federated,
> cross-company "FDE hub" to a **single client engagement** as the unit of scope, scale, and
> ownership. Written for a consulting/SI delivery context; deliberately anonymized. Sources at the end.

## Why re-scope (the market forces this)

Forward-deployed engineering is now a board-level operating model — Palantir's origin, then AWS's
**$1B forward-deployed-AI-engineer** program (30 Jun 2026), plus rival OpenAI/Anthropic enterprise
JVs (May 2026) and Deloitte/McKinsey FDE hiring. When everyone embeds engineers, the embedding stops
being a differentiator.

The essay the market is quoting — a16z, **"The Palantirization of Everything"** (16 Jan 2026) — is
the warning that reframes this repo. Firms that "over-rotate into forward deployment without a strong
product spine" get no increasing returns to scale and no durable moat: *"you're 'Accenture for X'
with a nicer front-end."* Palantir's difference is **architectural** — FDEs assemble **reusable
primitives** (data models, workflow engines, access controls), so a mature client needs *declining*
forward-deployed effort over time. Margins expand; work compounds.

**A pure services firm keeps engagement intensity constant, so nothing compounds.** That is the trap
this re-scope is designed to escape — *at the unit where it can actually be executed: one engagement.*

## The scope change

| | Before (over-scoped) | After (this branch) |
|---|---|---|
| **Unit** | A global FDE hub spanning many companies. | **One client engagement.** |
| **Owner** | Ambiguous / firm-wide → ownership politics, pushback. | **The client engagement** is the owner organization. |
| **Value shown** | The framework & architecture. | The **content and its quality** — the mined, evaluated artifacts. |
| **Scale** | Federated, many contributors, "public library." | Deep in one engagement; reuse proven *before* federating. |
| **Next step** | Platform vision. | A concrete pilot on **real, current work**. |

The framework can still *aspire* to be a hub. But adoption is earned one engagement at a time, and the
demonstration is scoped to a single client — the least-political, most-executable owner.

## The reframe: all three layers reduce to knowledge artifacts

Talent, tooling, and knowledge/experience are not three products — they are three views of **one set
of knowledge artifacts**. So FDE-os is, precisely:

> **A framework to MINE → EVALUATE → PACKAGE → ATTEST the knowledge artifacts an engagement produces,
> so each engagement lowers the marginal cost of the next one.**

```
  engagement work ──▶ MINE ──▶ EVALUATE (gate) ──▶ PACKAGE ──▶ ATTEST ──▶ reusable, trusted asset
        ▲                                                                        │
        └──────────────── lowers the cost of the next engagement ◀──────────────┘
```

## Constraints (the defensibility that makes this real)

Three levers separate a compounding asset factory from a prettier deck. All three are *already*
present as FDE-os primitives:

1. **Mechanical capture at the unit of the Skill/agent.** Every engagement emits **versioned,
   eval-gated artifacts by default** — not optional write-ups that depend on individual goodwill.
   Skills/MCP tools are the unit of reuse. → `knowledgefy`, `jd-compiler`, `field-kit-generator`,
   `fde-mcp-server`.
2. **Eval gates as the quality ratchet.** An artifact enters the reusable library only after passing
   an eval — converting tacit "it worked" into a verifiable primitive. This is what makes reuse safe
   and margins expandable. → `true-scorer` (TRUE), `criteria-scorer`, `rag-eval-harness`, `eval-loop`,
   `engagement-readiness` GO/NO-GO.
3. **Access control + proprietary outcome data as the moat.** In 2026, methodology is
   natural-language text — copyable, weakly protectable (trade-secret-fragile; AI output largely
   uncopyrightable). You cannot protect the *words*; you can control **who can run, see, and version
   them**, plus the private client-outcome telemetry no competitor can observe. → **two-layer split:**
   open-source framework (MIT, its own lifecycle) vs **private client content behind RBAC +
   attestation** (`portfolio-trust`, RBAC demo, owner-only private artifacts).

This is the direct answer to the a16z critique: **the moat is not the software and not the method —
it is the eval-validated, domain-tagged corpus of what worked, gated behind access control.** Reuse
must be *mechanically enforced*, not culturally hoped-for. That is what this repo enforces.

## The staffing-trust wedge (the highest-value entry point)

The sharpest concrete pain: a delivery partner must vouch for a person on a client engagement, and a
resume no longer answers three questions —

1. **Reliable?** Can they deliver, handle security, hit the deadline?
2. **Really competent?** A resume is a dead artifact, trivially faked by GenAI. (Most 2026 resumes are
   partly AI-generated; "AI made skills fakeable, and it made proof fakeable.")
3. **Resourceful?** Can they pick up an unfamiliar tech (e.g., Kubernetes) mid-engagement and still ship?

The market has adjacent primitives but **no composition of them**: LinkedIn/Entra Verified ID attest
*who you are*; Open Badges 3.0 attest *course claims*; SLSA/in-toto attest *how an artifact was built*;
git-ai / `Assisted-by:` trailers attest *code authorship*. **Nobody binds non-self-issuable, signed,
third-party vouches to contribution provenance into a portable "this person shipped this" credential.**
That is confirmed white space — and it is exactly what `portfolio-trust` does (non-self-issuable signed
vouches + provenance + CI badge → GO/NO-GO). The per-engagement factory *produces* this evidence as a
byproduct of mechanical capture: the artifacts a person ships, gated and attested, become the proof.

## Concrete next step (tied to real work)

Do not platform. Pick one live engagement and run one loop end-to-end:

- **48-hour pilot:** feed one real engagement's target JD to `jd-compiler` → a competency spine +
  demand matrix; run one deliverable through the eval gates; mint one attested `portfolio-trust`
  vouch. Show the *content quality*, not the architecture.
- **GO/NO-GO pilot:** run `engagement-readiness` (adopted? + works?) against a near-go-live agentic
  deliverable, offline, inside the client perimeter.

Federation is a later, earned step — after one engagement proves the compounding.

## Sources
- a16z, "The Palantirization of Everything," 16 Jan 2026.
- AWS $1B forward-deployed AI engineers — CNBC / Amazon, 30 Jun 2026; Forbes, 10 Jul 2026.
- OpenAI/Anthropic enterprise JVs — TechCrunch, 4 May 2026.
- Skills as the unit of reuse — Anthropic "Skills explained."
- Methodology-as-IP (trade secret / RBAC moat) — Mayer Brown (Dec 2025), Linklaters (2026), Permit.io, dev.to RBAC-for-AI.
- Attestation primitives — Microsoft Entra Verified ID; Open Badges 3.0 (IMS Global); SLSA/in-toto; git-ai / `Assisted-by:` trailer.
- Skills-based / evidence hiring — NACE Job Outlook 2026 (via Testlify); Interview Guys 2026.
- _Research method note: "last30days" signal skill was unavailable in this environment; equivalent recency was obtained via dated web sources (2026-emphasis)._
