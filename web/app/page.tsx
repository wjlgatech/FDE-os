import collection from "@/data/collection.json";
import config from "@/data/config.json";
import { ReportCard, asOf } from "@/lib/reportcard";
import { RoadmapHero } from "@/components/RoadmapHero";
import { MomentumStrip } from "@/components/MomentumStrip";
import { TrendLine } from "@/components/TrendLine";
import { DeliveryFeed } from "@/components/DeliveryFeed";
import { JourneyGraph } from "@/components/JourneyGraph";

// The Journey — one per codebase. Reads the committed collection.json (the data contract) at
// build time (SSG) and renders the self-updating progress view. Replace data/collection.json
// (via `npm run sync`) and redeploy; Vercel's git integration does this on every push.
// Repo identity comes from data/config.json so the scaffolder sets it without patching code.

export default function Page() {
  const cards = collection as ReportCard[];
  const now = asOf(cards);
  return (
    <main className="wrap">
      <p className="kicker reveal">ANYAGENT · JOURNEY · {config.repo}</p>
      <h1 className="reveal d1">{config.tagline}</h1>
      <p className="muted reveal d1">
        Self-updating from graded, evidence-backed deliveries. As of {now.toISOString().slice(0, 10)}.
      </p>

      <RoadmapHero cards={cards} now={now} />

      <h2>Momentum</h2>
      <MomentumStrip cards={cards} now={now} />

      <h2>Trend — grade vs the 0.70 target</h2>
      <TrendLine cards={cards} />

      <h2>Play the journey</h2>
      <JourneyGraph cards={cards} />

      <h2>Deliveries</h2>
      <DeliveryFeed cards={cards} />

      <p className="muted" style={{ marginTop: 40 }}>
        {cards.length} cards · data contract: <code>reportcards/collection.json</code> · rendered by
        the same grading logic as the <code>anyagent report</code> CLI.
      </p>
    </main>
  );
}
