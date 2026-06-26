"""Tests for eval-loop. Run:
  python3 -m unittest discover -s skills/eval-loop/tests -p 'test_*.py'

The tested core is the keep/revert decision + run-log rendering (scoring is pluggable).
"""
import importlib.util
import os
import tempfile
import unittest

_HERE = os.path.dirname(__file__)
_SCRIPT = os.path.join(_HERE, "..", "scripts", "eval_loop.py")
_spec = importlib.util.spec_from_file_location("eval_loop", _SCRIPT)
el = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(el)


class TestDecide(unittest.TestCase):
    def test_all_improving_accept(self):
        rounds = [{"label": "seed", "score": 0.41}, {"label": "r1", "score": 0.68},
                  {"label": "r2", "score": 0.90}]
        res = el.decide(rounds)
        verdicts = [d["verdict"] for d in res["decisions"]]
        self.assertEqual(verdicts, ["baseline", "accept", "accept"])
        self.assertEqual(res["winner_label"], "r2")
        self.assertEqual(res["winner_score"], 0.90)

    def test_regression_reverts_and_keeps_best(self):
        # reproduces the article: 0.41 -> 0.90 -> 0.82 (revert back to 0.90)
        rounds = [{"label": "seed", "score": 0.41}, {"label": "r1", "score": 0.90},
                  {"label": "r2-wordcap", "score": 0.82}]
        res = el.decide(rounds)
        self.assertEqual([d["verdict"] for d in res["decisions"]], ["baseline", "accept", "revert"])
        self.assertEqual(res["winner_label"], "r1")
        self.assertEqual(res["winner_score"], 0.90)

    def test_tie_reverts(self):
        rounds = [{"label": "a", "score": 0.8}, {"label": "b", "score": 0.8}]
        res = el.decide(rounds)
        self.assertEqual(res["decisions"][1]["verdict"], "revert")  # strict-improvement rule
        self.assertEqual(res["winner_label"], "a")

    def test_best_gain_is_largest_accepted(self):
        rounds = [{"label": "seed", "score": 0.41}, {"label": "num", "score": 0.68},
                  {"label": "ex", "score": 0.90}]
        res = el.decide(rounds)
        # gains: num +0.27, ex +0.22 -> largest is num
        self.assertEqual(res["best_gain"][0], "num")
        self.assertAlmostEqual(res["best_gain"][1], 0.27)


class TestRenderRunLog(unittest.TestCase):
    def test_table_shape_and_marks(self):
        rounds = [{"label": "seed", "change": "baseline", "score": 0.41},
                  {"label": "r1", "change": "add number", "score": 0.90},
                  {"label": "r2", "change": "word cap", "score": 0.82}]
        log = el.render_run_log(el.decide(rounds))
        self.assertIn("| Round | Change | Score | Verdict |", log)
        self.assertIn("accept ✅", log)
        self.assertIn("revert ❌", log)
        self.assertIn("What the loop learned", log)
        # 4 header/sep + 3 data rows present
        self.assertEqual(log.count("| 0 |") + log.count("| 1 |") + log.count("| 2 |"), 3)

    def test_determinism(self):
        rounds = [{"label": "a", "score": 0.4}, {"label": "b", "score": 0.9}]
        self.assertEqual(el.render_run_log(el.decide(rounds)),
                         el.render_run_log(el.decide(rounds)))


class TestScoreEachIntegration(unittest.TestCase):
    def _w(self, path, text):
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(text)

    def test_score_each_with_a_stub_scorer(self):
        # a fake scorer: echoes a score based on filename, so we test the wiring deterministically
        with tempfile.TemporaryDirectory() as d:
            v1 = os.path.join(d, "v1.txt"); self._w(v1, "x")
            v2 = os.path.join(d, "v2.txt"); self._w(v2, "y")
            scorer = os.path.join(d, "scorer.sh")
            # prints "score: 0.5" for v1, "score: 0.9" for v2
            self._w(scorer, '#!/bin/sh\ncase "$1" in *v1*) echo "score: 0.5";; *) echo "score: 0.9";; esac\n')
            os.chmod(scorer, 0o755)
            rounds = []
            for p in (v1, v2):
                rounds.append({"label": p, "change": p, "score": el._score_file(f"sh {scorer} {{file}}", p)})
            res = el.decide(rounds)
            self.assertEqual(res["decisions"][0]["verdict"], "baseline")
            self.assertEqual(res["decisions"][1]["verdict"], "accept")  # 0.9 > 0.5
            self.assertEqual(res["winner_score"], 0.9)

    def test_score_parse_percent(self):
        with tempfile.TemporaryDirectory() as d:
            f = os.path.join(d, "a.txt"); self._w(f, "x")
            scorer = os.path.join(d, "s.sh")
            self._w(scorer, '#!/bin/sh\necho "VERDICT score 90%"\n')
            os.chmod(scorer, 0o755)
            self.assertAlmostEqual(el._score_file(f"sh {scorer} {{file}}", f), 0.90)


if __name__ == "__main__":
    unittest.main()
