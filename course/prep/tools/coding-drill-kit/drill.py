#!/usr/bin/env python3
"""coding-drill-kit — eval-as-gate, pointed at a human.

The Google FDE coding room is hand-written Python with zero assist (syntax highlighting
only). The failure mode is fumbling idioms you *recognize* but can't *produce*. So this
kit applies the FDE-os discipline (score → gate → track) to the person:

  1. `start`  — creates a blank attempt file listing only the required signatures.
     You write the templates FROM MEMORY, in a bare editor, no AI, no autocomplete.
  2. `check`  — runs real unit cases against what you wrote; per-template PASS/FAIL
     with the failing case named. A syntax error is reported, not excused.
  3. Every check appends a row to problems.md — the tracker IS the eval-loop run-log
     (Round │ Template │ Score │ What broke).

The six templates cover the recruiter's four buckets (strings, graphs, SRE,
distributed-systems-flavored): bfs · topo_sort · longest_unique · union-find ·
LRUCache · RateLimiter. Gate: interview-ready = 6/6 from a blank page, twice, on
different days.
"""
from __future__ import annotations

import argparse
import datetime
import importlib.util
import sys
import traceback
from pathlib import Path

KIT_DIR = Path(__file__).resolve().parent
ATTEMPTS = KIT_DIR / "attempts"
TRACKER = KIT_DIR / "problems.md"

HEADER = '''"""Blank-page attempt — write all six templates FROM MEMORY. No AI, no autocomplete,
no peeking at the case study. Dry-run by hand before you run `check`.

Required (exact names/signatures):

  def bfs(grid, start) -> set                 # visited cells, 4-directional
  def topo_sort(num_nodes, edges) -> list     # Kahn; [] on cycle
  def longest_unique(s) -> int                # sliding window
  def find(parent, x) -> int                  # union-find w/ path compression
  def union(parent, a, b) -> None
  class LRUCache: __init__(capacity), get(key), put(key, value)
  class RateLimiter: __init__(rate, per), allow(key, now=None)   # token bucket

When done:  python3 drill.py check attempts/<this file>
"""
'''


def _fail(msg: str) -> tuple[bool, str]:
    """A failing case result."""
    return (False, msg)


def _ok() -> tuple[bool, str]:
    """A passing case result."""
    return (True, "")


def _check_bfs(mod) -> tuple[bool, str]:
    """bfs visits every reachable cell of an open grid exactly once."""
    grid = [[0, 0, 0], [0, 0, 0]]
    visited = mod.bfs(grid, (0, 0))
    want = {(r, c) for r in range(2) for c in range(3)}
    return _ok() if set(visited) == want else _fail(f"open 2x3 grid from (0,0): got {sorted(visited)}")


def _check_topo(mod) -> tuple[bool, str]:
    """topo_sort orders a chain and returns [] on a cycle."""
    if mod.topo_sort(4, [(0, 1), (1, 2), (2, 3)]) != [0, 1, 2, 3]:
        return _fail("chain 0->1->2->3 not ordered [0,1,2,3]")
    if mod.topo_sort(2, [(0, 1), (1, 0)]) != []:
        return _fail("cycle 0<->1 must return []")
    # partial progress + a cycle: the lazy `return order` bug returns [0] here, not []
    if mod.topo_sort(3, [(0, 1), (1, 2), (2, 1)]) != []:
        return _fail("0->(1<->2 cycle) must return [], not the partial order")
    return _ok()


def _check_sliding(mod) -> tuple[bool, str]:
    """longest_unique on the classic cases incl. empty string."""
    for s, want in (("abcabcbb", 3), ("bbbb", 1), ("", 0), ("pwwkew", 3)):
        got = mod.longest_unique(s)
        if got != want:
            return _fail(f"longest_unique({s!r}) = {got}, want {want}")
    return _ok()


def _check_union_find(mod) -> tuple[bool, str]:
    """union/find connect components and keep strangers apart."""
    parent = list(range(5))
    mod.union(parent, 0, 1)
    mod.union(parent, 1, 2)
    if mod.find(parent, 0) != mod.find(parent, 2):
        return _fail("after union(0,1),union(1,2): find(0) != find(2)")
    if mod.find(parent, 3) == mod.find(parent, 0):
        return _fail("3 was never unioned with 0 but shares a root")
    return _ok()


def _check_lru(mod) -> tuple[bool, str]:
    """LRUCache evicts least-recently-used at capacity."""
    c = mod.LRUCache(2)
    c.put(1, 1)
    c.put(2, 2)
    if c.get(1) != 1:
        return _fail("get(1) after put should be 1")
    c.put(3, 3)  # evicts 2 (1 was just used)
    if c.get(2) != -1:
        return _fail("2 should have been evicted (1 was more recently used)")
    if c.get(3) != 3:
        return _fail("get(3) should be 3")
    return _ok()


def _check_rate(mod) -> tuple[bool, str]:
    """RateLimiter allows `rate` per window then refills over time (injectable now)."""
    rl = mod.RateLimiter(2, 1)
    if not (rl.allow("u", now=0.0) and rl.allow("u", now=0.0)):
        return _fail("first 2 requests at t=0 must be allowed (rate=2)")
    if rl.allow("u", now=0.0):
        return _fail("3rd request at t=0 must be rejected")
    if not rl.allow("u", now=1.0):
        return _fail("after 1s (full window) a request must be allowed again")
    return _ok()


TEMPLATES = {
    "bfs": _check_bfs,
    "topo_sort": _check_topo,
    "longest_unique": _check_sliding,
    "union_find": _check_union_find,
    "LRUCache": _check_lru,
    "RateLimiter": _check_rate,
}

_REQUIRED_NAMES = {"bfs": "bfs", "topo_sort": "topo_sort", "longest_unique": "longest_unique",
                   "union_find": "find", "LRUCache": "LRUCache", "RateLimiter": "RateLimiter"}


def start() -> int:
    """Create a fresh blank-page attempt file and print its path."""
    ATTEMPTS.mkdir(exist_ok=True)
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M")
    path = ATTEMPTS / f"attempt-{stamp}.py"
    path.write_text(HEADER, encoding="utf-8")
    print(f"Blank page ready: {path}")
    print("Open it in a BARE editor (autocomplete off). Write all six from memory. Then:")
    print(f"  python3 {Path(__file__).name} check {path.relative_to(KIT_DIR)}")
    return 0


def check(attempt: str) -> int:
    """Run every template's cases against the attempt; log to the tracker; exit 1 unless 6/6."""
    path = Path(attempt) if Path(attempt).is_absolute() else KIT_DIR / attempt
    spec = importlib.util.spec_from_file_location("attempt", path)
    mod = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)
    except Exception:
        print("✗ file does not import — in the real room this is a lost round:")
        print("  " + traceback.format_exc(limit=1).strip().splitlines()[-1])
        _log(path.name, {t: "import-error" for t in TEMPLATES})
        return 1

    results: dict[str, str] = {}
    for name, checker in TEMPLATES.items():
        if not hasattr(mod, _REQUIRED_NAMES[name]):
            results[name] = "not attempted"
            continue
        try:
            passed, why = checker(mod)
            results[name] = "PASS" if passed else f"FAIL — {why}"
        except Exception as exc:  # a crash is a fail with the reason named
            results[name] = f"FAIL — raised {type(exc).__name__}: {exc}"

    n_pass = sum(1 for v in results.values() if v == "PASS")
    for name, verdict in results.items():
        print(f"  {'✓' if verdict == 'PASS' else '✗'} {name}: {verdict}")
    print(f"\nscore: {n_pass}/{len(TEMPLATES)}")
    print("VERDICT: " + ("GO — do it again tomorrow from a blank page" if n_pass == len(TEMPLATES)
                         else "NO-GO — re-drill the failures above, then re-check"))
    _log(path.name, results)
    return 0 if n_pass == len(TEMPLATES) else 1


def _log(attempt_name: str, results: dict[str, str]) -> None:
    """Append one tracker row per check — the eval-loop run-log for a human."""
    if not TRACKER.exists():
        TRACKER.write_text(
            "# Drill tracker — the run-log\n\n"
            "| When | Attempt | Score | What broke |\n|---|---|---|---|\n",
            encoding="utf-8")
    n_pass = sum(1 for v in results.values() if v == "PASS")
    broke = "; ".join(f"{k}: {v}" for k, v in results.items() if v != "PASS") or "—"
    when = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    with TRACKER.open("a", encoding="utf-8") as fh:
        fh.write(f"| {when} | {attempt_name} | {n_pass}/{len(TEMPLATES)} | {broke} |\n")


def main(argv: list[str] | None = None) -> int:
    """CLI entry point: start | check <attempt.py>."""
    ap = argparse.ArgumentParser(prog="drill", description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("start", help="create a blank-page attempt file")
    p_check = sub.add_parser("check", help="score an attempt against real unit cases")
    p_check.add_argument("attempt")
    ns = ap.parse_args(argv)
    return start() if ns.cmd == "start" else check(ns.attempt)


if __name__ == "__main__":
    sys.exit(main())
