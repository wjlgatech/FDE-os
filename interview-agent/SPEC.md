# Conversational evidence collector — spec

## Why
The vetting scorecard needs *evidence*. Collecting it is the slow part. The most information-rich
COLLECT method is a **structured conversation** — the approach behind evidence-based trait
inference: don't ask a person to rate themselves, probe their **specific past behavior** and infer
signals from what they actually say, then **validate the inference against ground truth**
downstream. This agent does the *infer* half; the work sample and reference do the *validate* half.

## What it is (and is not)
- **Is:** an intake interviewer that covers three areas — reliability, resourcefulness, technical
  depth — with one adaptive follow-up each, then extracts structured, quoted evidence + the exact
  next evidence to collect.
- **Is not:** a decision. By construction an interview can reach at most the **claimed** tier for
  reliability/technical (a story is not a vouch or a graded build), so it **never yields a GO on its
  own**. That honesty is the point — it prevents a smooth talker from shortcutting the gate.

## Flow (server-orchestrated, `api/interview.js`)
```
turn ─▶ turn ─▶ … ─▶ [[COMPLETE]] ─▶ extract ─▶ { dossier, candidate, next_evidence }
  one question at a time            hard cap    strict-JSON, schema-validated, one repair retry
```
- **turn**: system prompt fixes the three areas, behavior-only questions, one follow-up per area,
  emits `[[COMPLETE]]` when covered. Hard cap `MAX_TURNS=8` so it always terminates.
- **extract**: infers a tier per area — `observed_story` | `claimed` | `not_evidenced` — with the
  strongest supporting quote. "When unsure, choose the lower tier." Fabrication is designed out:
  no support ⇒ `not_evidenced`, never a fake pass. Output is validated; invalid ⇒ one repair ⇒ else
  a 502 (honest failure, not a guess).

## Evidence → scorecard mapping (honest tiers)
| area | best an interview can assert | so `candidate.json` gets | still needs |
|---|---|---|---|
| reliability | a past story | `references: []` (a story ≠ a vouch) | a **structured reference** |
| technical | a past story | `work_sample.observed:false` | an **observed work sample** |
| resourcefulness | a learn-a-tool story | `teach_back` set from the story tier | (confirm in the tool demo) |

Result: the intake record scores **NO-GO** by design until the two hard evidences are collected —
and the app hands the user the precise `next_evidence` list to go get them.

## Backend
- LLM via direct provider keys (`GROQ_API_KEY` / `GEMINI_API_KEY` / `NVIDIA_API_KEY`) if set on the
  project; **else** the shared delta-guide proxy (server-to-server, no new secret). Free-tier calls
  are retried. For production reliability, set one provider key on this Vercel project.
- Stateless: the client holds the transcript and posts it each turn.
