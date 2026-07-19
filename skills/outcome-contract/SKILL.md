---
name: outcome-contract
description: Encode an FDE engagement's success as a machine-scoreable outcome contract (baseline → target → measured evidence → GO/NO-GO), then gate on it deterministically. Use at engagement kickoff to turn "the client wants the outcome" into data, and at every checkpoint to report honestly whether the outcomes are measured and met. The engagement-level sibling of true-scorer (artifact quality) and rag-eval-harness (retrieval quality): no evidence ⇒ No; claimed ≠ measured; the gate cannot pass on unmeasured items. Offline, stdlib, CI-able (exit 0 GO / 2 NO-GO / 1 malformed).
---

# outcome-contract

> The Outcome-Based Model, made runnable: clients pay for the **result** (time saved, calls
> answered, orders taken), not the software license. That only works if the outcomes are encoded
> as **data** and gated on **evidence** — otherwise "outcome-based" is a pricing slide, not a
> mechanism. Derived from the FDE talk audit
> ([field note](../../docs/field-notes/2026-07-17-fde-talk-audit.md)).

## Why this exists (the verified gap)

FDE-os had three artifact-level gates (`true-scorer`, `criteria-scorer`, `rag-eval-harness`) and
**no engagement-level gate**. Nothing encoded "what does this engagement owe the client, and is
that measured?" — the exact mechanism the outcome-based model needs. This fills that gap and
nothing more.

## The contract (data, not prose)

```json
{
  "engagement": "acme-hotel-ai-receptionist",
  "outcomes": [
    {
      "id": "call-answer-rate",
      "statement": "AI receptionist answers calls without human handoff",
      "metric": "answered_without_handoff_pct",
      "baseline": 0,
      "target": 60,
      "direction": ">=",
      "blocking": true,
      "evidence": {"kind": "measured", "value": 72.5, "source": "https://.../dashboard-export.csv"}
    }
  ]
}
```

## The honesty rules (the whole point)

- **PASS needs measured evidence meeting the target.** Nothing else passes.
- **Claimed never passes.** A number without an independent source is reported (`~ CLAIMED`) but
  never counts — prefer observed over claimed. Measured-without-source is downgraded to claimed,
  loudly.
- **No evidence ⇒ NOT_MEASURED** — excluded, never a fake pass.
- **The gate cannot pass on unmeasured items.** GO iff every `blocking` outcome is a measured
  PASS. Advisory (`"blocking": false`) outcomes inform, never gate.
- **Malformed contracts fail loudly** (exit 1), never silently skip.

## Run it

```bash
python3 skills/outcome-contract/scripts/outcome_score.py score examples/acme-receptionist.json
python3 skills/outcome-contract/scripts/outcome_score.py score contract.json --json   # machine-readable
```

Exit codes gate CI: `0` GO · `2` NO-GO · `1` malformed.

## Boundaries (honest edges)

- **It scores the contract; it doesn't collect the measurements.** Wiring evidence values from a
  dashboard/telemetry export is the engagement's job (an `EvidenceCollector` seam, per the BRACE
  pattern) — this core stays offline and deterministic.
- **It can't detect a gamed metric.** If the target is wrong (answer-rate up, satisfaction down),
  that's a contract-design failure; pair a blocking outcome with an advisory counter-metric.
- Money/pricing is out of scope — this gates *delivery truth*, not invoicing.

## Verify

```bash
python3 -m pytest skills/outcome-contract/tests -q
```
