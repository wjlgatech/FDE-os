# Field note — auditing FDE-os against the "AI Agent FDE" talk (2026-07-17)

Source: a talk breakdown on the FDE role in the AI era (five theses: new species · last mile ·
talent profile · trust mechanism · organizational feedback loop), provided by the user. This note
records what the audit found and **what we changed because of it**.

## The audit: five theses vs the repo

| # | Talk thesis | FDE-os today | Verdict |
|---|---|---|---|
| 1 | **New species** — AI-native FDE inside the engineering org, influencing core product; anti-pattern: body-leasing | The repo *is* an engineering practice system (skills, gates, MCP server), not a consulting binder; the single-engagement re-scope (Bo Zhang) already rejects body-leasing | ✅ aligned — insight is organizational, recorded here |
| 2 | **Last mile + Outcome-Based Model** — clients pay for the result; FDE turns "almost ready" into "works here" | Three artifact-level gates (true-scorer, criteria-scorer, rag-eval-harness) but **no engagement-level outcome gate** — nothing encoded "what does this engagement owe the client, and is it measured?" | ❌ **the real gap → built [`skills/outcome-contract`](../../skills/outcome-contract/SKILL.md)** |
| 3 | **Talent = agency + responsibility over skill** — portfolio of real agents, not prompt wrappers; anti-pattern: tool-users without engineering fundamentals | readiness-rubric + scorecard exist and test fundamentals; the portfolio/receipts thesis is the repo's spine | 🟡 partial — rubric doesn't yet score *agency/ego/listening* signals; candidate for a later rubric extension, not rushed today |
| 4 | **Trust concretized onto the person** — barista/omakase; enterprises bet on a person, not an API | **portfolio-trust literally implements this**: signed, non-self-issuable vouches; provenance; GO/NO-GO. The talk independently validates the attestation-gap thesis | ✅ convergent — name it in marketing, don't rebuild it |
| 5 | **FDE as product mature-er** — field work for one client becomes a template for all; anti-pattern: siloed FDEs rebuilding hacks | README Objective 3 *is* this flywheel; field-kit-generator turns engagement learnings into forkable kits | ✅ aligned in design — the loop's enforcement (engagement → template, measured) can now ride on outcome-contract reports |

## What we learned (compressed)

1. **The one mechanism we lacked was the outcome contract.** "Outcome-based" is a pricing slide
   until outcomes are data with evidence rules. Shipped: contract-as-JSON, PASS only on measured
   evidence meeting target, claimed ≠ measured (downgraded loudly), no evidence ⇒ NOT_MEASURED,
   gate cannot pass on unmeasured blocking items, CI exit codes. 21 tests.
2. **Two of our core bets got independent validation** — trust-as-a-person (portfolio-trust) and
   field-as-laboratory (the flywheel). When an outside practitioner's talk lands on the same
   mechanisms, that's convergent evidence, not coincidence.
3. **The talent insight worth keeping:** *responsibility over skill* — skills commoditize; owning
   an outcome doesn't. That's precisely why the outcome contract names an engagement owner's
   obligations as data. The rubric extension (agency/ego/listening) is queued, not shipped —
   scoring soft signals deterministically needs design, and a rushed proxy would be a fake gate.

## Changed in this commit

- `skills/outcome-contract/` — scorer + 21 tests + example + SKILL.md (runs in `make check`).
- This field note.
