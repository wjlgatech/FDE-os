# Instrument 2 — Observed Work Sample (technical competence)

> The single highest-validity predictor of job performance (Schmidt & Hunter:
> work sample adds ~24% over cognitive ability alone). It answers the doubt she
> named directly — *"I don't know how much of what they built was actually them."*
> So it is **fresh and observed**, not a portfolio link.

**Format:** one standardized 90-minute task, done live (screen-shared) or as a
timeboxed take-home with a 15-min live walkthrough. The FDE work is the task:

1. **Build a small tool-using agent** — one real tool call, handle the failure case.
2. **Ground it with retrieval** over a tiny provided corpus — it must cite, not bluff.
3. **Ship an eval gate** — a check that fails loudly when the answer is ungrounded.

Reuse FDE-os assets so the bar is identical for everyone and not hand-waved:
- coding-room fundamentals → [`../coding-drill-kit/`](../coding-drill-kit/)
- retrieval/grounding metrics → [`../../../../skills/rag-eval-harness/`](../../../../skills/rag-eval-harness/)
- the design-round rubric → [`../coding-drill-kit/design-self-score.json`](../coding-drill-kit/design-self-score.json)

### Rubric (score each 0–1, average → `work_sample.score`)

| # | Graded behavior | 1.0 looks like |
|---|---|---|
| 1 | Agent actually runs & calls the tool | works first try, handles the error path |
| 2 | Retrieval is grounded | answers cite the corpus; refuses when unsupported |
| 3 | The eval gate is real | it *fails* on an ungrounded answer, not just prints |
| 4 | Code is legible under time pressure | someone else could extend it |
| 5 | Talks trade-offs while building | names cost / latency / failure modes unprompted |

**Bar:** `score ≥ 0.70` for a technical role (tune per role). Set `observed: true`
only if you watched them build it — an unobserved sample can't be attributed.

```json
"technical_competence": { "work_sample": {"observed": true, "score": 0.84, "threshold": 0.70} }
```
