# Instrument 1 — Structured Reference Protocol (reliability)

> Fixes the exact burn: unstructured "will you vouch for them?" is near-noise
> (validity ~.26). A **structured** reference asking about specific past behaviors
> is one of the strongest predictors there is. Same questions, every candidate.

**Who to ask:** 2 people who *actually worked with* the candidate on delivery — a
**client team** lead OR an **internal team** lead both count. Not a friend, not a
name they picked because it's safe. If they can't produce one person who ran a
project alongside them, that itself is the answer.

**How to run (5 min each):** send as a Microsoft Form or ask live and type the
answers. Keep it to work behavior — never personal attributes.

### Questions (forced-choice; the scale is the point)

1. Did they **show up** — meetings, standups, client calls — without you chasing them? `always / mostly / sometimes / no`
2. Did they **do what they said** they'd do by the date they said? `always / mostly / sometimes / no`
3. When something slipped, did they **communicate it proactively**, or did you find out late? `proactive / late / went dark`
4. Were they **reachable** during the engagement? `always / mostly / hard to reach`
5. Did they **deliver end-to-end**, or hand off a half-done piece? `end-to-end / needed rescue`
6. **The killer question:** would you **staff them on a client-facing role again**? `yes / no` — *and why in one line.*
7. Did they **ever no-show a client meeting or go dark**? `never / once / repeatedly`

### Scoring → feeds `scorecard.py`

- Any answer of **"went dark" (Q3) or "once/repeatedly" (Q7)** → set `went_dark_or_noshow: true` → **automatic NO-GO**. This is non-negotiable; it is the failure that damages the recommender.
- **"would staff again = yes"** from someone who worked with them → `would_staff_again: true`.
- Two independent "yes" references → a `⟳ pattern` (one great outcome can be an accident; a pattern can't).

```json
"reliability": { "references": [
  {"source": "client_team", "worked_with": true, "would_staff_again": true, "went_dark_or_noshow": false}
]}
```
