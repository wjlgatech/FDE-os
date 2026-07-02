# Microsoft Form 1 — Reliability Reference (send to the referee)

Paste each block into Microsoft Forms (**+ Add new** per question). Type in `[brackets]`.
Turn ON **"Shuffle options" = off** and **"Required" = on** for every question.
Send to **someone who worked with the candidate on delivery** — a client-team lead OR an
internal-team lead (both count). Ask **two**.

---

**Form title:** Delivery Reference — Staffing Confidence
**Description:** 5 minutes. About how this person worked on a past engagement — behavior only, kept confidential. There are no wrong answers; candor protects your own team.

---

**Q1.** Your relationship to the candidate `[Choice, required]`
- Client-team lead I reported to / worked alongside
- Internal Accenture team lead / peer on the same project
- Other (please specify) `[enable "Other"]`

**Q2.** Did they **show up** — meetings, standups, client calls — without being chased? `[Choice, required]`
- Always  ·  Mostly  ·  Sometimes  ·  No

**Q3.** Did they **do what they said** they would, by the date they said? `[Choice, required]`
- Always  ·  Mostly  ·  Sometimes  ·  No

**Q4.** When something slipped, did they **flag it proactively** or did you find out late? `[Choice, required]`
- Flagged it proactively  ·  Found out late  ·  They went dark

**Q5.** Were they **reachable** during the engagement? `[Choice, required]`
- Always  ·  Mostly  ·  Hard to reach

**Q6.** Did they **deliver end-to-end**, or hand off a half-done piece? `[Choice, required]`
- Delivered end-to-end  ·  Needed rescue

**Q7. (the decider)** Would you **staff them on a client-facing role again**? `[Choice, required]`
- Yes  ·  No

**Q8.** In one line — **why** that answer to Q7? `[Long text, required]`

**Q9.** Did they **ever no-show a client meeting or go dark**? `[Choice, required]`
- Never  ·  Once  ·  Repeatedly

---

## Answer → scorer mapping (fill one `references[]` entry from each response)

| Form answer | JSON field |
|---|---|
| Q1 = client-team | `"source": "client_team"` (else `"internal_team"`) |
| always relationship on a real project | `"worked_with": true` |
| Q7 = Yes | `"would_staff_again": true` |
| **Q4 = "went dark" OR Q9 = Once/Repeatedly** | `"went_dark_or_noshow": true` → **automatic NO-GO** |
| Q4 = proactively | `"communicated_proactively": true` |
| Q6 = end-to-end | `"delivered_end_to_end": true` |
