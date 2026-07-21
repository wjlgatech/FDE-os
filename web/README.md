# AnyAgent — Journey webapp (per codebase)

The **Journey** is the self-updating progress view for one codebase: a Vercel-hosted brief that
renders this repo's AnyAgent report cards. One webapp per repo (like `fde-os-brief.vercel.app`),
each reading *its own* `collection.json`.

## The data contract (why this doesn't drift)

The app renders **data, not embedded HTML**. `data/collection.json` is the single source of truth —
the same file the `anyagent report` CLI writes and reads. `lib/reportcard.ts` is a faithful mirror
of `src/anyagent/domain/reportcard.py` (grade = mean of KR scores; band thresholds 0.4/0.7/0.9;
rollup = this window vs the one before). Keep the math in sync and the CLI and webapp can never
disagree about a grade.

## UX zones (`app/page.tsx`)

1. **Roadmap Hero** — the every-turn card: 📍 where we are · ✅ this time · 🎯 heading · 🧭 why.
2. **Momentum strip** — day/week/month/quarter tiles with direction arrows.
3. **Trend line** — grade over time vs the 0.70 target; the polyline draws itself.
4. **Delivery feed** — reverse-chronological, filter by objective, expand for KRs + **evidence**;
   each card is deep-linkable (`#rc0007`).

All animated in the ADEPT / `/living-knowledge` spirit (staggered fade-up, bars that fill, trend
draw); honors `prefers-reduced-motion`.

## Develop / build

```bash
cd web
pnpm install
pnpm dev              # http://localhost:3000
pnpm build            # static export to ./out  (output: 'export')
pnpm sync             # refresh data/collection.json from ../docs/reportcards/collection.json
```

## Deploy to Vercel

- Set the project **Root Directory** to `web/`. Vercel auto-detects Next.js.
- The pipeline: `anyagent` auto-fires cards → `collection.json` is committed → push → Vercel
  git-integration redeploys. No database — **git is the store**, so the whole journey is versioned
  and PR-reviewable.

## Follow-ups (not in this proof)

- A `report web` CLI command to scaffold this app into any repo (templatize per codebase).
- The "play the graph" view (force-graph over the GraphML: deliveries → objectives, `then` edges).
- The embedded copilot ("ask about this repo's progress"), grounded in `collection.json`.
