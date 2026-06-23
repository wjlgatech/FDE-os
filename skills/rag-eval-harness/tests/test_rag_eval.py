"""Tests for rag-eval-harness. Run:
  python3 -m unittest discover -s skills/rag-eval-harness/tests -p 'test_*.py'

Metrics are checked against hand-computed values; grounding is checked on a supported vs
hallucinated answer.
"""
import importlib.util
import os
import unittest

_HERE = os.path.dirname(__file__)
_SCRIPT = os.path.join(_HERE, "..", "scripts", "rag_eval.py")
_spec = importlib.util.spec_from_file_location("rag_eval", _SCRIPT)
re_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(re_mod)


def _item(retrieved, gold=None, answer="", citations=None):
    it = {"query": "q", "retrieved": retrieved}
    if gold is not None:
        it["gold_context_ids"] = gold
    if answer:
        it["answer"] = answer
    if citations is not None:
        it["citations"] = citations
    return it


class TestRetrievalMetrics(unittest.TestCase):
    def setUp(self):
        # ranks: c1(rel) c2(not) c3(rel) c4(not) ; gold = {c1, c3, c5}
        self.it = _item(
            [{"id": "c1", "relevant": True}, {"id": "c2", "relevant": False},
             {"id": "c3", "relevant": True}, {"id": "c4", "relevant": False}],
            gold=["c1", "c3", "c5"],
        )

    def test_precision_at_k(self):
        # top-4: 2 relevant of 4 -> 0.5 ; top-2: 1 of 2 -> 0.5
        self.assertEqual(re_mod.precision_at_k(self.it, 4), 0.5)
        self.assertEqual(re_mod.precision_at_k(self.it, 2), 0.5)

    def test_recall_at_k(self):
        # gold has 3; top-4 retrieved contains c1,c3 -> 2/3
        self.assertAlmostEqual(re_mod.recall_at_k(self.it, 4), 2 / 3)
        # top-1 contains only c1 -> 1/3
        self.assertAlmostEqual(re_mod.recall_at_k(self.it, 1), 1 / 3)

    def test_recall_none_without_gold(self):
        it = _item([{"id": "c1", "relevant": True}])
        self.assertIsNone(re_mod.recall_at_k(it, 5))

    def test_mrr_first_relevant_at_rank_1(self):
        self.assertEqual(re_mod.mrr(self.it), 1.0)

    def test_mrr_first_relevant_at_rank_2(self):
        it = _item([{"id": "x", "relevant": False}, {"id": "y", "relevant": True}])
        self.assertEqual(re_mod.mrr(it), 0.5)

    def test_hit_rate(self):
        self.assertEqual(re_mod.hit_rate_at_k(self.it, 1), 1.0)
        none_it = _item([{"id": "a", "relevant": False}, {"id": "b", "relevant": False}])
        self.assertEqual(re_mod.hit_rate_at_k(none_it, 5), 0.0)


class TestGrounding(unittest.TestCase):
    def test_supported_answer_scores_high(self):
        it = _item(
            [{"id": "c1", "text": "Metformin is a first-line treatment for type 2 diabetes."}],
            answer="Metformin is a first-line treatment for type 2 diabetes.",
        )
        self.assertEqual(re_mod.grounding_score(it), 1.0)

    def test_hallucinated_answer_scores_low(self):
        it = _item(
            [{"id": "c1", "text": "Metformin is a first-line treatment for type 2 diabetes."}],
            answer="Aspirin cures pancreatic cancer in seven days according to the study.",
        )
        # none of the answer's content tokens are in the context -> 0.0
        self.assertLess(re_mod.grounding_score(it), 0.5)

    def test_no_answer_is_fully_grounded(self):
        it = _item([{"id": "c1", "text": "anything"}], answer="")
        self.assertEqual(re_mod.grounding_score(it), 1.0)

    def test_mixed_answer_partial(self):
        it = _item(
            [{"id": "c1", "text": "The drug lowers blood glucose."}],
            answer="The drug lowers blood glucose. It also grants immortality to all users forever.",
        )
        g = re_mod.grounding_score(it)
        self.assertGreater(g, 0.0)
        self.assertLess(g, 1.0)  # one grounded, one not


class TestCitationCoverage(unittest.TestCase):
    def test_cited_but_not_retrieved_flagged(self):
        it = _item([{"id": "c1", "text": "x"}], citations=["c1", "c9"])
        self.assertEqual(re_mod.citation_coverage(it), 0.5)  # c9 not retrieved

    def test_none_without_citations(self):
        self.assertIsNone(re_mod.citation_coverage(_item([{"id": "c1"}])))


class TestAggregateAndGate(unittest.TestCase):
    def test_evaluate_empty(self):
        self.assertEqual(re_mod.evaluate([]), {"n": 0, "metrics": {}})

    def test_gate_blocks_below_floor(self):
        metrics = {"recall@k": 0.4, "grounding": 0.9}
        passed, reasons = re_mod.gate(metrics, {"recall@k": 0.7, "grounding": 0.8})
        self.assertFalse(passed)
        self.assertTrue(any("recall@k=0.4" in r for r in reasons))

    def test_gate_passes_when_met(self):
        metrics = {"recall@k": 0.8, "grounding": 0.9}
        passed, reasons = re_mod.gate(metrics, {"recall@k": 0.7, "grounding": 0.8})
        self.assertTrue(passed)

    def test_gate_unmeasured_metric_does_not_hard_fail(self):
        # recall is None (no labels) -> note it, but don't hard-fail the gate
        passed, reasons = re_mod.gate({"recall@k": None, "grounding": 0.9},
                                      {"recall@k": 0.7, "grounding": 0.8})
        self.assertTrue(passed)
        self.assertTrue(any("not measured" in r for r in reasons))

    def test_determinism(self):
        data = [_item([{"id": "c1", "relevant": True}], gold=["c1"], answer="c1 text here")]
        self.assertEqual(re_mod.evaluate(data), re_mod.evaluate(data))


if __name__ == "__main__":
    unittest.main()
