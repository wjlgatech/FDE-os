"""facts tests — the parser graded against hand-verified values from real filings."""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
from facts import find_metric, load_facts  # noqa: E402

FACTS = load_facts()

HAND_VERIFIED = [
    ("Tesla", "total_revenue", "FY2025", 94827), ("Tesla", "total_revenue", "FY2024", 97690),
    ("Tesla", "total_revenue", "FY2023", 96773), ("Tesla", "net_income", "FY2025", 3855),
    ("Tesla", "net_income_attributable", "FY2025", 3794),
    ("Tesla", "total_revenue", "Q2-2026", 28236), ("Tesla", "total_revenue", "Q1-2026", 22387),
    ("Tesla", "total_revenue", "6M-2026", 50623), ("Tesla", "net_income", "Q1-2026", 491),
    ("Tesla", "diluted_eps", "FY2025", 1.08), ("Tesla", "operating_income", "FY2025", 4355),
    ("Tesla", "gross_profit", "FY2025", 17094), ("Tesla", "operating_cash_flow", "FY2025", 14747),
    ("Tesla", "cash_and_equivalents", "FY2025", 16513), ("Tesla", "total_assets", "FY2025", 137806),
    ("Apple", "total_revenue", "FY2025", 416161), ("Apple", "net_income", "FY2025", 112010),
    ("Apple", "diluted_eps", "FY2025", 7.46), ("Apple", "cash_and_equivalents", "FY2025", 35934),
    ("Apple", "operating_income", "FY2025", 133050),
]


class TestHandVerifiedValues(unittest.TestCase):
    def test_every_hand_verified_value_extracts_exactly_once(self):
        for company, metric, period, want in HAND_VERIFIED:
            with self.subTest(f"{company}.{metric}.{period}"):
                hits, _ = find_metric(FACTS, company, metric, period)
                self.assertEqual(sorted({h["value"] for h in hits}), [want])

    def test_near_miss_pair_stays_distinct(self):
        ni, near = find_metric(FACTS, "Tesla", "net_income", "FY2025")
        nia, _ = find_metric(FACTS, "Tesla", "net_income_attributable", "FY2025")
        self.assertEqual(ni[0]["value"], 3855)
        self.assertEqual(nia[0]["value"], 3794)
        self.assertTrue(any("attributable" in n["label"].lower() for n in near),
                        "asking net_income must SURFACE the attributable near-miss")

    def test_instant_metrics_never_answer_from_cashflow_rows(self):
        hits, _ = find_metric(FACTS, "Tesla", "cash_and_equivalents", "FY2025")
        for h in hits:
            self.assertEqual(h.get("section"), "CONSOLIDATED BALANCE SHEETS")
            self.assertTrue(h["period"].startswith("AsOf-"))

    def test_facts_carry_full_provenance(self):
        f = find_metric(FACTS, "Apple", "total_revenue", "FY2025")[0][0]
        for key in ("doc_id", "page", "line", "quote", "source_url", "scale"):
            self.assertTrue(f.get(key), f"fact missing {key}")
        self.assertIn("sec.gov/Archives", f["source_url"])


if __name__ == "__main__":
    unittest.main()
