#!/usr/bin/env python3
"""tools — a schema-validated, permissioned, idempotent tool registry.

The 2026 tool-calling reliability canon, in stdlib: arguments are validated
against a declared schema and rejected with a *repair-friendly* error naming
the exact field (so a model could fix and retry); side-effecting tools are
permission-gated and only run with explicit human approval; idempotency keys
make accidental double-calls safe; every call — success or failure — lands
in the trace.
"""
from __future__ import annotations

import hashlib
import json
import os


class ToolError(Exception):
    pass


class ToolTransientError(ToolError):
    """Retryable infrastructure failure (timeouts, flaky backends)."""


class PermissionRequired(ToolError):
    """A gated tool was called without human approval. By design, not retryable."""


class Tool:
    def __init__(self, name: str, description: str, params: dict, fn,
                 permission: str = "auto"):
        assert permission in ("auto", "gated")
        self.name, self.description = name, description
        self.params = params  # {arg_name: python type}
        self.fn = fn
        self.permission = permission


class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, Tool] = {}
        self._idempotency_cache: dict[tuple, dict] = {}

    def register(self, tool: Tool):
        self._tools[tool.name] = tool
        return self

    def list(self) -> list[dict]:
        return [{"name": t.name, "description": t.description,
                 "permission": t.permission,
                 "params": {k: v.__name__ for k, v in t.params.items()}}
                for t in self._tools.values()]

    def _validate(self, tool: Tool, args: dict):
        missing = sorted(set(tool.params) - set(args))
        unexpected = sorted(set(args) - set(tool.params))
        if missing:
            raise ToolError(f"{tool.name}: missing required arg(s) {missing}")
        if unexpected:
            raise ToolError(f"{tool.name}: unexpected arg(s) {unexpected}")
        for k, typ in tool.params.items():
            if not isinstance(args[k], typ):
                raise ToolError(
                    f"{tool.name}: arg '{k}' must be {typ.__name__}, "
                    f"got {type(args[k]).__name__}")

    def call(self, name: str, args: dict, tracer=None, human_approved: bool = False,
             idempotency_key: str | None = None) -> dict:
        event = {"kind": "tool_call", "tool": name, "args": args, "ok": False,
                 "cached": False}
        try:
            tool = self._tools.get(name)
            if tool is None:
                raise ToolError(f"unknown tool '{name}'; available: "
                                f"{sorted(self._tools)}")
            self._validate(tool, args)
            if tool.permission == "gated" and not human_approved:
                raise PermissionRequired(
                    f"{name} is gated — it only runs with explicit human approval")
            cache_key = (name, idempotency_key) if idempotency_key else None
            if cache_key and cache_key in self._idempotency_cache:
                event.update(ok=True, cached=True)
                return self._idempotency_cache[cache_key]
            result = tool.fn(**args)
            if cache_key:
                self._idempotency_cache[cache_key] = result
            event["ok"] = True
            return result
        except ToolError as e:
            event["error"] = str(e)
            raise
        finally:
            if tracer:
                tracer(event)


def build_registry(data_dir: str) -> ToolRegistry:
    """The take-home's three tools: two read-only lookups (auto) and one
    side-effecting PO issuer (gated — an agent may never call it alone)."""
    with open(os.path.join(data_dir, "vendors.json"), encoding="utf-8") as f:
        vendors = json.load(f)
    with open(os.path.join(data_dir, "software-catalog.json"), encoding="utf-8") as f:
        catalog = json.load(f)

    def vendor_risk_lookup(vendor: str) -> dict:
        rec = vendors.get(vendor)
        if rec is None:
            return {"known": False, "tier": None, "dpa_on_file": False, "soc2": False}
        return {"known": True, **rec}

    def software_catalog_lookup(vendor: str) -> dict:
        return {"approved": vendor in catalog["approved"]}

    def create_purchase_order(request_id: str, vendor: str, amount_usd: int) -> dict:
        digest = hashlib.sha1(f"{request_id}:{vendor}:{amount_usd}".encode()).hexdigest()
        return {"po_number": f"PO-{digest[:8].upper()}"}

    reg = ToolRegistry()
    reg.register(Tool("vendor_risk_lookup", "Vendor master: risk tier, DPA, SOC 2.",
                      {"vendor": str}, vendor_risk_lookup))
    reg.register(Tool("software_catalog_lookup", "Is this product on the approved list?",
                      {"vendor": str}, software_catalog_lookup))
    reg.register(Tool("create_purchase_order", "Issue a purchase order (side effect).",
                      {"request_id": str, "vendor": str, "amount_usd": int},
                      create_purchase_order, permission="gated"))
    return reg
