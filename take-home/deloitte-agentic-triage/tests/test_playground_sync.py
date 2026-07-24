"""The playground's vendored agent must be byte-identical to the source modules.

Duplication is allowed ONLY with a gate proving sync: the brief's /api/triage
function runs a vendored copy of the agent (Vercel deploys the brief dir alone),
and this test turns any drift between source and copy into a red build.
Also smoke-runs the playground handler core against two known scenarios.
"""
import json
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
VENDORED = os.path.join(ROOT, "brief", "api", "_agent")

PAIRS = (
    [(os.path.join(ROOT, "scripts", f), os.path.join(VENDORED, f))
     for f in ("graph.py", "tools.py", "retrieval.py", "memory.py",
               "reasoner.py", "guardrails.py", "agent.py")]
    + [(os.path.join(ROOT, "corpus", f), os.path.join(VENDORED, "corpus", f))
       for f in sorted(os.listdir(os.path.join(ROOT, "corpus")))]
    + [(os.path.join(ROOT, "data", f), os.path.join(VENDORED, "data", f))
       for f in ("vendors.json", "software-catalog.json")]
)


class TestVendoredSync(unittest.TestCase):
    def test_every_vendored_file_is_byte_identical_to_source(self):
        for src, dst in PAIRS:
            with self.subTest(file=os.path.basename(src)):
                self.assertTrue(os.path.exists(dst), f"missing vendored copy: {dst}")
                with open(src, "rb") as a, open(dst, "rb") as b:
                    self.assertEqual(a.read(), b.read(),
                                     f"vendored copy drifted: {dst} — re-copy from source")


class TestPlaygroundHandler(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, os.path.join(ROOT, "brief", "api"))
        from triage import run_triage  # noqa: F401
        cls.run_triage = staticmethod(run_triage)

    def test_routine_approve(self):
        out = self.run_triage({"request": {
            "date": "2026-05-04", "role": "Manager", "vendor": "Maple Office Supply",
            "category": "furniture", "amount_usd": 4000, "description": "chairs"}})
        self.assertEqual(out["decision"], "approve")
        self.assertTrue(out["citations"])

    def test_split_purchase_via_priors(self):
        req = {"date": "2026-05-12", "role": "Manager", "vendor": "Maple Office Supply",
               "category": "furniture", "amount_usd": 7000, "description": "desks"}
        alone = self.run_triage({"request": req})
        with_prior = self.run_triage({"request": req, "priors": [
            {"vendor": "Maple Office Supply", "amount_usd": 4000, "date": "2026-05-04"}]})
        self.assertEqual(alone["decision"], "approve")
        self.assertEqual(with_prior["decision"], "escalate")
        self.assertEqual(with_prior["escalate_to"], "authority-chain")

    def test_result_is_json_serializable(self):
        out = self.run_triage({"request": {
            "date": "2026-05-05", "role": "Director", "vendor": "Redline Data Brokers",
            "category": "services", "amount_usd": 15000, "description": "lists"}})
        self.assertEqual(out["decision"], "deny")
        json.dumps(out)  # must not raise


if __name__ == "__main__":
    unittest.main()
