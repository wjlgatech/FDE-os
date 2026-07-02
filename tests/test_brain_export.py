"""Drift gate: the committed toolkit-brain.json must equal a fresh export from the skill sources."""
import importlib.util
import json
import unittest
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("export_brain", _ROOT / "scripts" / "export_brain.py")
eb = importlib.util.module_from_spec(spec)
spec.loader.exec_module(eb)


class TestBrainExport(unittest.TestCase):
    def test_committed_brain_matches_sources(self):
        committed = json.loads((_ROOT / "assets" / "toolkit-brain.json").read_text(encoding="utf-8"))
        fresh = json.loads(json.dumps(eb.build_brain(), sort_keys=True))
        self.assertEqual(committed, fresh,
                         "assets/toolkit-brain.json is stale — run scripts/export_brain.py")

    def test_brain_has_the_three_cores(self):
        brain = eb.build_brain()
        self.assertEqual(brain["true"]["ship_total"], 10)
        self.assertIn("agentic_design", brain["jd"]["clusters"])
        self.assertIn("web_stack", brain["jd"]["tools"])          # the adopted Maven categories ride along
        names = {a["name"] for a in brain["mapper"]["archetypes"]}
        self.assertIn("regulated-signoff", names)
        self.assertEqual(sum(1 for d in brain["mapper"]["dimensions"].values() if d["load_bearing"]), 4)


if __name__ == "__main__":
    unittest.main()
