# portfolio-trust — the missing link for agentic portfolios (Vercel)

A self-authored portfolio proves *what you built*, but it **can't attest reliability** and, at
scale, collapses into a prettier resume. This enforces the missing evidence in the artifact itself:
**provenance + a CI-verified badge + non-self-issuable signed vouches**, read into a GO / NO-GO by
the same gate as the FDE-os scorecard. See [`SPEC.md`](SPEC.md). No LLM — deterministic, reliable.

- `api/vouch.js` — a *different* person signs a structured reference → a tamper-evident token (rejects self-vouch).
- `api/verify.js` — recompute the HMAC → valid / self_issued / tampered.
- `api/ingest.js` — read a portfolio's agent-card → verify attestations + provenance + CI → candidate + GO/NO-GO.
- `index.html` — check a portfolio, or mint a vouch.
- `agent-card.example.json` — the evidence extension (2 CI-verified projects, empty attestations → NO-GO on reliability until a real vouch is added).

## Deploy
```bash
cd portfolio-trust
vercel --prod --yes --scope <team>

# production trust needs a signing secret (else responses are flagged dev_secret:true):
SECRET=$(openssl rand -hex 32)
printf '%s' "$SECRET" | vercel env add VOUCH_SECRET production --scope <team>
vercel --prod --scope <team>          # redeploy to pick it up
```

## Verify locally
```bash
# sign→verify→tamper→self-issued + the ingest gate (portfolio w/o vouch = NO-GO; with a valid vouch = GO)
node <harness>   # 11 checks, all deterministic, no network
```
