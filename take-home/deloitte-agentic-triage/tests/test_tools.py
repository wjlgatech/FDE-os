"""tool registry tests — schema validation, permission gate, idempotency."""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
from tools import (PermissionRequired, Tool, ToolError, ToolRegistry,  # noqa: E402
                   build_registry)

DATA = os.path.join(os.path.dirname(__file__), "..", "data")


class TestValidation(unittest.TestCase):
    def setUp(self):
        self.reg = ToolRegistry()
        self.reg.register(Tool("add", "adds", {"a": int, "b": int},
                               lambda a, b: {"sum": a + b}))

    def test_happy_path(self):
        self.assertEqual(self.reg.call("add", {"a": 2, "b": 3})["sum"], 5)

    def test_errors_name_the_exact_problem(self):
        cases = [
            ({"a": 1}, "missing required arg"),
            ({"a": 1, "b": 2, "c": 3}, "unexpected arg"),
            ({"a": 1, "b": "two"}, "must be int"),
        ]
        for args, needle in cases:
            with self.subTest(args=args):
                with self.assertRaisesRegex(ToolError, needle):
                    self.reg.call("add", args)

    def test_unknown_tool_lists_available(self):
        with self.assertRaisesRegex(ToolError, "available.*add"):
            self.reg.call("nope", {})

    def test_failures_still_hit_the_trace(self):
        events = []
        with self.assertRaises(ToolError):
            self.reg.call("add", {"a": 1}, tracer=events.append)
        self.assertFalse(events[0]["ok"])
        self.assertIn("missing", events[0]["error"])


class TestPermissionAndIdempotency(unittest.TestCase):
    def setUp(self):
        self.reg = build_registry(DATA)

    def test_gated_tool_requires_human_approval(self):
        args = {"request_id": "R-X", "vendor": "V", "amount_usd": 1}
        with self.assertRaises(PermissionRequired):
            self.reg.call("create_purchase_order", args)
        po = self.reg.call("create_purchase_order", args, human_approved=True)
        self.assertTrue(po["po_number"].startswith("PO-"))

    def test_idempotency_key_dedupes_side_effects(self):
        events = []
        args = {"request_id": "R-X", "vendor": "V", "amount_usd": 1}
        first = self.reg.call("create_purchase_order", args, human_approved=True,
                              idempotency_key="R-X", tracer=events.append)
        second = self.reg.call("create_purchase_order", args, human_approved=True,
                               idempotency_key="R-X", tracer=events.append)
        self.assertEqual(first, second)
        self.assertFalse(events[0]["cached"])
        self.assertTrue(events[1]["cached"])

    def test_vendor_lookup_handles_unknown_honestly(self):
        known = self.reg.call("vendor_risk_lookup", {"vendor": "CloudMetric"})
        unknown = self.reg.call("vendor_risk_lookup", {"vendor": "Ghost Corp"})
        self.assertTrue(known["known"])
        self.assertFalse(unknown["known"])
        self.assertIsNone(unknown["tier"])


if __name__ == "__main__":
    unittest.main()
