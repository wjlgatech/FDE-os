# Microsoft Form 2 — Work-Sample Score (the reviewer fills this while observing)

Not sent to the candidate — the **reviewer** completes it during/after the 90-minute
observed build (see [`../../instruments/technical-work-sample.md`](../../instruments/technical-work-sample.md)).
Same rubric, every candidate, so scores are comparable across the whole center.

---

**Form title:** Work-Sample Score — Staffing Confidence
**Description:** Reviewer use. Score what you observed the candidate build live. Evidence, not impression.

---

**Q1.** Candidate id (anonymized) `[Short text, required]`
**Q2.** Role type `[Choice, required]` — Technical · Non-technical
**Q3.** Did you **observe** them build it fresh (not a portfolio link)? `[Choice, required]` — Yes · No

Score each 0–3 (`0 = absent, 1 = weak, 2 = solid, 3 = excellent`):

**Q4.** Agent runs & calls its tool, incl. the error path `[Choice 0/1/2/3, required]`
**Q5.** Retrieval is grounded — cites the corpus, refuses when unsupported `[Choice 0/1/2/3, required]`
**Q6.** The eval gate is real — it *fails* on an ungrounded answer `[Choice 0/1/2/3, required]`
**Q7.** Code is legible under time pressure — someone could extend it `[Choice 0/1/2/3, required]`
**Q8.** Talks trade-offs unprompted — cost / latency / failure modes `[Choice 0/1/2/3, required]`
**Q9.** One line: strongest and weakest moment you observed `[Long text, required]`

---

## Answer → scorer mapping

- `work_sample.score` = **(Q4+Q5+Q6+Q7+Q8) ÷ 15** → a 0.00–1.00 value.
- `work_sample.observed` = **Q3 = Yes** (if No, the sample can't be attributed → treated as not observed).
- `work_sample.threshold` = **0.70** for a technical role (tune per role on Wed of the rollout).

```json
"technical_competence": { "work_sample": {"observed": true, "score": 0.80, "threshold": 0.70} }
```
_(Example: scores 3,2,3,2,2 → 12/15 = 0.80 → clears the 0.70 bar.)_
