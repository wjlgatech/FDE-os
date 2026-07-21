import { ReportCard, grade, GRADE_TARGET, PALETTE } from "@/lib/reportcard";

// Grade over time vs the 0.70 target — the "are we improving?" proof. The polyline draws
// itself on load (see .trend polyline in globals.css).
export function TrendLine({ cards }: { cards: ReportCard[] }) {
  if (cards.length < 2) return null;
  const w = 900, h = 180, pad = 28;
  const ordered = [...cards].sort((a, b) => Date.parse(a.created_at) - Date.parse(b.created_at));
  const n = ordered.length;
  const pts = ordered.map((c, i) => {
    const x = pad + ((w - 2 * pad) * i) / (n - 1);
    const y = h - pad - (h - 2 * pad) * grade(c);
    return `${x.toFixed(1)},${y.toFixed(1)}`;
  });
  const targetY = h - pad - (h - 2 * pad) * GRADE_TARGET;
  return (
    <div className="panel reveal d3">
      <svg className="trend" width="100%" viewBox={`0 0 ${w} ${h}`} role="img"
           aria-label="Grade trend over time versus the 0.70 target">
        <line x1={pad} y1={targetY} x2={w - pad} y2={targetY} stroke={PALETTE.line} strokeDasharray="4" />
        <text x={w - pad} y={targetY - 5} textAnchor="end" fill={PALETTE.muted} fontSize="11">target 0.70</text>
        <polyline fill="none" stroke={PALETTE.clay} strokeWidth="2.5" points={pts.join(" ")} />
        {ordered.map((c, i) => {
          const [x, y] = pts[i].split(",").map(Number);
          return <circle key={c.id} cx={x} cy={y} r="3.5" fill={PALETTE.clay} />;
        })}
      </svg>
    </div>
  );
}
