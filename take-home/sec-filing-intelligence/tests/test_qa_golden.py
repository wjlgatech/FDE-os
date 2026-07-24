"""End-to-end gates: the golden QA eval and the cross-filing reconciliation
must pass on every commit — via the same CLI contract a human runs."""
import os
import subprocess
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SCRIPTS = os.path.join(ROOT, "scripts")


def run(script):
    return subprocess.run([sys.executable, os.path.join(SCRIPTS, script)],
                          capture_output=True, text=True, timeout=300)


class TestGoldenEval(unittest.TestCase):
    def test_golden_qa_eval_passes_all_gates(self):
        r = run("eval_sec.py")
        self.assertEqual(r.returncode, 0, r.stdout[-800:] + r.stderr[-300:])
        self.assertIn("VERDICT: PASS", r.stdout)
        self.assertIn('"answer_accuracy": 1.0', r.stdout)
        self.assertIn('"refusal_recall": 1.0', r.stdout)

    def test_cross_filing_reconciliation_holds(self):
        r = run("reconcile.py")
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn("additivity total_revenue: PASS", r.stdout)
        self.assertIn("additivity net_income: PASS", r.stdout)
        self.assertIn("NOT_MEASURED", r.stdout,
                      "the honest skip (YTD-only cash flow) must stay visible")


class TestRefusalShape(unittest.TestCase):
    def test_unfiled_period_refuses_with_the_reason(self):
        sys.path.insert(0, SCRIPTS)
        from qa import ask
        a = ask("What is Tesla's net income growth between 2025 and 2026?")
        self.assertEqual(a["type"], "refusal")
        self.assertTrue(any("FY2026" in r for r in a["reasons"]))
        self.assertTrue(any("latest annual" in r for r in a["reasons"]))


if __name__ == "__main__":
    unittest.main()
