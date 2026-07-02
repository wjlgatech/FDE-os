import os
import sys
import unittest

HERE = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(HERE, ".."))
import collectors as co  # noqa: E402
import match_engine as me  # noqa: E402

EX = os.path.join(HERE, "..", "examples")


class TestCollectors(unittest.TestCase):
    def test_demand_groups_roles_under_teams(self):
        d = co.CsvDemandCollector(os.path.join(EX, "demand.csv")).collect()
        teams = {t["team"]: t for t in d["teams"]}
        self.assertEqual(len(teams["Client-A RAG platform"]["open_roles"]), 2)
        lead = teams["Client-A RAG platform"]["open_roles"][0]
        self.assertEqual(lead["skills"], ["python", "rag", "agents"])
        self.assertEqual(lead["count"], 1)
        self.assertEqual(lead["role_type"], "technical")

    def test_supply_merges_roster_with_vetting_evidence(self):
        s = co.CsvSupplyCollector(os.path.join(EX, "roster.csv"), os.path.join(EX, "candidates")).collect()
        p = {x["id"]: x for x in s["people"]}
        self.assertTrue(p["anon-0042"]["available"])
        self.assertFalse(p["anon-0045"]["available"])
        # evidence block came from candidates/<id>.json
        self.assertIn("references", p["anon-0042"]["reliability"])
        self.assertAlmostEqual(p["anon-0042"]["technical_competence"]["work_sample"]["score"], 0.87)

    def test_supply_without_vetting_record_collects_empty_evidence(self):
        # a person on the roster with no candidate file must not silently pass the gate
        s = co.CsvSupplyCollector(os.path.join(EX, "roster.csv"), candidates_dir=None).collect()
        p = {x["id"]: x for x in s["people"]}
        self.assertEqual(p["anon-0042"].get("reliability", {}), {})

    def test_collect_then_match_matches_the_baked_example(self):
        demand = co.CsvDemandCollector(os.path.join(EX, "demand.csv")).collect()
        supply = co.CsvSupplyCollector(os.path.join(EX, "roster.csv"), os.path.join(EX, "candidates")).collect()
        plan = me.plan(supply, demand)
        assigned = {b["role_id"]: b["assigned"] for b in plan["board"]}
        self.assertEqual(assigned["FDE-lead"], ["anon-0042"])
        self.assertEqual(assigned["FDE-2"], [])  # short → at risk
        clientA = next(t for t in plan["team_next_steps"] if t["team"].startswith("Client-A"))
        self.assertTrue(clientA["milestone_at_risk"])

    def test_enterprise_collectors_are_honest_stubs(self):
        with self.assertRaises(NotImplementedError):
            co.MySchedulingCollector().collect()
        with self.assertRaises(NotImplementedError):
            co.WorkdayCollector().collect()


if __name__ == "__main__":
    unittest.main()
