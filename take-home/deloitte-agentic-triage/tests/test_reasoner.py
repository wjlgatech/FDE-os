"""reasoner tests — decisions come FROM retrieved text, never from constants.

The two tests that matter most in this file: (1) edit the policy text and the
decision changes — proof nothing is hardcoded; (2) withhold the governing
clause and the reasoner refuses to guess — no evidence ⇒ No.
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
from reasoner import PolicyReasoner  # noqa: E402
from retrieval import Chunk  # noqa: E402


def chunk(doc, text, effective=None):
    return Chunk(doc, "h", 1, 5, text, effective)


DELEGATION = chunk("delegation-of-authority.md",
                   "- Managers: up to and including $10,000.\n"
                   "- Directors: up to and including $100,000.\n"
                   "Any purchase request above $250,000 must be referred to the "
                   "Spend Committee.")
REQ = {"id": "R-T", "date": "2026-05-10", "role": "Manager", "vendor": "V",
       "category": "goods", "amount_usd": 8000, "description": "d"}
TOOLS = {"vendor": {"known": True, "tier": "Standard", "dpa_on_file": False,
                    "soc2": False}, "catalog": None}


def decide(request, chunks, tools=TOOLS, cumulative=0):
    return PolicyReasoner().decide(request, {
        "chunks": chunks, "tools": tools, "memory": {"cumulative_spend": cumulative}})


class TestGroundedThresholds(unittest.TestCase):
    def test_limits_are_parsed_from_the_retrieved_text(self):
        self.assertEqual(decide(REQ, [DELEGATION]).outcome, "approve")
        # Same request, tighter policy text → different decision. Nothing is
        # hardcoded: the corpus governs.
        tighter = chunk("delegation-of-authority.md",
                        "- Managers: up to and including $5,000.\n"
                        "Any purchase request above $250,000 must be referred to "
                        "the Spend Committee.")
        d = decide(REQ, [tighter])
        self.assertEqual(d.outcome, "escalate")
        self.assertEqual(d.escalate_to, "authority-chain")

    def test_missing_governing_clause_refuses_instead_of_guessing(self):
        d = decide(REQ, [chunk("procurement-policy-v3.md", "Unrelated text.")])
        self.assertEqual(d.outcome, "escalate")
        self.assertEqual(d.escalate_to, "insufficient-grounding")
        self.assertFalse(d.grounded)

    def test_every_fired_rule_carries_a_verbatim_citation(self):
        d = decide(REQ, [DELEGATION])
        self.assertTrue(d.reasons)
        for r in d.reasons:
            self.assertIn(r["citation"]["doc"], "delegation-of-authority.md")
            self.assertTrue(r["citation"]["quote"])


class TestSupersede(unittest.TestCase):
    V3 = chunk("procurement-policy-v3.md",
               "Software purchases above $50,000 require written approval from "
               "the CTO.", effective="2025-01-01")
    V4 = chunk("procurement-policy-v4-amendment.md",
               "Software purchases above $25,000 require written approval from "
               "the CTO.", effective="2026-04-01")
    SW_REQ = {**REQ, "role": "Director", "category": "software", "amount_usd": 30000}
    SW_TOOLS = {"vendor": TOOLS["vendor"], "catalog": {"approved": True}}

    def test_latest_effective_version_governs(self):
        d = decide(self.SW_REQ, [DELEGATION, self.V3, self.V4], tools=self.SW_TOOLS)
        self.assertEqual((d.outcome, d.escalate_to), ("escalate", "cto"))
        cited = {r["citation"]["doc"] for r in d.reasons}
        self.assertIn("procurement-policy-v4-amendment.md", cited)

    def test_before_the_amendment_v3_still_governs(self):
        early = {**self.SW_REQ, "date": "2026-03-01"}
        d = decide(early, [DELEGATION, self.V3, self.V4], tools=self.SW_TOOLS)
        self.assertEqual(d.outcome, "approve", "$30k < v3's $50k, v4 not yet effective")


class TestSeverityAndMemory(unittest.TestCase):
    def test_deny_outranks_escalations(self):
        risk = chunk("vendor-risk-tiers.md",
                     "Purchases from Prohibited vendors must be denied. Purchases "
                     "from unknown vendors must be escalated for vendor onboarding.")
        tools = {"vendor": {"known": True, "tier": "Prohibited", "dpa_on_file": False,
                            "soc2": False}, "catalog": None}
        d = decide({**REQ, "amount_usd": 300000}, [DELEGATION, risk], tools=tools)
        self.assertEqual(d.outcome, "deny")

    def test_cumulative_spend_flips_an_otherwise_fine_request(self):
        ok = decide(REQ, [DELEGATION], cumulative=0)
        split = decide(REQ, [DELEGATION], cumulative=4000)  # 8k + 4k > 10k
        self.assertEqual(ok.outcome, "approve")
        self.assertEqual((split.outcome, split.escalate_to),
                         ("escalate", "authority-chain"))
        self.assertIn("cumulative-over-limit", [r["rule"] for r in split.reasons])


if __name__ == "__main__":
    unittest.main()
