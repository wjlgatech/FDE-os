"""memory tests — cumulative vendor spend and budgeted context assembly."""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
from memory import ContextAssembler, ContextItem, SessionMemory  # noqa: E402


def req(rid, vendor, amount, date):
    return {"id": rid, "vendor": vendor, "amount_usd": amount, "date": date}


class TestSessionMemory(unittest.TestCase):
    def test_cumulative_counts_approved_only_inside_window(self):
        m = SessionMemory()
        m.record(req("R-1", "Acme", 4000, "2026-05-01"), "approve")
        m.record(req("R-2", "Acme", 9000, "2026-05-02"), "escalate")  # not spend
        m.record(req("R-3", "Acme", 2000, "2026-03-01"), "approve")   # outside window
        m.record(req("R-4", "Other", 5000, "2026-05-03"), "approve")  # other vendor
        self.assertEqual(m.cumulative_vendor_spend("Acme", "2026-05-12"), 4000)

    def test_window_boundary_is_inclusive(self):
        m = SessionMemory()
        m.record(req("R-1", "Acme", 1000, "2026-04-12"), "approve")
        self.assertEqual(m.cumulative_vendor_spend("Acme", "2026-05-12"), 1000)
        self.assertEqual(m.cumulative_vendor_spend("Acme", "2026-05-13"), 0)

    def test_summary_names_prior_requests(self):
        m = SessionMemory()
        self.assertIn("No prior requests", m.vendor_summary("Acme"))
        m.record(req("R-1", "Acme", 4000, "2026-05-01"), "approve")
        self.assertIn("R-1: $4,000 → approve", m.vendor_summary("Acme"))


class TestContextAssembler(unittest.TestCase):
    def test_budget_is_enforced_and_receipted(self):
        items = [ContextItem("a", "x " * 100, priority=5),
                 ContextItem("b", "y " * 100, priority=4),
                 ContextItem("c", "z " * 100, priority=3)]
        included, receipt = ContextAssembler(budget_tokens=250).assemble(items)
        self.assertEqual([i.kind for i in included], ["a", "b"])
        self.assertEqual([e["kind"] for e in receipt["excluded"]], ["c"])
        self.assertEqual(receipt["used_tokens"], 200)
        self.assertFalse(receipt["over_budget"])

    def test_pinned_always_survives_even_over_budget(self):
        items = [ContextItem("request", "r " * 100, pinned=True),
                 ContextItem("policy", "p " * 100, priority=5)]
        included, receipt = ContextAssembler(budget_tokens=50).assemble(items)
        self.assertEqual([i.kind for i in included], ["request"])
        self.assertTrue(receipt["over_budget"], "pinned overflow must be visible")

    def test_smaller_lower_priority_item_can_backfill(self):
        items = [ContextItem("big", "x " * 300, priority=5),
                 ContextItem("small", "y " * 10, priority=1)]
        included, _ = ContextAssembler(budget_tokens=100).assemble(items)
        self.assertEqual([i.kind for i in included], ["small"])


if __name__ == "__main__":
    unittest.main()
