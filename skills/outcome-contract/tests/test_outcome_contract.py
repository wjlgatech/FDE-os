"""outcome-contract tests — the honesty rules are the spec. Stdlib unittest (CI runs no pytest)."""
import contextlib
import io
import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
from outcome_score import (  # noqa: E402
    ContractError, score_contract, score_outcome, main,
    PASS, FAIL, CLAIMED, NOT_MEASURED,
)


def outcome(**kw):
    base = {"id": "o1", "metric": "m", "target": 60, "direction": ">=", "blocking": True}
    base.update(kw)
    return base


def contract(*outcomes):
    return {"engagement": "acme-test", "outcomes": list(outcomes)}


class TestOutcomeRules(unittest.TestCase):
    def test_measured_meeting_target_passes(self):
        r = score_outcome(outcome(evidence={"kind": "measured", "value": 72.5, "source": "https://x/y.csv"}))
        self.assertEqual(r["status"], PASS)

    def test_measured_missing_target_fails(self):
        r = score_outcome(outcome(evidence={"kind": "measured", "value": 41, "source": "https://x"}))
        self.assertEqual(r["status"], FAIL)

    def test_direction_lte(self):
        r = score_outcome(outcome(target=5, direction="<=",
                                  evidence={"kind": "measured", "value": 3, "source": "https://x"}))
        self.assertEqual(r["status"], PASS)

    def test_claimed_never_passes_even_if_it_meets_target(self):
        r = score_outcome(outcome(evidence={"kind": "claimed", "value": 99}))
        self.assertEqual(r["status"], CLAIMED)

    def test_measured_without_source_downgrades_to_claimed(self):
        r = score_outcome(outcome(evidence={"kind": "measured", "value": 99}))
        self.assertEqual(r["status"], CLAIMED)
        self.assertIn("downgraded", r["detail"])

    def test_no_evidence_is_not_measured_never_fake_pass(self):
        self.assertEqual(score_outcome(outcome())["status"], NOT_MEASURED)

    def test_baseline_delta_reported(self):
        r = score_outcome(outcome(baseline=10,
                                  evidence={"kind": "measured", "value": 70, "source": "https://x"}))
        self.assertEqual(r["delta_vs_baseline"], 60)


class TestGateRules(unittest.TestCase):
    def test_go_requires_all_blocking_pass(self):
        rep = score_contract(contract(
            outcome(id="a", evidence={"kind": "measured", "value": 70, "source": "https://x"}),
            outcome(id="b", target=5, direction="<=",
                    evidence={"kind": "measured", "value": 2, "source": "https://x"}),
        ))
        self.assertEqual(rep["verdict"], "GO")

    def test_gate_cannot_pass_on_non_passing_blocking_outcome(self):
        cases = {
            "not measured": None,
            "claimed": {"kind": "claimed", "value": 99},
            "measured fail": {"kind": "measured", "value": 1, "source": "https://x"},
        }
        for label, bad_evidence in cases.items():
            with self.subTest(label):
                o = outcome(id="bad") if bad_evidence is None else outcome(id="bad", evidence=bad_evidence)
                rep = score_contract(contract(
                    outcome(id="good", evidence={"kind": "measured", "value": 70, "source": "https://x"}),
                    o,
                ))
                self.assertEqual(rep["verdict"], "NO-GO")

    def test_advisory_outcome_does_not_block(self):
        rep = score_contract(contract(
            outcome(id="good", evidence={"kind": "measured", "value": 70, "source": "https://x"}),
            outcome(id="fyi", blocking=False),
        ))
        self.assertEqual(rep["verdict"], "GO")
        self.assertEqual(rep["counts"][NOT_MEASURED], 1)


class TestMalformedContracts(unittest.TestCase):
    def test_malformed_contract_raises(self):
        bad_contracts = [
            {},                                            # no engagement
            {"engagement": "x"},                           # no outcomes
            {"engagement": "x", "outcomes": []},           # empty outcomes
            {"engagement": "x", "outcomes": [{"id": "a", "metric": "m", "target": 1, "direction": "up"}]},
            {"engagement": "x", "outcomes": [               # duplicate ids
                {"id": "a", "metric": "m", "target": 1, "direction": ">="},
                {"id": "a", "metric": "m", "target": 1, "direction": ">="}]},
        ]
        for i, bad in enumerate(bad_contracts):
            with self.subTest(i=i):
                with self.assertRaises(ContractError):
                    score_contract(bad)

    def test_all_advisory_contract_rejected(self):
        with self.assertRaises(ContractError):
            score_contract(contract(outcome(id="a", blocking=False)))


class TestCLI(unittest.TestCase):
    def _write(self, tmpdir, data):
        p = os.path.join(tmpdir, "c.json")
        with open(p, "w", encoding="utf-8") as f:
            json.dump(data, f)
        return p

    def _run(self, argv):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = main(argv)
        return code, out.getvalue(), err.getvalue()

    def test_cli_go_exits_zero(self):
        with tempfile.TemporaryDirectory() as d:
            p = self._write(d, contract(
                outcome(evidence={"kind": "measured", "value": 70, "source": "https://x"})))
            code, out, _ = self._run(["score", p])
        self.assertEqual(code, 0)
        self.assertIn("VERDICT: GO", out)

    def test_cli_nogo_exits_two(self):
        with tempfile.TemporaryDirectory() as d:
            p = self._write(d, contract(outcome()))
            code, out, _ = self._run(["score", p])
        self.assertEqual(code, 2)
        self.assertIn("NO-GO", out)

    def test_cli_malformed_exits_one(self):
        with tempfile.TemporaryDirectory() as d:
            p = self._write(d, {"engagement": "x"})
            code, _, err = self._run(["score", p])
        self.assertEqual(code, 1)
        self.assertIn("error:", err)


if __name__ == "__main__":
    unittest.main()
