import { ReportCard, rollup, directionColor } from "@/lib/reportcard";

const ARROW = { improving: "↑", declining: "↓", steady: "→" } as const;

// Day / week / month / quarter momentum tiles — "are we winning?" at a glance.
export function MomentumStrip({ cards, now }: { cards: ReportCard[]; now: Date }) {
  const periods = ["day", "week", "month", "quarter"];
  return (
    <div className="tiles reveal d2">
      {periods.map((p) => {
        const r = rollup(cards, p, now);
        const color = directionColor(r.direction);
        return (
          <div className="tile" key={p}>
            <div className="p">{p}</div>
            <div className="v">{r.avgGrade.toFixed(2)}</div>
            <div className="d" style={{ color }}>
              {ARROW[r.direction]} {r.momentum >= 0 ? "+" : ""}{r.momentum.toFixed(2)} {r.direction}
            </div>
            <div className="k">{r.count} deliveries · prior {r.prevAvg.toFixed(2)}</div>
          </div>
        );
      })}
    </div>
  );
}
