# The COLLECT stage — sources behind one seam

`match_engine.py` needs **SUPPLY** (people + skills + availability + vetting evidence) and
**DEMAND** (teams + milestones + open roles). `collectors.py` builds both behind one interface,
so the demo runs on CSV today and the same match/recommend code runs on live enterprise data
tomorrow — nothing downstream changes.

```
sources ──▶ Collector.collect() ──▶ SUPPLY / DEMAND ──▶ match_engine.plan()
 CSV / Forms (now)                   (plain dicts)
 MyScheduling / Workday (v2)
```

## Working now

```bash
# DEMAND from a CSV (team, milestone, role_id, role_type, skills, count)
python3 collectors.py demand --csv examples/demand.csv > demand.json

# SUPPLY from a roster CSV (id, skills, available) + per-person vetting records
#   (candidates/<id>.json = the scorecard evidence from scorecard.py / forms_to_candidate.py)
python3 collectors.py supply --roster examples/roster.csv --candidates examples/candidates > supply.json

python3 match_engine.py plan --supply supply.json --demand demand.json
```

A roster row with **no** vetting record collects **empty** evidence — so the gate honestly marks
that person un-vetted (conditional/unmatched) instead of silently passing them.

## v2 — enterprise connectors (documented stubs, they raise until wired)

Same seam, one body per source. They exist as stubs so nothing fakes a data source.

| Connector | Reads (when wired) | Honesty rule |
|---|---|---|
| `MySchedulingCollector` | current assignment, roll-off date, chargeability → `available` + free-from date | prefer the **observed** booking (actual scheduled hours) over self-reported status |
| `WorkdayCollector` | talent-profile validated skills + stored delivery references | map a **client-team reference → a `vouch`**; never a self-asserted skill → a pass |

Both need SSO + the respective API scope (no scraping; GDPR-safe for EU/life-sciences data). The
posture matches the gate: **prefer observed evidence over claimed** — a real MyScheduling booking
beats "available: yes"; a Workday client reference beats a resume skill list.

## Why a seam and not a script

The whole loop (match → recommend → confirm) is written against the SUPPLY/DEMAND dicts, not
against CSV. Swapping in the Workday connector is a new `Collector` subclass — zero change to the
matcher, the scorecard gate, or the cockpit. That's what makes "demo on CSV Friday, run on live
data next quarter" a config change, not a rewrite.
