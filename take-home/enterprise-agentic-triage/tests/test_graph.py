"""graph tests — durable execution: checkpoints, retries, interrupt/resume."""
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
from graph import (END, Checkpointer, Command, GraphError, RetryPolicy,  # noqa: E402
                   StateGraph, interrupt_unless_resumed)


class Flaky(Exception):
    pass


def build_linear():
    g = StateGraph(entry="a")
    g.add_node("a", lambda s: {**s, "a": True})
    g.add_edge("a", "b")
    g.add_node("b", lambda s: {**s, "b": True})
    g.add_edge("b", END)
    return g


class TestRun(unittest.TestCase):
    def test_linear_run_checkpoints_every_step(self):
        with tempfile.TemporaryDirectory() as d:
            cp = Checkpointer(os.path.join(d, "cp.jsonl"))
            out = build_linear().run({}, checkpointer=cp)
            self.assertEqual(out["status"], "completed")
            self.assertTrue(out["state"]["a"] and out["state"]["b"])
            self.assertEqual([r["node"] for r in cp.history()], ["a", "b"])

    def test_conditional_edges_route_on_state(self):
        g = StateGraph(entry="a")
        g.add_node("a", lambda s: s)
        g.add_conditional_edges("a", lambda s: "hot" if s["x"] else "cold")
        g.add_node("hot", lambda s: {**s, "path": "hot"})
        g.add_node("cold", lambda s: {**s, "path": "cold"})
        g.add_edge("hot", END)
        g.add_edge("cold", END)
        self.assertEqual(g.run({"x": True})["state"]["path"], "hot")
        self.assertEqual(g.run({"x": False})["state"]["path"], "cold")

    def test_missing_edge_is_loud(self):
        g = StateGraph(entry="a")
        g.add_node("a", lambda s: s)
        with self.assertRaises(GraphError):
            g.run({})

    def test_max_steps_stops_cycles(self):
        g = StateGraph(entry="a")
        g.add_node("a", lambda s: s)
        g.add_edge("a", "a")
        with self.assertRaises(GraphError):
            g.run({}, max_steps=5)


class TestRetry(unittest.TestCase):
    def test_transient_failure_retried_to_success(self):
        calls = {"n": 0}

        def flaky(state):
            calls["n"] += 1
            if calls["n"] < 3:
                raise Flaky("transient")
            return {**state, "ok": True}

        g = StateGraph(entry="a")
        g.add_node("a", flaky, retry=RetryPolicy(max_attempts=3, retry_on=(Flaky,)))
        g.add_edge("a", END)
        out = g.run({})
        self.assertTrue(out["state"]["ok"])
        self.assertEqual(out["state"]["__attempts__"], 3)

    def test_exhausted_retries_raise_with_cause(self):
        g = StateGraph(entry="a")

        def always(state):
            raise Flaky("down")

        g.add_node("a", always, retry=RetryPolicy(max_attempts=2, retry_on=(Flaky,)))
        g.add_edge("a", END)
        with self.assertRaisesRegex(GraphError, "after 2 attempts"):
            g.run({})


class TestHumanInTheLoop(unittest.TestCase):
    def _gate_graph(self):
        g = StateGraph(entry="gate")

        def gate(state):
            verdict = interrupt_unless_resumed(state, "needs-human", {"k": 1})
            return {**state, "verdict": verdict}

        # An interrupt must never be eaten by a retry policy.
        g.add_node("gate", gate, retry=RetryPolicy(max_attempts=3, retry_on=(Exception,)))
        g.add_edge("gate", END)
        return g

    def test_interrupt_pauses_and_resume_completes(self):
        with tempfile.TemporaryDirectory() as d:
            cp = Checkpointer(os.path.join(d, "cp.jsonl"))
            g = self._gate_graph()
            paused = g.run({"x": 1}, checkpointer=cp)
            self.assertEqual(paused["status"], "interrupted")
            self.assertEqual(paused["reason"], "needs-human")
            self.assertEqual(cp.last()["status"], "interrupted")

            done = g.run({}, checkpointer=cp, resume=Command(resume={"action": "ok"}))
            self.assertEqual(done["status"], "completed")
            self.assertEqual(done["state"]["verdict"], {"action": "ok"})
            self.assertEqual(done["state"]["x"], 1, "state survived the pause")

    def test_resume_without_interrupt_is_loud(self):
        with tempfile.TemporaryDirectory() as d:
            cp = Checkpointer(os.path.join(d, "cp.jsonl"))
            with self.assertRaises(GraphError):
                build_linear().run({}, checkpointer=cp, resume=Command(resume={}))


if __name__ == "__main__":
    unittest.main()
