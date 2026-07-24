"""The golden dataset is the permanent regression net: 47 labeled cases across
11 tag families (common, boundary, tier, pii, software, supersede, memory,
injection, invalid, bids, combo), run end-to-end through the CLI contract and
graded by the eval gate. Anything below the gates turns the build red.

This set already earned its keep on day one: it exposed an unimplemented
policy rule (v3 §3 competitive bids) and a crash on vendor-less invalid
requests — both fixed the same day it was written.
"""
import json
import os
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
GOLDEN_REQ = os.path.join(ROOT, "data", "golden", "golden-requests.jsonl")
GOLDEN_TRUTH = os.path.join(ROOT, "data", "golden", "golden-truth.json")


class TestGoldenDataset(unittest.TestCase):
    def test_golden_set_shape(self):
        with open(GOLDEN_REQ, encoding="utf-8") as f:
            ids = [json.loads(l)["id"] for l in f if l.strip()]
        with open(GOLDEN_TRUTH, encoding="utf-8") as f:
            truth = json.load(f)
        self.assertGreaterEqual(len(ids), 40)
        self.assertEqual(sorted(ids), sorted(truth))
        tags = {t for gt in truth.values() for t in gt.get("tags", [])}
        for family in ("common", "boundary", "tier", "pii", "memory",
                       "injection", "invalid", "bids", "combo", "supersede"):
            self.assertIn(family, tags, f"golden set lost its '{family}' coverage")

    def test_golden_run_passes_the_eval_gate(self):
        with tempfile.TemporaryDirectory() as out:
            run = subprocess.run(
                [sys.executable, os.path.join(ROOT, "scripts", "run.py"),
                 "--requests", GOLDEN_REQ, "--out", out],
                capture_output=True, text=True)
            self.assertEqual(run.returncode, 0, run.stderr[-500:])
            ev = subprocess.run(
                [sys.executable, os.path.join(ROOT, "scripts", "eval.py"),
                 "--run-dir", out, "--ground-truth", GOLDEN_TRUTH],
                capture_output=True, text=True)
            self.assertEqual(ev.returncode, 0, ev.stdout[-800:] + ev.stderr[-200:])
            self.assertIn("VERDICT: PASS", ev.stdout)
            self.assertIn("✓ bids", ev.stdout, "the once-missing rule stays covered")


if __name__ == "__main__":
    unittest.main()
