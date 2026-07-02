#!/usr/bin/env python3
"""export_brain — generate assets/toolkit-brain.json from the Python skill sources.

The browser playground (playground.html) runs three skill cores client-side. Its knowledge
(cluster tells, tool taxonomy, archetype tells/traps, dimension weights, TRUE gate constants)
is NOT hand-copied into JS — it is exported here from the same Python modules the tests gate,
so the web version cannot silently drift from the tested cores. `tests/test_brain_export.py`
fails if the committed JSON differs from a fresh export.

Run after changing any of the three skills' constants:
  python3 scripts/export_brain.py          # rewrites assets/toolkit-brain.json
"""
from __future__ import annotations

import importlib.util
import json
import os
import sys

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUT = os.path.join(_ROOT, "assets", "toolkit-brain.json")


def _load(rel: str, name: str):
    """Import a skill script by repo-relative path."""
    spec = importlib.util.spec_from_file_location(name, os.path.join(_ROOT, rel))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def build_brain() -> dict:
    """Assemble the playground brain from the three skill modules."""
    jc = _load("skills/jd-compiler/scripts/jd_compile.py", "jd_compile")
    wm = _load("skills/invisible-workflow-mapper/scripts/workflow_map.py", "workflow_map")
    ts = _load("skills/true-scorer/scripts/score.py", "score")
    return {
        "schema": "toolkit-brain/1",
        "jd": {"clusters": jc.CLUSTERS, "tools": jc.TOOLS},
        "mapper": {"dimensions": wm.DIMENSIONS, "probes": wm.PROBES, "archetypes": wm.ARCHETYPES},
        "true": {"letters": list(ts.LETTERS), "ship_total": ts.SHIP_TOTAL,
                 "ship_min_letter": ts.SHIP_MIN_LETTER},
    }


def main() -> int:
    """CLI entry point: write the brain JSON deterministically."""
    brain = build_brain()
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(brain, fh, indent=2, sort_keys=True, ensure_ascii=False)
        fh.write("\n")
    print(f"wrote {os.path.relpath(OUT, _ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
