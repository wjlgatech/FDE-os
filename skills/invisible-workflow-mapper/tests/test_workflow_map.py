import json
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import workflow_map as wm  # noqa: E402

EX = os.path.join(os.path.dirname(__file__), "..", "examples", "claims-triage-signals.json")


def _load_example():
    with open(EX, encoding="utf-8") as fh:
        return json.load(fh)


class TestCoverage(unittest.TestCase):
    def test_unknown_dimension_is_an_error_not_a_silent_pass(self):
        with self.assertRaises(ValueError):
            wm.coverage({"signals": [{"dimension": "vibes", "observation": "x", "confidence": 0.9}]})

    def test_status_thresholds(self):
        self.assertEqual(wm._status(0.9), "known")
        self.assertEqual(wm._status(0.5), "partial")
        self.assertEqual(wm._status(0.1), "unknown")

    def test_best_confidence_wins_per_dimension(self):
        data = {"signals": [
            {"dimension": "decider", "observation": "a", "confidence": 0.3},
            {"dimension": "decider", "observation": "b", "confidence": 0.8},
        ]}
        cov = wm.coverage(data)
        self.assertEqual(cov["decider"]["confidence"], 0.8)
        self.assertEqual(cov["decider"]["status"], "known")

    def test_confidence_is_clamped(self):
        cov = wm.coverage({"signals": [{"dimension": "trigger", "observation": "x", "confidence": 5}]})
        self.assertEqual(cov["trigger"]["confidence"], 1.0)


class TestReadinessAndGate(unittest.TestCase):
    def test_load_bearing_unknown_blocks_even_if_others_strong(self):
        # everything known except a load-bearing dimension -> gate blocks
        data = {"signals": [
            {"dimension": "trigger", "observation": "x", "confidence": 1.0},
            {"dimension": "decider", "observation": "x", "confidence": 1.0},
            {"dimension": "approval_chain", "observation": "x", "confidence": 1.0},
            {"dimension": "evidence_ritual", "observation": "x", "confidence": 1.0},
            # adoption_owner missing entirely -> unknown, load-bearing
        ]}
        rep = wm.build_map(data, threshold=0.5)
        self.assertFalse(rep["gate"]["passed"])
        self.assertTrue(any("Adoption owner" in r for r in rep["gate"]["reasons"]))

    def test_full_load_bearing_coverage_passes(self):
        data = {"signals": [
            {"dimension": d, "observation": "x", "confidence": 0.9}
            for d, m in wm.DIMENSIONS.items() if m["load_bearing"]
        ]}
        rep = wm.build_map(data, threshold=0.6)
        self.assertTrue(rep["gate"]["passed"])
        self.assertGreaterEqual(rep["adoption_readiness"], 0.6)

    def test_readiness_only_counts_load_bearing(self):
        # a non-load-bearing signal alone should leave readiness at 0
        rep = wm.build_map({"signals": [{"dimension": "cadence", "observation": "x", "confidence": 1.0}]})
        self.assertEqual(rep["adoption_readiness"], 0.0)
        self.assertGreater(rep["map_completeness"], 0.0)


class TestArchetypes(unittest.TestCase):
    def test_regulated_and_shadow_inferred_from_example(self):
        rep = wm.build_map(_load_example())
        names = [a["name"] for a in rep["archetypes"]]
        self.assertIn("regulated-signoff", names)   # compliance/audit/legal tells
        self.assertIn("shadow-bottom-up", names)     # spreadsheet/side-channel tells

    def test_archetypes_sorted_by_signal_strength(self):
        rep = wm.build_map(_load_example())
        scores = [a["score"] for a in rep["archetypes"]]
        self.assertEqual(scores, sorted(scores, reverse=True))

    def test_no_tells_no_archetype(self):
        rep = wm.build_map({"signals": [{"dimension": "trigger", "observation": "a thing happens", "confidence": 0.5}]})
        self.assertEqual(rep["archetypes"], [])


class TestProbes(unittest.TestCase):
    def test_gaps_get_probes_known_dims_do_not(self):
        rep = wm.build_map(_load_example())
        # decider is weak (0.2) -> must be probed
        self.assertIn("decider", rep["probes"])
        # incumbent is strong (0.8) -> no probe
        self.assertNotIn("incumbent", rep["probes"])
        # every probed dimension yields at least one question
        self.assertTrue(all(len(qs) >= 1 for qs in rep["probes"].values()))


class TestRender(unittest.TestCase):
    def test_markdown_has_core_sections(self):
        rep = wm.build_map(_load_example())
        md = wm.render_md(rep, _load_example().get("context"))
        self.assertIn("# Invisible Workflow Map", md)
        self.assertIn("The decision workflow", md)
        self.assertIn("Probe next", md)
        self.assertIn("Adoption-readiness", md)


if __name__ == "__main__":
    unittest.main()
