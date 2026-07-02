# Instrument 3 — Learn-and-Teach-Back (resourcefulness / learning agility)

> This *is* her test, formalized: *"learn these two tools and show me Monday — if
> you know Claude Code well you can learn them in a day."* The job is a river of
> unfamiliar tools; the skill being measured is how fast someone turns "never seen
> it" into "shipped something and can teach it."

**Setup:** hand the candidate an **unfamiliar** agent-building tool (whatever low-code /
citizen-developer stack you're rolling out that week) on Friday. One-line brief:
*build one working thing with it and be ready to teach it back Monday.*

**Outcome over method — state this explicitly to the candidate:** you may use AI,
read docs, or ask anyone for help. The only rules are (1) don't break the law or
Accenture policy and (2) **you must produce a working result.** *How* they got
unstuck is signal, not a violation — note it, don't penalize it.

**The teach-back matters as much as the build.** These tools exist so *they* can
teach citizen developers. Someone who makes it work but can't explain it fails
half the job.

### Deliverable
1. A **working artifact** built with the tool (a runnable flow / agent / demo).
2. A **1-page or 5-minute teach-back** a non-engineer can follow.

### Rubric → feeds `scorecard.py`

| Signal | Field | Passes when |
|---|---|---|
| Did it run? | `artifact_worked` | the thing actually works, not slides about it |
| Can they teach it? | `teachback_clear` | a non-engineer could repeat the core steps |
| How they unblocked | `got_unstuck` | informational — self-directed unblocking is a plus, never a minus |

**Pass = `artifact_worked` AND `teachback_clear`.** (This is the axis an engineer's own
learn-a-new-tool-in-a-day demo is scored against — the tool eats its own dog food.)

```json
"resourcefulness": { "teach_back": {"artifact_worked": true, "teachback_clear": true, "got_unstuck": true} }
```
