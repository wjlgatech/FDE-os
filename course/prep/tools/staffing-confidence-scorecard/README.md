# staffing-confidence-scorecard — eval-as-gate, pointed at a hire

The org-scale sibling of [`coding-drill-kit`](../coding-drill-kit/) (eval pointed at
*your own* coding) and [`partner-trust-ledger`](../partner-trust-ledger/) (the
anti-resume for *yourself*). This one points the same evidence gate at a
**candidate you're about to recommend** — so an AI delivery org can vet on
evidence instead of gut, and a good recommendation becomes defensible instead of
a coin-flip.

## The pain (from a real AI-delivery lead)

> "I recommended someone who looked great on paper. They no-showed, went dark,
> didn't deliver. Now my *whole team's* credibility is spent — next time I
> recommend anyone, they say *'I don't want anybody from that team.'*"

Resumes don't catch this. Neither does "will you be a reference?" — the answer is
always yes. Three criteria actually decide whether staffing someone builds or
burns your credibility, and she named them in order:

1. **Reliable** — shows up, does what they said, communicates, reachable, delivers.
2. **Technical competence** — hands-on build ability (reliable-but-can't-build is useless for a technical role).
3. **Resourcefulness / learning agility** — learns a new tool in a day and *teaches it*.

## Why these three instruments (not a longer interview)

85 years of selection research (Schmidt & Hunter, 1998) is blunt: **work samples
and _structured_ references are top-tier predictors (r≈.5+); unstructured reference
checks are near-noise (~.26).** The lever is *structure*, not more conversation. So
each criterion gets the highest-validity instrument for it, and nothing else:

| Criterion | Instrument | Why it's the right one |
|---|---|---|
| reliability | [Structured Reference Protocol](instruments/reliability-reference.md) | structured refs predict; a single "went dark" is disqualifying |
| technical_competence | [Observed Work Sample](instruments/technical-work-sample.md) | #1 predictor; *observed* answers "how much was really them?" |
| resourcefulness | [Learn-and-Teach-Back](instruments/resourcefulness-teachback.md) | her own test, formalized; measures learn-a-tool-in-a-day |

## The gate (role-aware, AND-style)

```bash
python3 scorecard.py template > cand.json     # fill from the 3 instruments (anonymized id)
python3 scorecard.py score cand.json          # → per-axis GO/NO-GO + the named gap
python3 scorecard.py score cand.json --json   # machine-readable; exits non-zero on NO-GO
```

- **reliability** is a hard gate for *every* role — one credible "went dark / no-show" is an automatic NO-GO. It is never averaged away.
- **technical_competence** is a hard gate for technical roles (informational for non-technical ones).
- **resourcefulness** is a hard gate for every role — the work is constant tool-learning.
- **GO only if every required axis clears on real evidence** (a vouch from someone who worked with them; an *observed* work sample; a *working* teach-back). No evidence ⇒ No. A strong axis never rescues a weak one.

See [`candidate.example.json`](candidate.example.json) for a filled GO record.

**Bulk path (no hand-editing JSON)** — export each of the three Forms to CSV, then let
[`forms_to_candidate.py`](forms_to_candidate.py) build the record (columns matched by keyword,
missing column = hard error, never a silent wrong answer):

```bash
python3 forms_to_candidate.py merge \
    --refs reference.csv --tech worksample.csv --teach teachback.csv \
    --id anon-0042 --role technical | python3 scorecard.py score -
```

Runnable example CSVs are in [`examples/`](examples/). At 100-person scale: one loop over the
export rows → a GO/NO-GO board for the whole pipeline.

## Deploy it THIS WEEK on the stack you already have (zero procurement)

No new platform — it lives in Microsoft 365 + Workday + this 200-line script. Paste-ready
assets are in [`rollout/`](rollout/): three Microsoft Forms sheets
([`rollout/forms/`](rollout/forms/), each with its exact answer→scorer mapping so nothing drifts)
and a one-page [`rollout/leave-behind.md`](rollout/leave-behind.md).

- **Mon** — paste the 3 instrument question sets into **Microsoft Forms** (one form each). Drop this folder in the team **SharePoint/Teams** channel.
- **Tue** — dry-run on 2–3 candidates already in the pipeline; a reviewer fills `cand.json` from the form responses and runs `scorecard.py`.
- **Wed** — calibrate one number: the work-sample `threshold` per role. That's the only knob.
- **Thu** — run a *real* staffing decision through it end-to-end; attach the one-page scorecard to the candidate's **Workday** profile (where references already live) and to the **MyScheduling** staffing note.
- **Fri** — the ~100-person center adopts the identical funnel. Every recommendation now ships with a dossier, not a vibe. Roll-up: `for f in *.json; do python3 scorecard.py score "$f" --json; done` → a GO/NO-GO board across the pipeline.

**Wedge, then scale:** it's the same reusable gate an org needs for a portfolio-wide
agent-tool enablement — vet the *enablers* before they teach citizen developers across many
companies, with the exact `resourcefulness` instrument the tool rollout already requires.

## Fair, defensible, compliant by construction

- **Behavior + evidence only** — no protected attributes, no personal questions; identical questions for every candidate. Structure is what makes it *both* higher-validity *and* less biased.
- **Anonymized ids only in this repo** — real names/PII stay in Workday, never in a JSON here.
- **Sanctioned tools only** — Forms/SharePoint/Workday. No scraping; GDPR-safe for EU/life-sciences data.
- It **advises a human decision** — it produces a defensible scorecard and names the gap; the recommender still signs.

## Verify

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
```

14 tests: full-evidence GO; a single dark-flag is automatic NO-GO; no-reference / would-not-staff-again block; internal vs client vouch both count; unobserved or below-bar work sample blocks a technical role but is informational for a non-technical one (her "reliable-but-no-tech is useless *for these roles*"); made-it-work-but-can't-teach blocks; the pattern flag needs two vouches; bad role_type is a hard error.

_Sources for the validity claims: Schmidt & Hunter (1998), "The Validity and Utility
of Selection Methods in Personnel Psychology," Psychological Bulletin 124(2)._
