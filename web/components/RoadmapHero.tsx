import { ReportCard, grade, band, bandColor, rollup, directionColor } from "@/lib/reportcard";

const ARROW = { improving: "↑", declining: "↓", steady: "→" } as const;

// The every-turn Roadmap Card as the page hero: where we are · what we achieved · heading · why.
// Position is derived honestly from the collection; next/why are optional narrative (props).
export function RoadmapHero({
  cards, now, next, why,
}: { cards: ReportCard[]; now: Date; next?: string; why?: string }) {
  const latest = cards.length ? [...cards].sort((a, b) => Date.parse(a.created_at) - Date.parse(b.created_at)).at(-1)! : null;
  const week = rollup(cards, "week", now);
  const g = latest ? grade(latest) : 0;
  const b = band(g);

  const pos = latest ? (
    <>
      {cards.length} deliveries · latest <b>{latest.delivery}</b> graded{" "}
      <b style={{ color: bandColor(b) }}>{g.toFixed(2)}</b> ({b}) · week avg {week.avgGrade.toFixed(2)}{" "}
      <span style={{ color: directionColor(week.direction) }}>
        {ARROW[week.direction]} {week.momentum >= 0 ? "+" : ""}{week.momentum.toFixed(2)} ({week.direction})
      </span>
    </>
  ) : ("No cards recorded yet — this is the first.");

  const heading = next ?? `Close the gap to target 0.70 (currently ${week.avgGrade.toFixed(2)}, ${week.direction}).`;
  const reason = why ?? "Every delivery is graded so momentum and direction stay honest and visible.";

  return (
    <div className="hero">
      <div className="cell pos reveal d1"><div className="lbl">📍 Where we are on the roadmap</div><div className="txt">{pos}</div></div>
      <div className="cell win reveal d2"><div className="lbl">✅ What we achieved this time</div>
        <div className="txt">{latest ? <><b>{latest.delivery}</b> — {latest.objective}</> : "This is the first tracked delivery."}</div></div>
      <div className="cell next reveal d3"><div className="lbl">🎯 Where we're heading next</div><div className="txt">{heading}</div></div>
      <div className="cell why reveal d4"><div className="lbl">🧭 Why</div><div className="txt">{reason}</div></div>
    </div>
  );
}
