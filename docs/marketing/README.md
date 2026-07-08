# docs/marketing — copy about the project

Marketing copy *about FDE-os itself* (distinct from the Delta series, which is the product's content
layer). Every piece here is **easy enough for a sharp 15-year-old, deep enough for an AI director,
and not allergic to a joke** — and each was scored by the project's own gates before shipping
(dogfooding: a project about eval-gated honesty should gate its own marketing).

| File | What | Gate score |
|---|---|---|
| [`fde-os-longform-article.md`](fde-os-longform-article.md) | Long-form (~7 min) LinkedIn-style article about the project | **11/12** via `true-scorer` (PASS) |
| [`agentic-portfolio-missing-link.md`](agentic-portfolio-missing-link.md) | Long-form (~7 min): why a 60-second AI portfolio won't get you hired — the **attestation gap** (claimed → observed → attested) | **11/12** via `true-scorer` (agent-refined, PASS) |
| [`agentic-native-delivery-org.md`](agentic-native-delivery-org.md) | Long-form (~8 min), **for delivery leadership**: the evidence (MIT 95% / Gartner) that AI failure is *organizational, not model* → an empowering, agentic-native, tech-enforced operating model. No firm named. | **10/12** via `true-scorer` (agent-refined, PASS) |
| [`missing-link-short-post.md`](missing-link-short-post.md) | ~230-word feed post pairing the attestation-gap long-form | **4/4** via `criteria-scorer` (PASS) |
| [`learn-any-domain-10x.md`](learn-any-domain-10x.md) | Long-form (~7 min): learn any field 10× wide **and** deep with AI — the **Map · Ladder · Gate** model, mapped term-by-term to the cognitive science (Ericsson, Roediger & Karpicke, Bjork, Gick & Holyoak…), funny on purpose. Anthropic-style visuals. | **11/12** via `true-scorer` (agent-refined, PASS) |
| [`learn-10x-short-post.md`](learn-10x-short-post.md) | ~220-word feed post pairing the Map·Ladder·Gate long-form | **4/4** via `criteria-scorer` (PASS) |
| [`assets/mlg-*.svg` / `.png`](assets/) | Anthropic-style thumbnail + 2 infographics (Map·Ladder·Gate loop; term-by-term mapping) | — |
| [`short-posts.md`](short-posts.md) | Two ~185-word feed posts (Post 1: "the robot caught the human"; Post 2: "the loop is the skill") | **4/4 each** via `criteria-scorer` (PASS) |
| [`assets/ml-*.svg` / `.png`](assets/) | Thumbnail + 2 infographics for the attestation-gap piece (brand SVG → PNG via `rsvg-convert`) | — |
| [`viral-post-criteria.json`](viral-post-criteria.json) | The criteria the short posts are gated on (number, closing question, ≤230 words, no 2026-suppressed engagement-bait) | — |

## Reproduce the scores

```bash
python3 skills/true-scorer/scripts/score.py docs/marketing/fde-os-longform-article.md
# each short post (extract the body, then):
python3 skills/criteria-scorer/scripts/criteria_score.py score <post.md> \
  docs/marketing/viral-post-criteria.json --threshold 0.75
```

## Posting notes

- **Link in the first comment**, never the body (LinkedIn cuts in-body-link reach ~60%).
- Best window (US): Tue–Thu, 8–10am ET. Don't edit for ~30 min after posting.
- Reply to every comment in the first hour — it's the biggest algorithm lever.
- The long-form article is the depth; the short posts are the exposure that drives to it. Pair them.
- Honesty is the brand: the numbers carry reliability flags, and the copy admits the project's own
  bugs on purpose. Keep it that way.
