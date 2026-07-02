import json
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import trust_ledger as tl  # noqa: E402


def _ledger(tech="artifact", rel="artifact", learn="artifact", rep="vouch", rep_n=1):
    return {
        "dimensions": {
            "technical_competence": [{"claim": "x", "evidence": tech}],
            "reliability": [{"claim": "x", "evidence": rel}],
            "learning_agility": [{"claim": "x", "evidence": learn}],
            "validated_reputation": [{"claim": "x", "evidence": rep}] * rep_n,
        }
    }


class TestGate(unittest.TestCase):
    def test_full_evidence_passes(self):
        r = tl.evaluate(_ledger())
        self.assertTrue(r["go"])
        self.assertEqual(r["blockers"], [])

    def test_reputation_without_vouch_blocks(self):
        # A verifiable artifact is NOT a person who vouches.
        r = tl.evaluate(_ledger(rep="artifact"))
        self.assertFalse(r["go"])
        self.assertTrue(any("validated_reputation" in b for b in r["blockers"]))

    def test_one_weak_axis_blocks_despite_others(self):
        # true-scorer's AND-gate discipline: strong elsewhere does not rescue.
        r = tl.evaluate(_ledger(tech="claimed"))
        self.assertFalse(r["go"])
        self.assertTrue(any("technical_competence" in b for b in r["blockers"]))

    def test_claimed_only_never_passes(self):
        r = tl.evaluate(_ledger(tech="claimed", rel="claimed", learn="claimed", rep="claimed"))
        self.assertFalse(r["go"])
        # every axis under floor + reputation missing vouch
        self.assertGreaterEqual(len(r["blockers"]), 4)

    def test_pattern_flag_requires_two_vouches(self):
        one = tl.evaluate(_ledger(rep_n=1))["results"]["validated_reputation"]
        two = tl.evaluate(_ledger(rep_n=2))["results"]["validated_reputation"]
        self.assertFalse(one.pattern)
        self.assertTrue(two.pattern)

    def test_missing_dimension_is_zero_and_blocks(self):
        r = tl.evaluate({"dimensions": {"technical_competence": [{"claim": "x", "evidence": "vouch"}]}})
        self.assertFalse(r["go"])

    def test_unknown_tier_is_hard_error(self):
        with self.assertRaises(ValueError):
            tl.evaluate(_ledger(tech="excellent"))

    def test_unknown_dimension_is_hard_error(self):
        with self.assertRaises(ValueError):
            tl.evaluate({"dimensions": {"vibes": [{"claim": "x", "evidence": "vouch"}]}})

    def test_dimension_tier_is_strongest_evidence(self):
        led = {"dimensions": {
            "technical_competence": [
                {"claim": "a", "evidence": "claimed"},
                {"claim": "b", "evidence": "artifact"},
            ],
            "reliability": [{"claim": "x", "evidence": "artifact"}],
            "learning_agility": [{"claim": "x", "evidence": "artifact"}],
            "validated_reputation": [{"claim": "x", "evidence": "vouch"}],
        }}
        r = tl.evaluate(led)
        self.assertEqual(r["results"]["technical_competence"].tier, tl.TIERS["artifact"])
        self.assertTrue(r["go"])

    def test_example_ledger_passes(self):
        path = os.path.join(os.path.dirname(__file__), "..", "ledger.example.json")
        with open(path, encoding="utf-8") as f:
            r = tl.evaluate(json.load(f))
        self.assertTrue(r["go"], msg=str(r["blockers"]))


if __name__ == "__main__":
    unittest.main()
