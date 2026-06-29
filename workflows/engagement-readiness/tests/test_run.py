import json
import os
import sys
import unittest

HERE = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(HERE, ".."))
import run  # noqa: E402

EX = os.path.join(HERE, "..", "examples", "engagement.json")


def _example():
    with open(EX, encoding="utf-8") as fh:
        return json.load(fh)


class TestEngagementReadiness(unittest.TestCase):
    def test_example_is_go_when_both_stages_pass(self):
        rep = run.run_engagement(_example())
        self.assertTrue(rep["go"])
        self.assertEqual(rep["verdict"], "GO")
        self.assertEqual(set(rep["stages_assessed"]), {"adoption", "eval"})

    def test_no_go_if_adoption_blocks(self):
        b = _example()
        # strip the load-bearing signals so adoption can't pass
        b["workflow"]["signals"] = [s for s in b["workflow"]["signals"] if s["dimension"] == "trigger"]
        rep = run.run_engagement(b)
        self.assertFalse(rep["go"])
        self.assertTrue(any("adoption fit BLOCKED" in r for r in rep["reasons"]))

    def test_no_go_if_eval_missing(self):
        b = _example()
        b.pop("eval")
        rep = run.run_engagement(b)
        self.assertFalse(rep["go"])
        self.assertTrue(any("eval not assessed" in r for r in rep["reasons"]))

    def test_no_go_if_eval_fails_thresholds(self):
        b = _example()
        b["eval"]["thresholds"] = {"recall@k": 0.99, "precision@k": 0.99}  # impossible bar
        rep = run.run_engagement(b)
        self.assertFalse(rep["go"])
        self.assertFalse(rep["eval_pass"])

    def test_no_go_if_eval_has_no_threshold_bar(self):
        b = _example()
        b["eval"].pop("thresholds")  # ran but no pass/fail bar
        rep = run.run_engagement(b)
        self.assertFalse(rep["go"])
        self.assertIsNone(rep["eval_pass"])

    def test_render_has_verdict_and_both_stages(self):
        md = run.render_md(run.run_engagement(_example()))
        self.assertIn("Engagement Readiness", md)
        self.assertIn("will it get adopted", md)
        self.assertIn("does it work", md)


if __name__ == "__main__":
    unittest.main()
