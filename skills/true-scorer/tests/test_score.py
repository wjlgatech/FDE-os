"""Tests for TRUE-scorer. The gate (threshold) is the load-bearing core — tested exhaustively.

Run: python3 -m unittest discover -s skills/true-scorer/tests -p 'test_*.py'
"""
import importlib.util
import os
import unittest

_HERE = os.path.dirname(__file__)
_SCRIPT = os.path.join(_HERE, "..", "scripts", "score.py")
_REPO = os.path.abspath(os.path.join(_HERE, "..", "..", ".."))
_spec = importlib.util.spec_from_file_location("score", _SCRIPT)
sc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(sc)


class TestGate(unittest.TestCase):
    def test_perfect_passes(self):
        passed, reasons = sc.gate({"T": 3, "R": 3, "U": 3, "E": 3})
        self.assertTrue(passed)
        self.assertEqual(reasons, [])

    def test_total_10_with_a_letter_below_2_blocks(self):
        # total = 10 but E=1 -> the AND condition must block (not just the sum)
        passed, reasons = sc.gate({"T": 3, "R": 3, "U": 3, "E": 1})
        self.assertFalse(passed)
        self.assertTrue(any("E=1" in r for r in reasons))

    def test_total_10_with_min_2_passes_boundary(self):
        passed, reasons = sc.gate({"T": 2, "R": 3, "U": 3, "E": 2})
        self.assertTrue(passed)

    def test_below_total_blocks(self):
        passed, reasons = sc.gate({"T": 2, "R": 2, "U": 2, "E": 3})  # total 9
        self.assertFalse(passed)
        self.assertTrue(any("total 9" in r for r in reasons))

    def test_missing_letter_blocks(self):
        passed, reasons = sc.gate({"T": 3, "R": 3, "U": 3})
        self.assertFalse(passed)
        self.assertTrue(any("missing score for E" in r for r in reasons))


class TestHeuristicOnPost1(unittest.TestCase):
    """Post #1 is the known 12/12 reference; the heuristic baseline should not block it."""

    def setUp(self):
        self.draft = os.path.join(_REPO, "Delta-01-field-manual.md")

    def test_post1_field_manual_clears_gate_on_heuristics(self):
        with open(self.draft, encoding="utf-8") as fh:
            scores, _ = sc.heuristic_scores(fh.read())
        passed, reasons = sc.gate(scores)
        self.assertTrue(passed, f"Post #1 should clear the gate; got {scores}, reasons={reasons}")

    def test_post1_has_reusable_and_experienceable_signals(self):
        with open(self.draft, encoding="utf-8") as fh:
            scores, _ = sc.heuristic_scores(fh.read())
        # Post #1 links a Field Kit (R) and has the "10-minute version" try-this (E)
        self.assertGreaterEqual(scores["R"], 2)
        self.assertGreaterEqual(scores["E"], 2)


class TestHeuristicBlocksDeficient(unittest.TestCase):
    def test_no_asset_no_tryit_blocks(self):
        text = "# A thought\nHere is an abstract idea with no model, no asset, no exercise. "
        scores, _ = sc.heuristic_scores(text)
        passed, _ = sc.gate(scores)
        self.assertFalse(passed)
        # R (no asset) and E (no try-this) should both be below the floor
        self.assertLess(scores["R"], 2)
        self.assertLess(scores["E"], 2)


if __name__ == "__main__":
    unittest.main()
