# Source: take-home/enterprise-agentic-triage/scripts/graph.py

```python
#!/usr/bin/env python3
"""graph — a durable-execution state graph, stdlib only.

LangGraph 1.x semantics rebuilt from the primitive up, to show the machinery
is understood rather than imported: a checkpoint after every super-step,
`interrupt_unless_resumed` for human-in-the-loop gates, `Command(resume=...)`
to continue a paused run, per-node retry policies, and a bounded step count
so a bad router can never loop forever.

One honest divergence from LangGraph: real `interrupt()` replays the node and
*returns* the resume value ambiently; here the node asks the state for it
explicitly (`interrupt_unless_resumed(state, ...)`). Same contract, no
hidden global.
"""
from __future__ import annotations

import json
import os

END = "__end__"


class GraphError(Exception):
    pass


class GraphInterrupt(Exception):
    """A node paused the run for a human. Never retried, never swallowed."""

    def __init__(self, reason: str, payload=None):
        super().__init__(reason)
        self.reason = reason
        self.payload = payload


def interrupt_unless_resumed(state: dict, reason: str, payload=None):
    """Pause here unless a human already answered (via Command(resume=...))."""
    if "__resume__" in state:
        return state.pop("__resume__")
    raise GraphInterrupt(reason, payload)


class Command:
    """Resume instruction for an interrupted run: Command(resume=<human input>)."""

    def __init__(self, resume=None):
        self.resume = resume


class RetryPolicy:
    def __init__(self, max_attempts: int = 3, retry_on=(Exception,)):
        self.max_attempts = max_attempts
        self.retry_on = retry_on


class Checkpointer:
    """Durable JSON checkpoint stream — one record per super-step, replayable."""

    def __init__(self, path: str):
        self.path = path
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)

    def save(self, record: dict) -> None:
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, sort_keys=True) + "\n")

    def history(self) -> list[dict]:
        if not os.path.exists(self.path):
            return []
        with open(self.path, encoding="utf-8") as f:
            return [json.loads(line) for line in f if line.strip()]

    def last(self) -> dict | None:
        h = self.history()
        return h[-1] if h else None


class StateGraph:
    def __init__(self, entry: str):
        self.entry = entry
        self.nodes: dict = {}
        self.retries: dict = {}
        self.edges: dict = {}
        self.routers: dict = {}

    def add_node(self, name: str, fn, retry: RetryPolicy | None = None):
        self.nodes[name] = fn
        if retry:
            self.retries[name] = retry
        return self

    def add_edge(self, src: str, dst: str):
        self.edges[src] = dst
        return self

    def add_conditional_edges(self, src: str, router):
        self.routers[src] = router
        return self

    def _run_node(self, name: str, state: dict) -> dict:
        policy = self.retries.get(name, RetryPolicy(max_attempts=1))
        last = None
        for attempt in range(1, policy.max_attempts + 1):
            try:
                out = self.nodes[name](state)
            except GraphInterrupt:
                raise  # a human gate is not a failure — never retry it
            except policy.retry_on as e:  # noqa: PERF203 — retry loop is the point
                last = e
                continue
            if not isinstance(out, dict):
                raise GraphError(f"node '{name}' must return a dict state")
            out["__attempts__"] = attempt
            return out
        raise GraphError(f"node '{name}' failed after {policy.max_attempts} attempts: {last}")

    def _next(self, name: str, state: dict) -> str:
        if name in self.routers:
            return self.routers[name](state)
        if name in self.edges:
            return self.edges[name]
        raise GraphError(f"node '{name}' has no outgoing edge")

    def run(self, state: dict, checkpointer: Checkpointer | None = None,
            tracer=None, max_steps: int = 50, resume: Command | None = None) -> dict:
        """Drive the graph to END or to an interrupt. Returns
        {"status": "completed", "state": ...} or
        {"status": "interrupted", "node": ..., "reason": ..., "payload": ...}."""
        current = self.entry
        seq = 0
        if resume is not None:
            if checkpointer is None:
                raise GraphError("resume requires the checkpointer of the paused run")
            last = checkpointer.last()
            if not last or last.get("status") != "interrupted":
                raise GraphError("nothing to resume: no interrupted checkpoint found")
            state = dict(last["state"])
            state["__resume__"] = resume.resume
            current = last["node"]
            seq = last["seq"]

        while current != END:
            seq += 1
            if seq > max_steps:
                raise GraphError(f"max_steps={max_steps} exceeded at node '{current}'")
            try:
                state = self._run_node(current, state)
            except GraphInterrupt as gi:
                record = {"seq": seq, "node": current, "status": "interrupted",
                          "reason": gi.reason, "payload": gi.payload, "state": state}
                if checkpointer:
                    checkpointer.save(record)
                if tracer:
                    tracer({"kind": "step", "seq": seq, "node": current,
                            "status": "interrupted", "reason": gi.reason})
                return {"status": "interrupted", "node": current,
                        "reason": gi.reason, "payload": gi.payload}
            if checkpointer:
                checkpointer.save({"seq": seq, "node": current, "status": "ok",
                                   "state": state})
            if tracer:
                tracer({"kind": "step", "seq": seq, "node": current, "status": "ok",
                        "attempts": state.get("__attempts__", 1)})
            current = self._next(current, state)

        return {"status": "completed", "state": state}

```
