# Acceptance — every term of the assignment, mapped to an artifact

Statuses: **SHIPPED** = code + tests + a measured result · **SEAM** = documented swap
point, not exercised · **STATED** = an honest written position (the assignment asks for
reasoning, not just code). Suite: `python3 -m unittest discover -s tests` (7 suites) —
wired into the repo's `make check` and CI.

## The wrinkle: PDF as primary source

| Term | Status | Artifact |
|---|---|---|
| "Treat PDF filings as the primary data source, not XBRL JSON" | SHIPPED | `fetch_filings.py` downloads the real documents, prints them to PDF (headless Chromium), extracts with `pdftotext -layout` → page-anchored JSON in `corpus/extracted/` (PDF SHA256 pinned). No XBRL tag is read anywhere in the pipeline. |
| "EDGAR API sparingly … identify which filings exist" | SHIPPED | Exactly 6 documented calls total: 2 × submissions JSON (discovery — the permitted use) + 4 document downloads, 1s apart, honest User-Agent. CI runs zero network calls. |
| "3–5 representative filings, 1–2 companies" | SHIPPED | 4 filings, 2 companies: Tesla 10-K FY2025, Tesla 10-Q Q1-2026 + Q2-2026 (filed 2026-07-23 — the day before this build), Apple 10-K FY2025. |
| "parse once up front, or retrieve per question?" | STATED | Split by content type: numeric statements are parsed ONCE into a facts store (a financial table is a coordinate system — parse the coordinate system); prose is retrieved per-question extractively. `facts.py` docstring carries the argument. |

## Functional expectations 1–5

| Term | Status | Artifact |
|---|---|---|
| §1 Answer natural-language financial questions | SHIPPED | `qa.py` — 26-case golden eval at answer_accuracy 1.0, incl. the assignment's own examples (Apple revenue $416,161M; Tesla Q2 YoY +25.52%; gross margin 18.03%). |
| §2 Traceability: source, period, values, calc steps, citations | SHIPPED | Every numeric answer carries: doc_id + page + line + **verbatim quote** + SEC source URL per operand, explicit calc steps ("growth = (3,855 − 7,153) / \|7,153\| = −46.11%"), period labels. `citation_validity` gate re-verifies every quote against the corpus (1.0). |
| §3 Handle ambiguity honestly | SHIPPED | Refusal is a first-class outcome with reasons: unfiled period (the assignment's headline question "growth between 2025 and 2026" → refuses, names latest-filed FY2025), absent company (names what IS in the corpus), unsupported metric (lists the registry), conflicting extractions (refuses rather than guesses). 10-Q figures flagged unaudited; GAAP-only stated; refusal_recall AND refusal_precision both gated at 1.0. |
| §4 Agentic / workflow-oriented approach | SHIPPED | The pipeline runs on take-home #1's durable StateGraph (imported by path — compose, never re-implement): parse → route → retrieve → validate → compute → answer, with refusal branches. Verification passes = the validate node + `reconcile.py`; fallbacks = prose route + explain-missing route. |
| §5 Justify retrieval/extraction for numeric tables | SHIPPED + STATED | Mechanism: deterministic layout parsing (`facts.py`), not embeddings. The near-miss the assignment names — "Net income" ($3,855M) vs "Net income attributable to common stockholders" ($3,794M) — exists 3 rows apart in the real Tesla 10-K; the pipeline keeps them distinct AND discloses the neighbor in every answer (`test_near_miss_pair_stays_distinct`). |

## §5's four explicit questions

| Question | Answer (implemented, not just argued) |
|---|---|
| What retrieval mechanism, and why | Rule/layout-based structured parsing for tables (a table is label × period coordinates; parse the coordinates); keyword-scored extractive retrieval for prose. Embeddings: deliberately absent from the numeric path — a documented seam for prose semantic search only. |
| What embeddings are good/bad at | Bad: numeric magnitude, table position, fine label distinctions — the near-miss pair would embed nearly identically while differing by $61M. Good: topical similarity over prose (risk factors, MD&A). Our guard: exact-label matching + mandatory near-miss disclosure in the answer's caveats. |
| Where arithmetic happens | `Decimal` in `compute()` — never a model. Growth, margins, deltas are exactly reproducible; the eval's correctness definition is exact match BECAUSE arithmetic is deterministic. |
| How do you know numbers are correct | Three ways, all shipped: (1) 26 hand-verified golden Q/A pairs checked against the source filings (gate: 1.0); (2) `citation_validity` — every quoted line re-verified verbatim; (3) `reconcile.py` — cross-filing identities on real data: Q1 revenue (Q1 10-Q) + Q2 revenue (Q2 10-Q) = 6M YTD (Q2 10-Q) → 22,387 + 28,236 = 50,623 exact; same for net income. The YTD-only cash-flow case is NOT_MEASURED, stated. |

## Deliverables & discussion prompts

| Term | Status | Artifact |
|---|---|---|
| Tangible artifact | SHIPPED | Runnable CLI (`qa.py "question"`), eval (`eval_sec.py`), reconciler, tests — all offline after the one documented fetch. |
| 5–10 min walkthrough | SHIPPED | `TALKING_POINTS.md` (this folder). |
| Trust & hallucination discussion | STATED | In TALKING_POINTS + this file: the failure that burned trust (LLM arithmetic + no traceability) is structurally impossible here — numbers only come from parsed coordinates with quotes, math only from Decimal. Where it still fails: unseen table layouts (parser rules are fit to 2 issuers), restated/amended filings (would reconcile-FAIL, which is the alarm working), scanned-image PDFs (no OCR). |
| Scale question ("what breaks first at tens of thousands of filings?") | STATED | Measured basis: 4 filings → 1,433 facts parse in ~0.4s single-core (≈0.1s/filing ⇒ ~1 CPU-hour for 30k filings — parsing is NOT the bottleneck). What breaks first: (1) layout-rule variance across issuers/decades — the fix is per-issuer rule packs + a triage queue driven by reconciliation failures; (2) the facts store outgrows JSON → SQLite/Parquet with the same schema; (3) label canonicalization at scale → controlled vocabulary + human-gated mapping proposals. |
| Where AI was used / deliberately not used | STATED | Built WITH an AI coding agent end-to-end (the assignment encourages it). In the artifact: no LLM in the numeric path by design; two documented LLM seams (question parsing, prose summarization) each promotable only through the golden gate. |

## Graded fundamentals (the "no fixed answer key" list)

Every bullet in the assignment's grading note maps to a shipped, testable behavior — see
`data/golden/golden-qa.json` `_meta.correctness_definition` for what "correct" means here,
and the honest-weakness list in TALKING_POINTS.md ("where my own system is weak" is a
required deliverable, not a confession).
