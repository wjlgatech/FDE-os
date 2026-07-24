# Walkthrough (5–10 min) — SEC Filing Intelligence

**Opener (30s).** "The last system died because executives couldn't trust the numbers.
So I built the pipeline where the untrustworthy parts are structurally impossible: numbers
only come from parsed table coordinates with verbatim quotes, arithmetic only from
deterministic code, and every answer either carries its receipts or refuses out loud."

**What it is (60s).** Four REAL filings (Tesla 10-K FY2025, Q1+Q2-2026 10-Qs — Q2 filed the
day before I built this — and Apple 10-K FY2025), fetched with a 6-call documented EDGAR
budget, printed to PDF, extracted with layout preserved. PDF is the primary reality, exactly
as specified; no XBRL tag is read anywhere.

**The demo (2 min, run live).**
```
python3 scripts/qa.py "What was Apple's total revenue in 2025?"        # $416,161M + quote + page + URL
python3 scripts/qa.py "What is Tesla's net income growth between 2025 and 2026?"   # REFUSES: FY2026 not filed
python3 scripts/qa.py "What was Tesla's Q2 revenue change year-over-year?"          # +25.52%, both quarters cited
python3 scripts/eval_sec.py     # 26 hand-verified cases: all gates 1.0
python3 scripts/reconcile.py    # Q1+Q2 == 6M YTD across two documents, to the million
```
Note the second one: the assignment's own headline example is **unanswerable** — FY2026
doesn't exist. The system says so and names what IS on file. A correct "I can't" was the
whole point of the exercise.

**The three decisions that matter (2 min).**
1. **Tables are coordinate systems, not prose.** Embeddings optimize topical similarity —
   they cannot tell "Net income" ($3,855M) from "Net income attributable to common
   stockholders" ($3,794M) three rows apart in Tesla's real income statement. I parse the
   coordinates (label row × period column) and every answer DISCLOSES the near-miss
   neighbor it didn't pick. That disclosure is tested.
2. **Arithmetic never touches the LLM.** Growth = Decimal((b−a)/|a|). An LLM computing
   3,855/7,153 is a rounding hallucination at best; at billions scale it's how trust died.
   Deterministic math is also what makes "correct = exact match" a coherent eval definition.
3. **Correctness is built, not assumed.** With XBRL you get meaning for free; with PDFs
   you build your own ground truth: 26 hand-verified Q/A pairs (gate 1.0), every citation
   re-verified verbatim (gate 1.0), and cross-filing reconciliation — Q1 10-Q + Q2 10-Q
   must sum to the 6-month YTD column: 22,387 + 28,236 = 50,623, exact. Three numbers, two
   independent documents, one identity that only holds if extraction, period mapping, and
   scale handling are ALL right.

**Where it's weak (say it first, 60s).** Parser rules are fit to two issuers' layouts —
a third company is a rule-pack away, and reconciliation failures are the triage signal;
scanned-image PDFs need OCR (absent); amended/restated filings would reconcile-FAIL (which
is the alarm working, but a human resolves it); prose answers are extractive quotes, not
synthesis — the LLM summarization seam is documented and would be promoted through the same
golden gate as everything else.

**Scale (30s).** Parsing measured at ~0.1s/filing single-core ⇒ the 30k-filing archive is
about a CPU-hour — parsing isn't the bottleneck. Layout variance is: the fix is per-issuer
rule packs, a reconciliation-driven triage queue, and the facts store moving JSON → SQLite.

**Close.** "Same discipline as my first take-home: deterministic core, receipts everywhere,
refusal as a feature, and an eval gate that failed me before it passed me."
