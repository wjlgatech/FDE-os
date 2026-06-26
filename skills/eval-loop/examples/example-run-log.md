# Autoresearch run log (reproduced from the source article)

| Round | Change | Score | Verdict |
|---|---|---|---|
| 0 | baseline prompt | 0.41 | baseline |
| 1 | require a concrete number | 0.68 (+0.27) | accept ✅ |
| 2 | restrict buzzwords | 0.79 (+0.11) | accept ✅ |
| 3 | add example + audience framing | 0.9 (+0.11) | accept ✅ |
| 4 | 80-word cap | 0.82 (-0.08) | revert ❌ |
| 5 | revert word cap | 0.9 (+0.0) | revert ❌ |

**Winner:** r3 (score 0.9).
**What the loop learned:** the largest single gain (+0.27) came from "r1". Git holds the full trajectory; reverted rounds stay in history.
