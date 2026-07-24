"""end-to-end tests — the whole take-home, graded against its own ground truth.

Covers: the full batch matching ground truth via the CLI contract
(run.py → eval.py, subprocess — the same finish line CI uses), the
memory-dependence of the split-purchase catch, the HITL pause/resume flow
issuing a PO through the gated tool, and the eval gate failing loudly on a
tampered run.
"""
import json
import os
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
from agent import TriageAgent  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CORPUS = os.path.join(ROOT, "corpus")
DATA = os.path.join(ROOT, "data")


def load_requests():
    with open(os.path.join(DATA, "requests.jsonl"), encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def load_truth():
    with open(os.path.join(DATA, "ground-truth.json"), encoding="utf-8") as f:
        return json.load(f)


class TestFullBatchViaCLI(unittest.TestCase):
    def test_run_then_eval_exits_zero(self):
        with tempfile.TemporaryDirectory() as out:
            run = subprocess.run(
                [sys.executable, os.path.join(ROOT, "scripts", "run.py"),
                 "--out", out], capture_output=True, text=True)
            self.assertEqual(run.returncode, 0, run.stderr)
            ev = subprocess.run(
                [sys.executable, os.path.join(ROOT, "scripts", "eval.py"),
                 "--run-dir", out], capture_output=True, text=True)
            self.assertEqual(ev.returncode, 0, ev.stdout + ev.stderr)
            self.assertIn("VERDICT: PASS", ev.stdout)

    def test_tampered_run_fails_the_gate_with_exit_2(self):
        with tempfile.TemporaryDirectory() as out:
            subprocess.run([sys.executable, os.path.join(ROOT, "scripts", "run.py"),
                            "--out", out], capture_output=True, text=True, check=True)
            path = os.path.join(out, "decisions.json")
            with open(path, encoding="utf-8") as f:
                decisions = json.load(f)
            decisions["R-002"]["decision"] = "approve"  # a missed escalation
            with open(path, "w", encoding="utf-8") as f:
                json.dump(decisions, f)
            ev = subprocess.run(
                [sys.executable, os.path.join(ROOT, "scripts", "eval.py"),
                 "--run-dir", out], capture_output=True, text=True)
            self.assertEqual(ev.returncode, 2)
            self.assertIn("escalation_recall", ev.stdout)


class TestAgentBehaviors(unittest.TestCase):
    def _agent(self):
        return TriageAgent(CORPUS, DATA)

    def test_split_purchase_is_only_caught_with_memory(self):
        reqs = {r["id"]: r for r in load_requests()}
        with tempfile.TemporaryDirectory() as d:
            fresh = self._agent()  # no R-001 in memory → R-006 looks fine alone
            alone = fresh.process(reqs["R-006"], os.path.join(d, "a.jsonl"))
            self.assertEqual(alone["decision"], "approve")

            sessioned = self._agent()
            sessioned.process(reqs["R-001"], os.path.join(d, "b.jsonl"))
            after = sessioned.process(reqs["R-006"], os.path.join(d, "c.jsonl"))
            self.assertEqual(after["decision"], "escalate")
            self.assertEqual(after["escalate_to"], "authority-chain")

    def test_escalation_pauses_then_human_resume_issues_po(self):
        req = {r["id"]: r for r in load_requests()}["R-002"]
        with tempfile.TemporaryDirectory() as d:
            cp = os.path.join(d, "cp.jsonl")
            agent = self._agent()
            paused = agent.process(req, cp)
            self.assertEqual(paused["status"], "awaiting_human")
            self.assertEqual(paused["gate_reason"], "spend-committee")

            final = agent.resume(cp, {"action": "approve"})
            self.assertEqual(final["decision"], "approve")
            self.assertTrue(final["po_number"].startswith("PO-"),
                            "gated PO tool must fire only after human approval")

    def test_human_can_also_deny_at_the_gate(self):
        req = {r["id"]: r for r in load_requests()}["R-009"]
        with tempfile.TemporaryDirectory() as d:
            cp = os.path.join(d, "cp.jsonl")
            agent = self._agent()
            agent.process(req, cp)
            final = agent.resume(cp, {"action": "deny"})
            self.assertEqual(final["decision"], "deny")
            self.assertIsNone(final.get("po_number"))

    def test_injection_is_flagged_but_never_changes_the_decision(self):
        req = {r["id"]: r for r in load_requests()}["R-008"]
        with tempfile.TemporaryDirectory() as d:
            events = []
            final = self._agent().process(req, os.path.join(d, "cp.jsonl"),
                                          tracer=events.append)
            self.assertEqual(final["decision"], "approve")
            self.assertIn("prompt-injection", final["guard_flags"])
            hygiene = [e for e in events if e.get("guard") == "instruction-hygiene"]
            self.assertTrue(hygiene and not hygiene[0]["decision_affected"])

    def test_every_decision_matches_ground_truth_in_session_order(self):
        truth = load_truth()
        agent = self._agent()
        with tempfile.TemporaryDirectory() as d:
            for req in load_requests():
                got = agent.process(req, os.path.join(d, f"{req['id']}.jsonl"))
                with self.subTest(request=req["id"]):
                    self.assertEqual(got["decision"], truth[req["id"]]["decision"])
                    if truth[req["id"]].get("escalate_to"):
                        self.assertEqual(got["escalate_to"],
                                         truth[req["id"]]["escalate_to"])


if __name__ == "__main__":
    unittest.main()
