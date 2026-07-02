# partner-trust-ledger — the anti-resume, as a gate

Companion to [`coding-drill-kit`](../coding-drill-kit/): **eval-as-gate applied to a human** —
but where the drill proves you can *code*, this proves a hiring partner can **stake their
reputation on you**.

## Why this exists

The lesson came from a real conversation with a senior AI/data lead sourcing FDEs (details
private; the *rubric* is the reusable asset). She had been burned once: recommended someone who
was strong on paper, who then flopped — and the blast radius wasn't just her, it was her whole
team's ability to recommend anyone again. So she now decides on **evidence, not resumes**, and she
said the hierarchy out loud:

> Don't trust the resume. Trust what they already built. Trust *most* the client team who says
> *"without you, we're not running."*

That is the same posture FDE-os already enforces on artifacts (`true-scorer`'s AND-gate,
`rag-eval-harness`'s "no evidence ⇒ no pass"). This tool points it at a **person**.

## The four axes a partner actually evaluates

| Axis | What it means | Evidence that counts |
|---|---|---|
| `technical_competence` | deep, hands-on build ability (Python + agent building) | a shipped thing they can open |
| `reliability` | you show up and do what you said | milestones hit on the date you named |
| `learning_agility` | learn a new tool in a day, teach it back | a demo of a tool you didn't know last week |
| `validated_reputation` | a named human who worked with you attests | a reachable reference — the gold tier |

## Evidence tiers (you don't rate yourself — your evidence does)

```
vouch    (3)  a named person who worked with you attests   ← the only thing that clears reputation
artifact (2)  a verifiable shipped thing (repo, live app, demo)
claimed  (1)  self-report / resume only
none     (0)  asserted with nothing behind it
```

A dimension's tier is its **strongest** evidence — one "without you we don't run" outweighs ten
claims. Two independent vouches raise a `⟳ pattern` flag, because one great outcome can be an
accident and a pattern cannot.

## The gate (hard, AND-style)

1. **No axis may rest on `claimed`/`none`** → every axis must reach `artifact`. *No evidence ⇒ No.*
2. **`validated_reputation` must carry a `vouch`** → an artifact is not a person.

`GO` only if 1 **and** 2 — a strong total never rescues one weak axis (same discipline as
`true-scorer`).

## Run it

```bash
cd course/prep/tools/partner-trust-ledger

python3 trust_ledger.py template > my-ledger.json   # blank to fill in (gitignored)
# fill each axis with real claims + honest evidence tiers, then:
python3 trust_ledger.py score my-ledger.json         # → per-axis tier + GO / NO-GO
python3 trust_ledger.py score my-ledger.json --json  # machine-readable, exits non-zero on NO-GO
```

See [`ledger.example.json`](ledger.example.json) for a filled, name-free example.

**Use it as a mirror before an intro call:** if your ledger is `NO-GO`, you are not ready to ask
someone to stake their name on you — the blockers name exactly what to go earn first (usually:
turn a `claimed` into an `artifact`, or line up a real `vouch`). If it's `GO`, lead the
conversation with the evidence, not the resume.

## Verify

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
```

Covers the gate exhaustively: full-evidence passes; reputation-without-vouch blocks; one weak axis
blocks despite strong others; claimed-only never passes; the pattern flag; unknown tier/dimension
are hard errors (never silent passes).

`my-ledger.json` is yours — gitignored, never committed.
