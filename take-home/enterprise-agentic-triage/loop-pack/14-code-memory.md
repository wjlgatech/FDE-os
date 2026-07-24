# Source: take-home/enterprise-agentic-triage/scripts/memory.py

```python
#!/usr/bin/env python3
"""memory — session memory and token-budgeted context assembly, with receipts.

Two halves of the JD's "memory and context management" term:

SessionMemory is the state that outlives a single request — per-vendor
decision history that lets the agent catch split purchasing (requests that
are individually fine but cumulatively over a limit). One request at a time,
the rule is invisible; memory is what makes it enforceable.

ContextAssembler is context engineering made measurable: candidate items
compete for a fixed token budget, pinned items always survive, and the
assembler emits a receipt of exactly what was included and what was dropped.
Context rot is the reason the budget exists; the receipt is what makes the
trade-off auditable instead of vibes.
"""
from __future__ import annotations

from datetime import date


class SessionMemory:
    def __init__(self):
        self.vendor_history: dict[str, list[dict]] = {}

    def record(self, request: dict, outcome: str) -> None:
        self.vendor_history.setdefault(request["vendor"], []).append({
            "request_id": request["id"],
            "amount_usd": request.get("amount_usd", 0),
            "date": request["date"],
            "outcome": outcome,
        })

    def cumulative_vendor_spend(self, vendor: str, on_date: str,
                                window_days: int = 30) -> int:
        """Approved spend with this vendor inside the rolling window.
        Approved-only: escalated/denied requests never became spend."""
        ref = date.fromisoformat(on_date)
        total = 0
        for rec in self.vendor_history.get(vendor, []):
            delta = (ref - date.fromisoformat(rec["date"])).days
            if 0 <= delta <= window_days and rec["outcome"] == "approve":
                total += rec["amount_usd"]
        return total

    def vendor_summary(self, vendor: str) -> str:
        recs = self.vendor_history.get(vendor, [])
        if not recs:
            return f"No prior requests for {vendor} this session."
        parts = [f"{r['request_id']}: ${r['amount_usd']:,} → {r['outcome']}"
                 for r in recs]
        return f"Prior requests for {vendor}: " + "; ".join(parts)


def _est_tokens(text: str) -> int:
    # Honest approximation: whitespace words ≈ tokens within ~30% on English
    # prose. Good enough to enforce a budget; swap in a real tokenizer at the
    # seam if exactness ever matters.
    return len(text.split())


class ContextItem:
    def __init__(self, kind: str, text: str, priority: int = 0, pinned: bool = False):
        self.kind, self.text, self.priority, self.pinned = kind, text, priority, pinned
        self.tokens = _est_tokens(text)


class ContextAssembler:
    def __init__(self, budget_tokens: int = 350):
        self.budget = budget_tokens

    def assemble(self, items: list[ContextItem]) -> tuple[list[ContextItem], dict]:
        """Greedy fill: pinned first (always in, even over budget — a pinned
        overflow is a design bug the receipt makes visible), then by priority.
        Returns (included, receipt)."""
        included: list[ContextItem] = []
        excluded: list[ContextItem] = []
        used = 0
        for item in [i for i in items if i.pinned]:
            included.append(item)
            used += item.tokens
        for item in sorted([i for i in items if not i.pinned],
                           key=lambda i: -i.priority):
            if used + item.tokens <= self.budget:
                included.append(item)
                used += item.tokens
            else:
                excluded.append(item)
        receipt = {
            "budget_tokens": self.budget,
            "used_tokens": used,
            "over_budget": used > self.budget,
            "included": [{"kind": i.kind, "tokens": i.tokens} for i in included],
            "excluded": [{"kind": i.kind, "tokens": i.tokens} for i in excluded],
        }
        return included, receipt

```
