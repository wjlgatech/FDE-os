# Take-home #2: SEC Filing Intelligence

Natural-language financial questions over **real SEC filings treated as PDFs** (the
assignment's constraint: the archive is PDF, EDGAR API is scarce). Grounded answers with
verbatim quotes, page anchors, deterministic arithmetic, and refusal as a first-class
outcome.

**Corpus (real, provenance-pinned):** Tesla 10-K FY2025 · Tesla 10-Q Q1-2026 · Tesla 10-Q
Q2-2026 (filed 2026-07-23) · Apple 10-K FY2025 — fetched with a documented 6-call EDGAR
budget (`scripts/fetch_filings.py`), printed to PDF, extracted with `pdftotext -layout`
into page-anchored JSON (`corpus/extracted/`, PDF SHA256 pinned). CI is fully offline.

## Run it

```bash
python3 scripts/qa.py "What was Apple's total revenue in 2025?"
python3 scripts/eval_sec.py      # 26 hand-verified golden cases; 4 gates, all 1.0; exit 0/2
python3 scripts/reconcile.py     # cross-filing identities on real data; exit 0/2
python3 -m unittest discover -s tests -p 'test_*.py'
```

**Scoreboard:** answer_accuracy **1.0** · refusal_recall **1.0** (unanswerable questions —
including the assignment's own "growth between 2025 and 2026" — must refuse) ·
refusal_precision **1.0** (answerable questions must not refuse) · citation_validity
**1.0** (every quote re-verified verbatim). Cross-filing reconciliation: Q1+Q2 = 6M YTD
exact for revenue and net income across two independent documents.

**The map from every assignment term to its artifact:** [`ACCEPTANCE.md`](ACCEPTANCE.md).
**The 5–10 minute walkthrough:** [`TALKING_POINTS.md`](TALKING_POINTS.md).

Built on take-home #1's cores (durable StateGraph imported by path — compose, never
re-implement). Honest boundaries: two-issuer layout rules, no OCR, extractive-only prose,
LLM seams documented and gate-promoted only.
