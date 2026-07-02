import json
import os
import sys
import unittest

HERE = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(HERE, ".."))
import match_engine as me  # noqa: E402

EX = os.path.join(HERE, "..", "examples")


def load(name):
    with open(os.path.join(EX, name), encoding="utf-8") as f:
        return json.load(f)


class TestMatchEngine(unittest.TestCase):
    def setUp(self):
        self.supply = load("supply.example.json")
        self.demand = load("demand.example.json")
        self.plan = me.plan(self.supply, self.demand)

    def test_no_double_booking(self):
        # one person can be assigned to at most one role across the whole board
        assigned = [pid for b in self.plan["board"] for pid in b["assigned"]]
        self.assertEqual(len(assigned), len(set(assigned)))

    def test_best_fit_wins_the_assignment(self):
        lead = next(b for b in self.plan["board"] if b["role_id"] == "FDE-lead")
        fde2 = next(b for b in self.plan["board"] if b["role_id"] == "FDE-2")
        self.assertIn("anon-0042", lead["assigned"])   # overlap 3 > overlap 2
        self.assertNotIn("anon-0042", fde2["assigned"])  # can't also fill FDE-2

    def test_shortfall_flags_milestone_at_risk(self):
        clientA = next(t for t in self.plan["team_next_steps"] if t["team"].startswith("Client-A"))
        self.assertTrue(clientA["milestone_at_risk"])
        self.assertIn("technical competence", clientA["next_best_step"])  # names the fastest close

    def test_conditional_pool_carries_blocker(self):
        fde2 = next(b for b in self.plan["board"] if b["role_id"] == "FDE-2")
        cond = next(c for c in fde2["conditional"] if c["id"] == "anon-0043")
        self.assertIn("technical_competence", cond["blockers"])

    def test_unavailable_person_never_assigned(self):
        assigned = {pid for b in self.plan["board"] for pid in b["assigned"]}
        self.assertNotIn("anon-0045", assigned)
        s = next(x for x in self.plan["person_next_steps"] if x["id"] == "anon-0045")
        self.assertEqual(s["status"], "UNAVAILABLE")

    def test_non_technical_role_gate_is_softer(self):
        # anon-0044 has no work sample but fills a non_technical role
        deliv = next(b for b in self.plan["board"] if b["role_id"] == "delivery-lead")
        self.assertIn("anon-0044", deliv["assigned"])

    def test_person_statuses(self):
        st = {x["id"]: x["status"] for x in self.plan["person_next_steps"]}
        self.assertEqual(st["anon-0042"], "ASSIGN")
        self.assertEqual(st["anon-0043"], "CONDITIONAL")
        self.assertEqual(st["anon-0044"], "ASSIGN")

    def test_gate_reused_not_reimplemented(self):
        # a person blocked by the scorecard must not be eligible anywhere
        for b in self.plan["board"]:
            for e in b["eligible"]:
                self.assertTrue(e["go"])


if __name__ == "__main__":
    unittest.main()
