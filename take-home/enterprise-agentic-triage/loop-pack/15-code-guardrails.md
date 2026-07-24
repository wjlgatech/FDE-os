# Source: take-home/enterprise-agentic-triage/scripts/guardrails.py

```python
#!/usr/bin/env python3
"""guardrails — deterministic hard rules layered around the reasoner.

Three guards, three different failure modes:

1. Input validation — a malformed request is rejected before any reasoning
   happens (policy §2: missing fields ⇒ invalid, never processed).
2. Instruction hygiene — free-text fields are data, not instructions
   (data-privacy addendum). Injection attempts are flagged into the trace
   but NEVER change the decision: acting on them would be the vulnerability,
   and silently dropping them would hide the attack from the audit trail.
3. Monotonic severity — hard rules evaluated on tool facts alone (no
   retrieval in the loop) can only make the outcome STRICTER, never looser.
   If retrieval fails or the reasoner is wrong in the permissive direction,
   the floor catches it; a guard that could loosen outcomes would be a
   second attack surface instead of a defense.
"""
from __future__ import annotations

import re

from reasoner import SEVERITY

REQUIRED_FIELDS = ("id", "date", "requester", "role", "vendor", "category",
                   "description")

_INJECTION_PATTERNS = [
    r"ignore (all|any|previous|the) .{0,40}(polic|instruction|check|rule)",
    r"approve (this |it )?immediately",
    r"disregard .{0,40}(polic|instruction|check|rule)",
    r"you are now|new instructions:",
]


def validate_request(raw: dict) -> list[str]:
    errors = [f"missing required field '{f}'" for f in REQUIRED_FIELDS
              if not raw.get(f)]
    amount = raw.get("amount_usd")
    if amount is None:
        errors.append("missing required field 'amount_usd'")
    elif not isinstance(amount, (int, float)) or isinstance(amount, bool) or amount <= 0:
        errors.append("'amount_usd' must be a positive number")
    return errors


def scan_injection(text: str) -> list[str]:
    lowered = text.lower()
    return [p for p in _INJECTION_PATTERNS if re.search(p, lowered)]


# Hard floors: enforced on structured facts only (request fields + tool
# results), independent of what retrieval surfaced. Duplicating the two
# highest-blast-radius rules here is defense in depth, not redundancy.
HARD_COMMITTEE_FLOOR = 250_000


def hard_floor(request: dict, vendor_fact: dict) -> str | None:
    if vendor_fact.get("tier") == "Prohibited":
        return "deny"
    if request["amount_usd"] > HARD_COMMITTEE_FLOOR:
        return "escalate"
    return None


def apply_monotonic(reasoner_outcome: str, floor_outcome: str | None) -> tuple[str, bool]:
    """Final outcome is the max severity of the two. Returns (outcome, tripped)
    where tripped=True means the hard floor was STRICTER than the reasoner —
    i.e. the guard did real work and the trace should say so."""
    if floor_outcome is None:
        return reasoner_outcome, False
    final = max(reasoner_outcome, floor_outcome, key=lambda o: SEVERITY[o])
    return final, SEVERITY[floor_outcome] > SEVERITY[reasoner_outcome]

```
