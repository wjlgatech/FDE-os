"use client";

import { useMemo, useState } from "react";
import { ReportCard, grade, band, bandColor, scoreColor } from "@/lib/reportcard";

// Reverse-chronological feed of deliveries. Filter by objective; expand a card to see its
// key results + EVIDENCE (verify-don't-vibe — the evidence is the point). Each card is
// deep-linkable via its id anchor (#rc0007).
export function DeliveryFeed({ cards }: { cards: ReportCard[] }) {
  const objectives = useMemo(
    () => Array.from(new Set(cards.map((c) => c.objective))),
    [cards],
  );
  const [active, setActive] = useState<string | null>(null);

  const shown = [...cards]
    .filter((c) => !active || c.objective === active)
    .sort((a, b) => Date.parse(b.created_at) - Date.parse(a.created_at));

  return (
    <div>
      <div className="filters">
        <button className="chip" aria-pressed={active === null} onClick={() => setActive(null)}>
          all ({cards.length})
        </button>
        {objectives.map((o) => (
          <button key={o} className="chip" aria-pressed={active === o} onClick={() => setActive(o)}>
            {o}
          </button>
        ))}
      </div>
      <div className="feed">
        {shown.map((c) => {
          const g = grade(c);
          const b = band(g);
          return (
            <details className="card" key={c.id} id={c.id}>
              <summary>
                <span className="date">{c.created_at.slice(0, 10)}</span>
                <span className="del">{c.delivery}</span>
                <span className="grade" style={{ color: bandColor(b) }}>{g.toFixed(2)}</span>
                <span className="muted">{b}</span>
              </summary>
              <div className="krs">
                {c.key_results.map((k, i) => (
                  <div className="krrow" key={i}>
                    <span>{k.text}</span>
                    <span>
                      <span className="bar">
                        <span style={{ ["--w" as string]: `${Math.round(Math.max(0, Math.min(1, k.score)) * 100)}%`, background: scoreColor(k.score) }} />
                      </span>
                      {k.score.toFixed(2)}
                    </span>
                    {k.evidence && <span className="ev">evidence: {k.evidence} · target: {k.target}</span>}
                  </div>
                ))}
              </div>
            </details>
          );
        })}
      </div>
    </div>
  );
}
