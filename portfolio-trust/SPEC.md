# Portfolio trust layer — spec

## The problem it closes
An agentic portfolio proves *what you built* (bottom-up, good) but is **self-authored and
point-in-time**, so at scale it collapses toward a prettier resume and it **cannot attest
reliability** — the one thing that burns a recommender. The missing link is to move each of the
three signals from **claimed → observed / attested**, and to *enforce* that in the artifact itself.

## Three enforced primitives

1. **Provenance** (fixes "how much did they contribute?") — per project: `contribution_pct`,
   `commits`, first/last commit. Owned = real authorship over time, not a linked repo.
2. **CI-verified** (fixes "a repo exists ≠ it works") — per project: `verified:true` only when a
   reproducible eval/test run passed. A badge earned by a green run, not a checkbox.
3. **Signed vouches** (the reliability primitive) — a **different** verified person signs a
   structured reference. Server-signed (HMAC), so it is **tamper-evident** (edit any field → the
   signature breaks) and **non-self-issuable** (voucher ≠ subject, enforced + flagged on verify).

## The agent-card evidence extension
Add to `.well-known/agent-card.json`:
```json
{ "name": "...", "evidence": {
    "projects": [ { "name","repo",
      "provenance": {"contribution_pct","commits","first_commit","last_commit"},
      "verified": true } ],
    "attestations": [ "<signed vouch token from /api/vouch>" ] } }
```

## Endpoints (`/api`)
- `POST /api/vouch`  {subject, voucher, relationship, worked_with, would_staff_again, went_dark_or_noshow, engagement} → **rejects self-vouch**, returns a signed `token`.
- `POST /api/verify` {token} → {valid, self_issued, payload} (recomputes the HMAC).
- `POST /api/ingest` {card_url | card} → verifies attestations, reads provenance + CI, emits a
  **scorecard-compatible `candidate` + a GO / NO-GO**. Only *valid, non-self-issued* vouches count;
  any went-dark attestation is an automatic NO-GO; a portfolio with projects but no vouch is
  NO-GO on reliability — by design.

## Honesty / mapping (same discipline as the FDE-os scorecard)
| criterion | passes only when | tier |
|---|---|---|
| reliability | ≥1 valid non-self-issued vouch, would-staff-again, zero dark flags | vouch |
| technical | ≥1 CI-`verified` project | observed |
| resourcefulness | ≥1 owned project with real commit provenance | observed |

## Security notes (prototype honesty)
- HMAC secret = `VOUCH_SECRET` (Vercel env). Without it, a dev secret is used and every response is
  flagged `dev_secret:true` (not production-trustworthy).
- The signature proves *server-issued + integrity + voucher≠subject + timestamp*. It does **not**
  yet prove the voucher is a distinct real human — production would bind the voucher to an OAuth
  identity (GitHub / org SSO) before signing. That's the one gap between this prototype and trust.
