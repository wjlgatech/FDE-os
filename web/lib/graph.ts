// "Play the journey" graph model — a dependency-free deterministic layout of the collection.
// Objectives are hubs on a ring; each objective's cards fan out around it; a faint temporal
// chain links cards in the order they shipped. Mirrors the GraphML the CLI exports
// (nodes: objective|card; edges: scores, then) so the two views tell the same story.

import { ReportCard, grade, band, bandColor, PALETTE } from "./reportcard";

export interface GNode {
  id: string;
  kind: "objective" | "card";
  label: string;
  x: number;
  y: number;
  r: number;
  color: string;
  grade?: number;
}
export interface GEdge { from: string; to: string; kind: "scores" | "then"; }
export interface Graph { nodes: GNode[]; edges: GEdge[]; w: number; h: number; }

export function buildGraph(cards: ReportCard[]): Graph {
  const w = 900, h = 560, cx = w / 2, cy = h / 2;
  const objectives = Array.from(new Set(cards.map((c) => c.objective)));
  const nodes: GNode[] = [];
  const edges: GEdge[] = [];
  const objRing = Math.min(cx, cy) * 0.52;

  const objPos = new Map<string, { x: number; y: number }>();
  objectives.forEach((o, i) => {
    const a = (2 * Math.PI * i) / Math.max(1, objectives.length) - Math.PI / 2;
    const x = cx + objRing * Math.cos(a);
    const y = cy + objRing * Math.sin(a);
    objPos.set(o, { x, y });
    nodes.push({ id: objId(o), kind: "objective", label: o, x, y, r: 9, color: PALETTE.ink });
  });

  // cards fan out around their objective hub, ordered in time within the objective
  const byObj = new Map<string, ReportCard[]>();
  for (const c of cards) (byObj.get(c.objective) ?? byObj.set(c.objective, []).get(c.objective)!).push(c);
  for (const [obj, cs] of byObj) {
    const hub = objPos.get(obj)!;
    const ordered = [...cs].sort((a, b) => Date.parse(a.created_at) - Date.parse(b.created_at));
    ordered.forEach((c, i) => {
      const spread = ordered.length > 1 ? (i / (ordered.length - 1) - 0.5) : 0;
      const outAngle = Math.atan2(hub.y - cy, hub.x - cx) + spread * 0.9;
      const dist = 78 + (i % 2) * 26;
      const x = hub.x + dist * Math.cos(outAngle);
      const y = hub.y + dist * Math.sin(outAngle);
      const g = grade(c);
      nodes.push({ id: c.id, kind: "card", label: c.delivery, x, y, r: 6 + g * 6, color: bandColor(band(g)), grade: g });
      edges.push({ from: c.id, to: objId(obj), kind: "scores" });
    });
  }

  // temporal "then" chain across ALL cards (the journey through time)
  const chrono = [...cards].sort((a, b) => Date.parse(a.created_at) - Date.parse(b.created_at));
  for (let i = 1; i < chrono.length; i++) edges.push({ from: chrono[i - 1].id, to: chrono[i].id, kind: "then" });

  return { nodes, edges, w, h };
}

function objId(o: string): string {
  return "obj:" + o;
}
