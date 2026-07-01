#!/usr/bin/env python3
"""TRUE-scorer — the publish gate for Delta Field Manuals.

TRUE = Transferable (model), Reusable (forkable asset), Understandable (15-yo-legible),
Experience-able (a felt "try this"). Each letter scores 0–3.

Ship threshold (the gate's whole point): **total >= 10 AND every letter >= 2.**

Two layers:
  - `gate(scores)` — the deterministic threshold. This is the load-bearing, fully-tested core.
  - `heuristic_scores(text)` — structural signals (presence of a Field Kit link, a "try this"
    exercise, a named model, jargon density) that give an agent a defensible *baseline*. The
    final 0–3 per letter is the agent's call combining these signals with semantic judgment
    (see SKILL.md). The script never invents a pass: heuristics cap, the agent confirms.

Usage:
  python3 score.py <draft.md>                 # heuristic baseline + gate verdict
  python3 score.py --scores T=3,R=3,U=3,E=1   # apply the gate to explicit per-letter scores
"""
from __future__ import annotations

import argparse
import os
import re
import sys

LETTERS = ("T", "R", "U", "E")
SHIP_TOTAL = 10
SHIP_MIN_LETTER = 2


def gate(scores: dict[str, int]) -> tuple[bool, list[str]]:
    """The ship gate: total >= 10 AND every letter >= 2. Returns (passed, reasons)."""
    reasons: list[str] = []
    for ltr in LETTERS:
        if ltr not in scores:
            reasons.append(f"missing score for {ltr}")
    if reasons:
        return False, reasons
    total = sum(scores[ltr] for ltr in LETTERS)
    below = [ltr for ltr in LETTERS if scores[ltr] < SHIP_MIN_LETTER]
    if total < SHIP_TOTAL:
        reasons.append(f"total {total} < {SHIP_TOTAL}")
    for ltr in below:
        reasons.append(f"{ltr}={scores[ltr]} < {SHIP_MIN_LETTER} (no letter may be below {SHIP_MIN_LETTER})")
    return (not reasons), reasons


def heuristic_scores(text: str) -> tuple[dict[str, int], dict[str, str]]:
    """Structural baseline per letter. Conservative: a signal raises the floor, it never
    guarantees a 3. The agent refines upward/downward with semantic judgment."""
    low = text.lower()
    notes: dict[str, str] = {}

    # R — Reusable: is a forkable asset linked/named?
    has_kit = bool(re.search(r"field[\s-]?kit|skill\.md|field-kits/|/skill|forkable|mega-prompt", low))
    has_run = bool(re.search(r"how to run|run it|fork (it|and)|download", low))
    R = 3 if (has_kit and has_run) else 2 if has_kit else 1 if "you could build" in low else 0
    notes["R"] = f"kit-linked={has_kit}, run-instructions={has_run}"

    # E — Experience-able: a concrete "try this" exercise?
    has_try = bool(re.search(r"try it|try this|the \d+-?min|10-minute|do the exercise|run the experiment|count (how many|the)", low))
    E = 3 if has_try and re.search(r"that number|you just felt|conviction|felt result", low) else 2 if has_try else 1 if re.search(r"imagine|story", low) else 0
    notes["E"] = f"try-this={has_try}"

    # T — Transferable: a named, diagrammed model?
    has_named_model = bool(re.search(r"\bloop\b|\bmodel\b|call it the|the \w+ \w+:|framework", low))
    has_diagram = ">" in text and bool(re.search(r"→|->|deploy.*learn.*build|one .* many", low))
    T = 3 if has_named_model and has_diagram else 2 if has_named_model else 1
    notes["T"] = f"named-model={has_named_model}, diagram/quote={has_diagram}"

    # U — Understandable: concrete-first, low unanchored jargon. Heuristic: jargon density.
    jargon = len(re.findall(r"\b(leverage|paradigm|synerg|orchestrat|substrate|isomorph|epistemic)\w*", low))
    words = max(len(low.split()), 1)
    density = jargon / words
    has_concrete_open = bool(re.search(r"imagine|picture|story|a (great|bad)|you can('?t| not)", low[:600]))
    U = 3 if density < 0.003 and has_concrete_open else 2 if density < 0.006 else 1
    notes["U"] = f"jargon-density={density:.4f}, concrete-open={has_concrete_open}"

    return {"T": T, "R": R, "U": U, "E": E}, notes


def parse_scores(arg: str) -> dict[str, int]:
    """Parse 'T=2,R=3,...' manual score overrides."""
    out: dict[str, int] = {}
    for part in arg.split(","):
        k, _, v = part.partition("=")
        out[k.strip().upper()] = int(v)
    return out


def main() -> int:
    """CLI entry point: score a draft and apply the ship gate."""
    ap = argparse.ArgumentParser()
    ap.add_argument("draft", nargs="?", help="path to a draft Field Manual (.md)")
    ap.add_argument("--scores", help="explicit per-letter scores, e.g. T=3,R=3,U=2,E=2")
    args = ap.parse_args()

    if args.scores:
        scores = parse_scores(args.scores)
        notes = {}
    elif args.draft:
        if not os.path.isfile(args.draft):
            print(f"error: no such draft: {args.draft}", file=sys.stderr)
            return 2
        with open(args.draft, encoding="utf-8") as fh:
            scores, notes = heuristic_scores(fh.read())
    else:
        ap.error("provide a draft path or --scores")

    passed, reasons = gate(scores)
    print("TRUE score (" + ("heuristic baseline — agent refines" if not args.scores else "explicit") + "):")
    for ltr in LETTERS:
        n = f"  ({notes[ltr]})" if ltr in notes else ""
        print(f"  {ltr} = {scores.get(ltr, '?')}{n}")
    total = sum(scores.get(ltr, 0) for ltr in LETTERS)
    print(f"  total = {total} / 12")
    if passed:
        print("VERDICT: PASS — clears the ship gate (>=10 and every letter >=2).")
        return 0
    print("VERDICT: BLOCK — " + "; ".join(reasons))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
