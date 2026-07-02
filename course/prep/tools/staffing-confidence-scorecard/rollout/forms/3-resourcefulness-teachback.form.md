# Microsoft Form 3 — Learn-and-Teach-Back Score (reviewer fills this)

Reviewer completes after the candidate's teach-back of an **unfamiliar** tool they were
given ~1 day earlier (see [`../../instruments/resourcefulness-teachback.md`](../../instruments/resourcefulness-teachback.md)).
Remind the candidate up front: **use AI, docs, anyone — just produce a working result and be able
to teach it.** How they got unstuck is signal, never a penalty.

---

**Form title:** Learn-and-Teach-Back Score — Staffing Confidence
**Description:** Reviewer use. Did they turn "never seen this tool" into "it works and I can teach it" inside the window?

---

**Q1.** Candidate id (anonymized) `[Short text, required]`
**Q2.** Which unfamiliar tool were they given? `[Short text, required]`
**Q3.** Did the artifact they built **actually run** (not slides about it)? `[Choice, required]` — Yes · Partially · No
**Q4.** Could a **non-engineer** repeat the core steps from their teach-back? `[Choice, required]` — Yes · Somewhat · No
**Q5.** How did they get unstuck? `[Choice, required]` — Self-directed (docs/AI/asked, then solved) · Needed hand-holding · Didn't get unstuck
**Q6.** One line: what they shipped and how they explained it `[Long text, required]`

---

## Answer → scorer mapping

| Form answer | JSON field |
|---|---|
| Q3 = Yes | `"artifact_worked": true` |
| Q4 = Yes | `"teachback_clear": true` |
| Q5 = Self-directed | `"got_unstuck": true` (informational — a plus, never gates) |

**Pass = `artifact_worked` AND `teachback_clear`.**

```json
"resourcefulness": { "teach_back": {"artifact_worked": true, "teachback_clear": true, "got_unstuck": true} }
```
