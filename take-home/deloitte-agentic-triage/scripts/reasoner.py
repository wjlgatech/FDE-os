#!/usr/bin/env python3
"""reasoner — the model seam: decisions grounded in retrieved policy text.

`Reasoner.decide(request, evidence)` is where an LLM would sit. The shipped
implementation is deterministic on purpose — the take-home grades the
machinery around the model, and a deterministic reasoner makes every other
layer testable to ground truth. Swap `PolicyReasoner` for an LLM-backed one
behind the same signature and nothing else changes.

The non-negotiable property either way: every threshold and rule is parsed
FROM the retrieved policy chunks, never hardcoded. Change the policy corpus
and the decisions change; fail to retrieve the governing clause and the
reasoner says so (grounded=False) instead of guessing — no evidence ⇒ No.
Each fired rule carries a Citation whose quote is verbatim-verifiable.
"""
from __future__ import annotations

import re
from datetime import date

from retrieval import Chunk, Citation, cite

SEVERITY = {"approve": 0, "escalate": 1, "deny": 2}

_ROLE_PLURAL = {"Manager": "Managers", "Director": "Directors",
                "Vice President": "Vice Presidents"}


class Decision:
    def __init__(self, outcome: str, reasons: list[dict], escalate_to: str | None,
                 grounded: bool):
        self.outcome = outcome
        self.reasons = reasons
        self.escalate_to = escalate_to
        self.grounded = grounded

    def as_dict(self) -> dict:
        return {"outcome": self.outcome, "escalate_to": self.escalate_to,
                "grounded": self.grounded, "reasons": self.reasons}


def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _sentence_of(text: str, pos: int) -> str:
    """The full sentence containing position `pos` — used as the citation quote."""
    starts = [m.end() for m in re.finditer(r"[.!?]\s", text[:pos])]
    start = starts[-1] if starts else 0
    m = re.search(r"[.!?]", text[pos:])
    end = pos + m.end() if m else len(text)
    return text[start:end].strip()


class PolicyReasoner:
    def decide(self, request: dict, evidence: dict) -> Decision:
        chunks: list[Chunk] = evidence["chunks"]
        vendor = evidence["tools"].get("vendor", {})
        catalog = evidence["tools"].get("catalog")
        cumulative = evidence["memory"].get("cumulative_spend", 0)
        amount = request["amount_usd"]
        is_software = request["category"] in ("software", "cloud")

        def find(pattern: str):
            for c in chunks:
                m = re.search(pattern, _norm(c.text))
                if m:
                    return c, m
            return None, None

        def reason(rule: str, chunk: Chunk, match) -> dict:
            quote = _sentence_of(_norm(chunk.text), match.start())
            return {"rule": rule, "citation": cite(chunk, quote).as_dict()}

        reasons: list[dict] = []
        escalations: list[str] = []
        ungrounded: list[str] = []

        def fire(rule: str, target: str | None, outcome: str, pattern: str):
            chunk, m = find(pattern)
            if chunk is None:
                ungrounded.append(rule)  # the fact fired but the clause wasn't retrieved
                return
            reasons.append(reason(rule, chunk, m))
            if outcome == "escalate" and target:
                escalations.append(target)
            outcomes.append(outcome)

        outcomes: list[str] = []

        if vendor.get("tier") == "Prohibited":
            fire("prohibited-vendor", None, "deny",
                 r"Purchases from Prohibited vendors must be denied")
        if not vendor.get("known"):
            fire("unknown-vendor", "vendor-onboarding", "escalate",
                 r"unknown vendors must be escalated for vendor onboarding")
        if vendor.get("tier") == "High-Risk":
            fire("high-risk-vendor", "third-party-risk", "escalate",
                 r"escalated to Third-Party Risk Management")
        if request.get("processes_pii") and not vendor.get("dpa_on_file"):
            fire("pii-without-dpa", "privacy-office", "escalate",
                 r"If no DPA is on file, the request must be escalated to the Privacy Office")
        if is_software and catalog is not None and not catalog.get("approved"):
            fire("software-not-approved", "enterprise-architecture", "escalate",
                 r"requests for unlisted products must be escalated to Enterprise Architecture")
        if is_software:
            threshold, chunk, m = self._software_threshold(chunks, request["date"])
            if threshold is None:
                ungrounded.append("software-threshold")
            elif amount > threshold:
                reasons.append(reason("software-cto-approval", chunk, m))
                escalations.append("cto")
                outcomes.append("escalate")

        committee, c_chunk, c_m = self._parse_amount(
            chunks, r"above \$([\d,]+) must be referred to the Spend Committee")
        role_limit, r_chunk, r_m = self._parse_amount(
            chunks, _ROLE_PLURAL.get(request["role"], request["role"])
            + r"s?: up to and including \$([\d,]+)")

        if committee is not None and amount > committee:
            reasons.append(reason("spend-committee", c_chunk, c_m))
            escalations.append("spend-committee")
            outcomes.append("escalate")
        elif committee is None:
            ungrounded.append("committee-threshold")

        if role_limit is None:
            ungrounded.append("role-limit")
        elif amount + cumulative > role_limit:
            rule = ("cumulative-over-limit" if amount <= role_limit
                    else "over-role-limit")
            reasons.append(reason(rule, r_chunk, r_m))
            escalations.append("authority-chain")
            outcomes.append("escalate")

        # Policy §3: competitive bids above a threshold, Preferred tier exempt.
        # Checked last so authority/committee outrank it as the escalation target.
        if vendor.get("tier") != "Preferred" and not request.get("bids_on_file"):
            bids_limit, b_chunk, b_m = self._parse_amount(
                chunks, r"above \$([\d,]+) require evidence of at least two "
                        r"competitive bids")
            if bids_limit is None:
                ungrounded.append("bids-threshold")
            elif amount > bids_limit:
                reasons.append(reason("competitive-bids-missing", b_chunk, b_m))
                escalations.append("competitive-bids")
                outcomes.append("escalate")

        if ungrounded:
            # A governing clause could not be found in the retrieved evidence.
            # Guessing here is how ungrounded approvals happen — refuse instead.
            return Decision("escalate", reasons, "insufficient-grounding",
                            grounded=False)

        if not outcomes:
            reasons.append(reason("within-role-limit", r_chunk, r_m))
            return Decision("approve", reasons, None, grounded=True)

        final = max(outcomes, key=lambda o: SEVERITY[o])
        target = escalations[0] if final == "escalate" and escalations else None
        return Decision(final, reasons, target, grounded=True)

    @staticmethod
    def _parse_amount(chunks: list[Chunk], pattern: str):
        for c in chunks:
            m = re.search(pattern, _norm(c.text))
            if m:
                return int(m.group(1).replace(",", "")), c, m
        return None, None, None

    @staticmethod
    def _software_threshold(chunks: list[Chunk], request_date: str):
        """Resolve the v3-vs-v4 conflict by effective date: among retrieved
        chunks stating a software threshold, the latest one already effective
        on the request date governs. The supersede lives in the corpus; the
        reasoner only applies it."""
        req = date.fromisoformat(request_date)
        best = (None, None, None, None)  # effective, threshold, chunk, match
        for c in chunks:
            m = re.search(r"Software purchases above \$([\d,]+)", _norm(c.text))
            if not m or c.effective_date is None:
                continue
            eff = date.fromisoformat(c.effective_date)
            if eff <= req and (best[0] is None or eff > best[0]):
                best = (eff, int(m.group(1).replace(",", "")), c, m)
        return best[1], best[2], best[3]
