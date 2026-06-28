#!/usr/bin/env python3
"""eval-loop — turn a sequence of scored artifact versions into a kept winner + a run-log.

The primitive FDE-os was missing (per docs/research/agent-loops-critical-eval.md): *edit a version →
score it → keep if better, revert if worse → log the trajectory.* Git is the memory — the run-log is
a committed markdown file. The scorer is pluggable (criteria-scorer / true-scorer / rag-eval-harness);
the keep/revert + run-log logic is the deterministic, tested core here.

The run-log adopts the source article's proven 4-column shape: Round | Change | Score | Verdict.

Two modes:
  log         explicit scored rounds (a rounds.json) -> run-log.md   (manual logging; fully testable)
  score-each  artifact version files + a scorer command -> score each -> decide -> run-log.md

Usage:
  python3 eval_loop.py log <rounds.json> --out run-log.md
  python3 eval_loop.py score-each --scorer "python3 .../criteria_score.py score {file} crit.json" \
      v1.md v2.md v3.md --out run-log.md
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys

SCORE_RE = re.compile(r"(?:score[^0-9]*)?(\d+(?:\.\d+)?)%?", re.IGNORECASE)


def _max_gain(cur: tuple | None, label: str, delta: float) -> tuple:
    """Keep the larger of the current best (label, delta) gain and a new candidate."""
    if cur is None or delta > cur[1]:
        return (label, delta)
    return cur


def decide(rounds: list[dict]) -> dict:
    """Core keep/revert logic. rounds = [{label, change, score}, ...] in order.

    Round 0 is the baseline (verdict 'baseline'). Each later round is 'accept' iff its score strictly
    beats the best-so-far (a tie reverts — accept requires real improvement); otherwise 'revert' and
    the best-so-far is unchanged. Returns {decisions:[...], winner_label, winner_score, best_gain}.
    """
    decisions: list[dict] = []
    best_score = None
    best_label = None
    best_gain = None  # (label, delta) of the largest accepted improvement
    for i, r in enumerate(rounds):
        score = float(r["score"])
        label = r.get("label", f"round-{i}")
        change = r.get("change", "")
        if i == 0:
            verdict, delta = "baseline", None
            best_score, best_label = score, label
        elif score > best_score:
            delta = round(score - best_score, 4)
            verdict = "accept"
            best_gain = _max_gain(best_gain, label, delta)
            best_score, best_label = score, label
        else:
            verdict, delta = "revert", round(score - best_score, 4)
        decisions.append({"round": i, "label": label, "change": change,
                          "score": score, "verdict": verdict, "delta": delta})
    return {"decisions": decisions, "winner_label": best_label,
            "winner_score": best_score, "best_gain": best_gain}


def render_run_log(result: dict, title: str = "Run log") -> str:
    """Render the article's 4-column run-log table + a 'what the loop learned' summary."""
    lines = [f"# {title}", "", "| Round | Change | Score | Verdict |", "|---|---|---|---|"]
    for d in result["decisions"]:
        mark = {"baseline": "", "accept": " ✅", "revert": " ❌"}[d["verdict"]]
        delta = "" if d["delta"] is None else f" ({d['delta']:+})"
        lines.append(f"| {d['round']} | {d['change'] or d['label']} | {d['score']}{delta} | {d['verdict']}{mark} |")
    lines.append("")
    lines.append(f"**Winner:** {result['winner_label']} (score {result['winner_score']}).")
    if result["best_gain"]:
        lbl, gain = result["best_gain"]
        lines.append(f"**What the loop learned:** the largest single gain ({gain:+}) came from "
                     f"\"{lbl}\". Git holds the full trajectory; reverted rounds stay in history.")
    return "\n".join(lines) + "\n"


def _score_file(scorer_cmd: str, path: str) -> float:
    """Run a scorer command on a file and parse a numeric score from its stdout. {file} is substituted."""
    cmd = scorer_cmd.replace("{file}", path)
    out = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    text = out.stdout + out.stderr
    m = SCORE_RE.search(text)
    if not m:
        raise ValueError(f"could not parse a score from scorer output for {path}:\n{text[:200]}")
    val = float(m.group(1))
    return val / 100.0 if "%" in text[m.start():m.end() + 1] or val > 1 else val


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)

    lg = sub.add_parser("log")
    lg.add_argument("rounds", help="JSON list of {label, change, score} in order")
    lg.add_argument("--out", default=None)
    lg.add_argument("--title", default="Run log")

    se = sub.add_parser("score-each")
    se.add_argument("versions", nargs="+", help="artifact version files in order")
    se.add_argument("--scorer", required=True, help="scorer command; {file} is substituted")
    se.add_argument("--out", default=None)
    se.add_argument("--title", default="Run log")

    args = ap.parse_args()

    if args.cmd == "log":
        with open(args.rounds, encoding="utf-8") as fh:
            rounds = json.load(fh)
    else:  # score-each
        rounds = []
        for i, path in enumerate(args.versions):
            score = _score_file(args.scorer, path)
            rounds.append({"label": path, "change": path, "score": score})

    result = decide(rounds)
    log = render_run_log(result, title=args.title)
    if args.out:
        out_dir = os.path.dirname(os.path.abspath(args.out))
        os.makedirs(out_dir, exist_ok=True)
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(log)
        print(f"run-log -> {args.out}")
    print(log)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
