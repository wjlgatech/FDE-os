#!/usr/bin/env python3
"""agent — the triage agent: six JD terms wired into one durable graph.

    intake ──(invalid)──────────────────────────────► finalize
      │ ok
      ▼
    enrich (tools, retried on transient) ─► retrieve ─► assemble ─► decide
                                               ▲                      │
                                               └── expand ◄─(ungrounded, once)
                                                                      │
                                              guard ◄─────────────────┘
                                                │
                    ┌─(escalate)─► human_gate (interrupt → Command(resume))─┐
                    │                                                       ▼
                    └─(approve/deny)──────────────────────────────────► finalize

Every step checkpoints; every tool call, retrieval, context receipt, guard
trip, and decision lands in the trace. Escalations pause at the human gate —
in batch mode the pause IS the answer (the agent's job is to know what it
may not decide); a human can resume with Command(resume=...) and only then
does the gated purchase-order tool fire.
"""
from __future__ import annotations

import json

from graph import (END, Checkpointer, Command, RetryPolicy, StateGraph,
                   interrupt_unless_resumed)
from guardrails import apply_monotonic, hard_floor, scan_injection, validate_request
from memory import ContextAssembler, ContextItem, SessionMemory
from reasoner import PolicyReasoner
from retrieval import Retriever, compress
from tools import ToolTransientError, build_registry


class TriageAgent:
    def __init__(self, corpus_dir: str, data_dir: str, budget_tokens: int = 350):
        self.retriever = Retriever(corpus_dir)
        self.registry = build_registry(data_dir)
        self.reasoner = PolicyReasoner()
        self.assembler = ContextAssembler(budget_tokens)
        self.memory = SessionMemory()
        self._by_id = {c.id: c for c in self.retriever.chunks}
        self._tracer = None
        self.graph = self._build()

    # -- nodes ---------------------------------------------------------------

    def _intake(self, state: dict) -> dict:
        req = state["request"]
        errors = validate_request(req)
        flags = scan_injection(str(req.get("description", "")))
        state["guard_flags"] = ["prompt-injection"] if flags else []
        if flags and self._tracer:
            self._tracer({"kind": "guard", "guard": "instruction-hygiene",
                          "flags": flags, "decision_affected": False})
        state["decision"] = ({"outcome": "invalid", "escalate_to": None,
                              "grounded": True, "reasons": [], "errors": errors}
                             if errors else None)
        return state

    def _enrich(self, state: dict) -> dict:
        req = state["request"]
        vendor = self.registry.call("vendor_risk_lookup", {"vendor": req["vendor"]},
                                    tracer=self._tracer, idempotency_key=req["id"])
        catalog = None
        if req["category"] in ("software", "cloud"):
            catalog = self.registry.call("software_catalog_lookup",
                                         {"vendor": req["vendor"]},
                                         tracer=self._tracer,
                                         idempotency_key=req["id"])
        state["tools"] = {"vendor": vendor, "catalog": catalog}
        return state

    def _queries(self, state: dict) -> list[str]:
        req, vendor = state["request"], state["tools"]["vendor"]
        qs = ["approval limits by role Managers Directors Vice Presidents Spend Committee",
              "cumulative spend same vendor rolling 30-day window split orders",
              "competitive bids evidence purchases above Preferred tier exempt"]
        if not vendor["known"]:
            qs.append("unknown vendors escalated vendor onboarding master database")
        elif vendor["tier"] in ("Prohibited", "High-Risk"):
            qs.append("Prohibited vendors denied High-Risk enhanced due diligence "
                      "escalated Third-Party Risk Management")
        if req.get("processes_pii"):
            qs.append("personal data PII Data Processing Agreement DPA escalated "
                      "Privacy Office")
        if req["category"] in ("software", "cloud"):
            qs.append("software purchases threshold CTO approval amendment supersedes")
            qs.append("approved software list architecture review escalated "
                      "Enterprise Architecture")
        if state.get("expanded"):
            qs.append("purchase policy approval escalated denied requirements")
        return qs

    def _retrieve(self, state: dict) -> dict:
        top_k = 5 if state.get("expanded") else 3
        seen, ids = set(), []
        for q in self._queries(state):
            hits = self.retriever.search(q, top_k=top_k)
            if self._tracer:
                self._tracer({"kind": "retrieval", "query": q,
                              "results": [{"id": c.id, **scores} for c, scores in hits]})
            for c, _ in hits:
                if c.id not in seen:
                    seen.add(c.id)
                    ids.append(c.id)
        state["evidence_ids"] = ids
        return state

    def _assemble(self, state: dict) -> dict:
        req = state["request"]
        cumulative = self.memory.cumulative_vendor_spend(req["vendor"], req["date"])
        state["memory_facts"] = {"cumulative_spend": cumulative}
        query = " ".join(self._queries(state))
        items = [ContextItem("request", json.dumps(req), pinned=True)]
        for cid in state["evidence_ids"]:
            items.append(ContextItem(f"policy:{cid}",
                                     compress(self._by_id[cid], query), priority=5))
        items.append(ContextItem("tools", json.dumps(state["tools"]), priority=4))
        items.append(ContextItem("memory", self.memory.vendor_summary(req["vendor"]),
                                 priority=3))
        _, receipt = self.assembler.assemble(items)
        state["context_receipt"] = receipt
        if self._tracer:
            self._tracer({"kind": "context", **receipt})
        return state

    def _decide(self, state: dict) -> dict:
        req = state["request"]
        evidence = {"chunks": [self._by_id[i] for i in state["evidence_ids"]],
                    "tools": state["tools"], "memory": state["memory_facts"]}
        decision = self.reasoner.decide(req, evidence)
        state["decision"] = decision.as_dict()
        if self._tracer:
            self._tracer({"kind": "decision", "grounded": decision.grounded,
                          "outcome": decision.outcome,
                          "escalate_to": decision.escalate_to,
                          "rules": [r["rule"] for r in decision.reasons]})
        return state

    def _route_decide(self, state: dict) -> str:
        if not state["decision"]["grounded"] and not state.get("expanded"):
            return "expand"  # one bounded self-correction pass, then accept
        return "guard"

    def _expand(self, state: dict) -> dict:
        state["expanded"] = True
        if self._tracer:
            self._tracer({"kind": "self-correction",
                          "action": "expand retrieval — decision was ungrounded"})
        return state

    def _guard(self, state: dict) -> dict:
        decision = state["decision"]
        floor = hard_floor(state["request"], state["tools"]["vendor"])
        final, tripped = apply_monotonic(decision["outcome"], floor)
        if tripped:
            decision["outcome"] = final
            if final == "escalate" and not decision.get("escalate_to"):
                decision["escalate_to"] = "hard-floor"
            decision["reasons"].append({"rule": "hard-floor", "citation": None})
        decision["guard_tripped"] = tripped
        if self._tracer:
            self._tracer({"kind": "guard", "guard": "monotonic-severity",
                          "floor": floor, "tripped": tripped, "final": final})
        return state

    def _human_gate(self, state: dict) -> dict:
        decision = state["decision"]
        verdict = interrupt_unless_resumed(
            state, reason=decision.get("escalate_to") or "escalation",
            payload={"request_id": state["request"]["id"], "decision": decision})
        decision["human_verdict"] = verdict
        if verdict.get("action") == "approve":
            decision["outcome"] = "approve"
            po = self.registry.call(
                "create_purchase_order",
                {"request_id": state["request"]["id"],
                 "vendor": state["request"]["vendor"],
                 "amount_usd": state["request"]["amount_usd"]},
                tracer=self._tracer, human_approved=True,
                idempotency_key=state["request"]["id"])
            decision["po_number"] = po["po_number"]
        elif verdict.get("action") == "deny":
            decision["outcome"] = "deny"
        return state

    def _finalize(self, state: dict) -> dict:
        req, decision = state["request"], state["decision"]
        if decision["outcome"] != "invalid":
            # An invalid request was never processed — recording it would also
            # crash on whichever required field it is missing (e.g. no vendor).
            self.memory.record(req, decision["outcome"])
        state["final"] = {
            "id": req["id"],
            "decision": decision["outcome"],
            "escalate_to": decision.get("escalate_to"),
            "grounded": decision.get("grounded", True),
            "citations": [r["citation"] for r in decision.get("reasons", [])
                          if r.get("citation")],
            "guard_flags": state.get("guard_flags", []),
            "guard_tripped": decision.get("guard_tripped", False),
            "context_receipt": state.get("context_receipt"),
            "po_number": decision.get("po_number"),
        }
        return state

    # -- graph ---------------------------------------------------------------

    def _build(self) -> StateGraph:
        g = StateGraph(entry="intake")
        g.add_node("intake", self._intake)
        g.add_conditional_edges(
            "intake", lambda s: "finalize" if s["decision"] else "enrich")
        g.add_node("enrich", self._enrich,
                   retry=RetryPolicy(max_attempts=3, retry_on=(ToolTransientError,)))
        g.add_edge("enrich", "retrieve")
        g.add_node("retrieve", self._retrieve)
        g.add_edge("retrieve", "assemble")
        g.add_node("assemble", self._assemble)
        g.add_edge("assemble", "decide")
        g.add_node("decide", self._decide)
        g.add_conditional_edges("decide", self._route_decide)
        g.add_node("expand", self._expand)
        g.add_edge("expand", "retrieve")
        g.add_node("guard", self._guard)
        g.add_conditional_edges(
            "guard", lambda s: ("human_gate" if s["decision"]["outcome"] == "escalate"
                                else "finalize"))
        g.add_node("human_gate", self._human_gate)
        g.add_edge("human_gate", "finalize")
        g.add_node("finalize", self._finalize)
        g.add_edge("finalize", END)
        return g

    # -- public API ----------------------------------------------------------

    def process(self, request: dict, checkpoint_path: str, tracer=None) -> dict:
        """Run one request to completion or to the human gate. Returns the
        final summary; for interrupted runs the escalation IS the answer."""
        self._tracer = tracer
        cp = Checkpointer(checkpoint_path)
        result = self.graph.run({"request": request, "expanded": False},
                                checkpointer=cp, tracer=tracer)
        if result["status"] == "interrupted":
            d = result["payload"]["decision"]
            paused = cp.last()["state"]
            return {"id": request["id"], "decision": d["outcome"],
                    "escalate_to": d.get("escalate_to"),
                    "grounded": d.get("grounded", True),
                    "citations": [r["citation"] for r in d.get("reasons", [])
                                  if r.get("citation")],
                    "guard_flags": paused.get("guard_flags", []),
                    "guard_tripped": d.get("guard_tripped", False),
                    "context_receipt": paused.get("context_receipt"),
                    "status": "awaiting_human", "gate_reason": result["reason"]}
        return result["state"]["final"]

    def resume(self, checkpoint_path: str, human_input: dict, tracer=None) -> dict:
        """Continue a paused run with a human verdict, e.g. {"action": "approve"}."""
        self._tracer = tracer
        cp = Checkpointer(checkpoint_path)
        result = self.graph.run({}, checkpointer=cp, tracer=tracer,
                                resume=Command(resume=human_input))
        return result["state"]["final"]
