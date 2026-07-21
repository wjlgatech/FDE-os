"use client";

import { useState } from "react";
import { ReportCard, PALETTE } from "@/lib/reportcard";
import { buildGraph, GNode } from "@/lib/graph";

// Play the journey: objectives (dark hubs) with their graded deliveries fanned around them,
// linked by a faint temporal chain. Hover a node for its label; click a card node to jump to
// its entry in the feed (#id). Deterministic layout — no runtime deps, no physics jitter.
export function JourneyGraph({ cards }: { cards: ReportCard[] }) {
  const [hover, setHover] = useState<GNode | null>(null);
  if (cards.length < 2) return null;
  const g = buildGraph(cards);
  const nodeById = new Map(g.nodes.map((n) => [n.id, n]));

  return (
    <div className="panel reveal d3">
      <svg width="100%" viewBox={`0 0 ${g.w} ${g.h}`} role="img" aria-label="Journey graph: objectives and graded deliveries over time">
        {g.edges.map((e, i) => {
          const a = nodeById.get(e.from), b = nodeById.get(e.to);
          if (!a || !b) return null;
          const then = e.kind === "then";
          return (
            <line key={i} x1={a.x} y1={a.y} x2={b.x} y2={b.y}
              stroke={then ? PALETTE.sky : PALETTE.line}
              strokeWidth={then ? 1 : 1.5}
              strokeDasharray={then ? "3 4" : undefined}
              opacity={then ? 0.5 : 0.8} />
          );
        })}
        {g.nodes.map((n) => {
          const isCard = n.kind === "card";
          const el = (
            <g key={n.id} onMouseEnter={() => setHover(n)} onMouseLeave={() => setHover(null)}
               style={{ cursor: isCard ? "pointer" : "default" }}>
              <circle cx={n.x} cy={n.y} r={n.r} fill={isCard ? n.color : "#fff"}
                stroke={n.color} strokeWidth={isCard ? 0 : 2.5} />
              {!isCard && (
                <text x={n.x} y={n.y - n.r - 6} textAnchor="middle" fontSize="11" fontWeight={700}
                  fill={PALETTE.ink}>{trunc(n.label, 28)}</text>
              )}
            </g>
          );
          return isCard ? <a key={n.id} href={`#${n.id}`}>{el}</a> : el;
        })}
        {hover && hover.kind === "card" && (
          <text x={hover.x} y={hover.y - hover.r - 6} textAnchor="middle" fontSize="11"
            fill={PALETTE.ink}>{trunc(hover.label, 34)} · {hover.grade?.toFixed(2)}</text>
        )}
      </svg>
      <p className="muted" style={{ padding: "0 10px 8px" }}>
        Dark hubs = objectives · dots = graded deliveries (size &amp; color by grade) · dashed blue = the path through time.
        Click a delivery to jump to it.
      </p>
    </div>
  );
}

function trunc(s: string, n: number): string {
  return s.length > n ? s.slice(0, n - 1) + "…" : s;
}
