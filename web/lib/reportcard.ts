// The report-card data contract + grading/rollup logic — a faithful TS mirror of
// src/anyagent/domain/reportcard.py. The Python CLI and this webapp render from the SAME
// collection.json; keeping the math identical here is what stops the two surfaces drifting.

export const GRADE_TARGET = 0.7;
export const AT_RISK = 0.4;
export const SANDBAG = 0.9;
const MOMENTUM_EPS = 0.02;
export const PERIOD_DAYS: Record<string, number> = { day: 1, week: 7, month: 30, quarter: 90 };

export interface KeyResult {
  text: string;
  target: string;
  score: number;
  evidence: string;
}

export interface ReportCard {
  id: string;
  delivery: string;
  objective: string;
  key_results: KeyResult[];
  created_at: string;
}

export type Band = "on-track" | "progress" | "at-risk" | "sandbagged?";
export type Direction = "improving" | "steady" | "declining";

export function grade(card: ReportCard): number {
  if (!card.key_results.length) return 0;
  const mean = card.key_results.reduce((s, k) => s + k.score, 0) / card.key_results.length;
  return round3(mean);
}

export function band(g: number): Band {
  if (g >= SANDBAG) return "sandbagged?";
  if (g >= GRADE_TARGET) return "on-track";
  if (g >= AT_RISK) return "progress";
  return "at-risk";
}

export function directionOf(momentum: number): Direction {
  if (momentum > MOMENTUM_EPS) return "improving";
  if (momentum < -MOMENTUM_EPS) return "declining";
  return "steady";
}

export interface Rollup {
  period: string;
  count: number;
  avgGrade: number;
  prevAvg: number;
  momentum: number;
  direction: Direction;
}

export function rollup(cards: ReportCard[], period: string, now: Date): Rollup {
  const days = PERIOD_DAYS[period] ?? 7;
  const cur = cards.filter((c) => inWindow(c.created_at, now, 0, days));
  const prev = cards.filter((c) => inWindow(c.created_at, now, days, 2 * days));
  const avg = avgGrade(cur);
  const prevAvg = avgGrade(prev);
  const momentum = round3(avg - prevAvg);
  return { period, count: cur.length, avgGrade: avg, prevAvg, momentum, direction: directionOf(momentum) };
}

function avgGrade(cards: ReportCard[]): number {
  if (!cards.length) return 0;
  return round3(cards.reduce((s, c) => s + grade(c), 0) / cards.length);
}

function inWindow(iso: string, now: Date, loDays: number, hiDays: number): boolean {
  const age = ageDays(now, iso);
  return age !== null && loDays <= age && age < hiDays;
}

function ageDays(now: Date, iso: string): number | null {
  const t = Date.parse(iso);
  if (Number.isNaN(t)) return null;
  return (now.getTime() - t) / 86_400_000;
}

function round3(n: number): number {
  return Math.round(n * 1000) / 1000;
}

// "As of" the latest delivery — the honest default for a proof page (populated windows even if
// the repo is browsed weeks later). A live production build could pass `new Date()` instead.
export function asOf(cards: ReportCard[]): Date {
  const times = cards.map((c) => Date.parse(c.created_at)).filter((t) => !Number.isNaN(t));
  return times.length ? new Date(Math.max(...times)) : new Date();
}

// Anthropic brand-as-code palette — identical to the Python renderer.
export const PALETTE = {
  paper: "#faf9f5", ink: "#141413", clay: "#d97757", sky: "#6a9bcc",
  moss: "#788c5d", line: "#e6e2d8", muted: "#6b675e", risk: "#c0392b",
};

export function bandColor(b: Band): string {
  return { "on-track": PALETTE.moss, progress: PALETTE.clay, "at-risk": PALETTE.risk, "sandbagged?": PALETTE.sky }[b];
}

export function directionColor(d: Direction): string {
  return { improving: PALETTE.moss, declining: PALETTE.risk, steady: PALETTE.muted }[d];
}

export function scoreColor(score: number): string {
  return score >= 0.7 ? PALETTE.moss : score >= 0.4 ? PALETTE.clay : PALETTE.risk;
}
