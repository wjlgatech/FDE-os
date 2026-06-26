"""Tests for criteria-scorer. Run:
  python3 -m unittest discover -s skills/criteria-scorer/tests -p 'test_*.py'
"""
import importlib.util
import os
import unittest

_HERE = os.path.dirname(__file__)
_SCRIPT = os.path.join(_HERE, "..", "scripts", "criteria_score.py")
_spec = importlib.util.spec_from_file_location("criteria_score", _SCRIPT)
cs = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cs)


class TestCriteria(unittest.TestCase):
    def test_all_pass_scores_one(self):
        text = "We cut latency by 40%. See [the report](https://x.com/r)."
        criteria = [
            {"question": "has a number?", "type": "must_contain_number"},
            {"question": "cites a source?", "type": "must_cite"},
            {"question": "under 50 words?", "type": "max_words", "value": 50},
        ]
        rep = cs.score_artifact(text, criteria)
        self.assertEqual(rep["score"], 1.0)

    def test_must_contain_number(self):
        self.assertTrue(cs.evaluate_criterion("grew 27%", {"type": "must_contain_number"}))
        self.assertFalse(cs.evaluate_criterion("grew a lot", {"type": "must_contain_number"}))

    def test_max_words_fail_with_reason(self):
        text = "word " * 200
        criteria = [{"question": "under 150 words?", "type": "max_words", "value": 150}]
        rep = cs.score_artifact(text, criteria)
        self.assertEqual(rep["score"], 0.0)
        passed, reasons = cs.gate(rep["score"], 0.8, rep["results"])
        self.assertFalse(passed)
        self.assertTrue(any("under 150 words" in r for r in reasons))

    def test_min_words(self):
        self.assertTrue(cs.evaluate_criterion("a b c d", {"type": "min_words", "value": 3}))
        self.assertFalse(cs.evaluate_criterion("a b", {"type": "min_words", "value": 3}))

    def test_must_not_match_buzzwords(self):
        crit = {"type": "must_not_match", "value": ["synergy", "leverage", "paradigm"]}
        self.assertTrue(cs.evaluate_criterion("a clear plain sentence", crit))
        self.assertFalse(cs.evaluate_criterion("we leverage synergy", crit))

    def test_must_match(self):
        crit = {"type": "must_match", "value": r"\bbefore\b.*\bafter\b"}
        self.assertTrue(cs.evaluate_criterion("before X and after Y", crit))
        self.assertFalse(cs.evaluate_criterion("no framing here", crit))

    def test_must_cite(self):
        self.assertTrue(cs.evaluate_criterion("see https://example.com", {"type": "must_cite"}))
        self.assertTrue(cs.evaluate_criterion("per [doc 1]", {"type": "must_cite"}))
        self.assertFalse(cs.evaluate_criterion("no citation at all", {"type": "must_cite"}))

    def test_unknown_type_raises(self):
        with self.assertRaises(cs.CriterionError):
            cs.evaluate_criterion("x", {"type": "vibes"})

    def test_gate_threshold(self):
        passed, _ = cs.gate(0.8, 0.8)
        self.assertTrue(passed)  # >= is a pass
        passed, reasons = cs.gate(0.5, 0.8)
        self.assertFalse(passed)

    def test_determinism(self):
        text = "grew 40%, see [r](https://x.com)"
        crit = [{"type": "must_contain_number", "question": "n"}, {"type": "must_cite", "question": "c"}]
        self.assertEqual(cs.score_artifact(text, crit), cs.score_artifact(text, crit))

    def test_example_criteria_file_scores(self):
        ex = os.path.join(_HERE, "..", "examples", "launch-announcement-criteria.json")
        import json
        with open(ex, encoding="utf-8") as fh:
            criteria = json.load(fh)
        # an artifact crafted to pass all the example criteria
        good = ("We shipped the new export. Before, exports took 9 minutes; after, 12 seconds. "
                "Try it in Settings. Full notes: [changelog](https://example.com/log).")
        rep = cs.score_artifact(good, criteria)
        self.assertGreaterEqual(rep["score"], 0.8)


if __name__ == "__main__":
    unittest.main()
