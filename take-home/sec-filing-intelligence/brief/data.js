/* Single source of truth for the SEC case-study brief (window.BRIEF_DATA) and the
   /api/chat corpus. Generated 2026-07-24 from the take-home's shipped artifacts —
   every number below is a measured, CI-gated result; playground answers come from
   the REAL pipeline (api/ask.py, vendored byte-identical, drift-gated). */
const BRIEF_DATA = {
  stats: { cases: "26/26", gates: 4, filings: 4 },

  repo: "https://github.com/wjlgatech/FDE-os/tree/main/take-home/sec-filing-intelligence",

  wrinkle: [
    ["PDF is the primary reality — not XBRL", "The archive is purchased PDFs; the pipeline reads layout-extracted PDF text only. No XBRL tag anywhere.", "fetch_filings.py → chromium print-to-pdf → pdftotext -layout → page-anchored JSON, PDF SHA256-pinned"],
    ["EDGAR API is scarce", "Exactly 6 documented calls, ever: 2 discovery (the permitted use) + 4 document downloads. CI runs zero network calls.", "the budget is written in the fetch script's docstring"],
    ["Small representative corpus", "4 real filings, 2 companies: Tesla 10-K FY2025 + 10-Q Q1/Q2-2026 (Q2 filed the day before this build), Apple 10-K FY2025.", "scale plan measured: ~0.1s/filing parse ⇒ ~1 CPU-hour for a 30k archive; layout variance breaks first, not throughput"],
  ],

  decisions: [
    { title: "Tables are coordinate systems — parse, don't embed",
      why: "Embedding models optimize topical similarity; they cannot encode numeric magnitude, table position, or fine label distinctions. The assignment's own example — 'Net income' vs 'Net income attributable to common stockholders' — is REAL in the Tesla 10-K: $3,855M vs $3,794M, three rows apart, near-identical as vectors.",
      how: "Deterministic layout parsing: period headers (annual, quarterly 3/6-month, balance-sheet instants — incl. split two-line headers), scale sentinels, label × column coordinates. The near-miss neighbor is DISCLOSED in every answer's caveats — tested." },
    { title: "Arithmetic never touches the LLM",
      why: "An LLM computing (94,827 − 97,690)/97,690 is a rounding hallucination at best; at billions scale it's how the previous system lost executive trust.",
      how: "Decimal in compute() — growth, margins, deltas exactly reproducible. That determinism is what lets the eval define 'correct' as EXACT match, no tolerance band." },
    { title: "Refusal is a first-class outcome",
      why: "A correct 'I can't answer' beats a polished hallucination — the assignment says so; the eval enforces it BOTH ways.",
      how: "refusal_recall gated 1.0 (every must-refuse refuses: unfiled FY2026, absent companies, unsupported metrics, conflicting extractions) AND refusal_precision gated 1.0 (no answerable question refuses). Refusals name what the corpus DOES hold." },
    { title: "Correctness is built, not assumed",
      why: "With XBRL, meaning is free; with PDFs you build your own ground truth.",
      how: "Three shipped mechanisms: 26 hand-verified golden Q/A pairs (gate 1.0); citation_validity — every quoted line re-verified verbatim against the corpus (gate 1.0); reconcile.py — cross-filing identities: Q1 + Q2 must equal the 6-month YTD column, across two independent documents." },
    { title: "LLM seams, gate-promoted only",
      why: "The graded fundamental is knowing what LLMs do reliably vs what deterministic code must own.",
      how: "Two documented seams — question parsing (currently deterministic patterns) and prose summarization (currently extractive quotes with page cites). Either gets an LLM only by matching the deterministic baseline through the same golden gate." },
    { title: "Composed, not re-invented",
      why: "House rule: import cores, never re-implement.",
      how: "The pipeline runs on take-home #1's durable StateGraph, imported by path: parse → route → retrieve → validate → compute → answer, with refusal branches as edges." },
  ],

  scoreboard: [
    { label: "answer_accuracy", value: "1.0", note: "26/26 golden cases — exact value + unit + period" },
    { label: "refusal_recall", value: "1.0", note: "every unanswerable case refuses (gate)" },
    { label: "refusal_precision", value: "1.0", note: "no answerable case refuses (gate)" },
    { label: "citation_validity", value: "1.0", note: "every quote re-verified verbatim (gate)" },
    { label: "reconciliation", value: "PASS", note: "Q1 22,387 + Q2 28,236 = 50,623 = 6M YTD, exact; net income likewise; YTD-only cash flow honestly NOT_MEASURED" },
  ],

  golden_sample: [
    ["What was Apple's total revenue in 2025?", "$416,161M — quote + page + SEC URL", "value"],
    ["Tesla net income growth 2025 → 2026?", "REFUSES: FY2026 not filed; names latest annual on file (FY2025)", "refusal — the assignment's own headline example"],
    ["Tesla Q2 revenue change YoY?", "$22,496M → $28,236M = +25.52%, both quarters cited", "quarter growth"],
    ["Tesla net income 2025?", "$3,855M — and the answer DISCLOSES the $3,794M 'attributable' neighbor it didn't pick", "near-miss disclosure"],
    ["Tesla gross margin 2025?", "17,094 / 94,827 = 18.03% — Decimal, calc steps shown", "derived metric"],
    ["Microsoft net income, latest filing?", "REFUSES: not in the corpus; names what IS (Tesla, Apple) and how to add a company", "refusal"],
  ],

  corpus: [
    "WHAT THIS IS: case study #2 from a Big-Four consulting firm's Agentic-AI-Engineer loop (name withheld publicly; the named layer lives in the private founding-members vault) — the second-round take-home: natural-language questions over SEC filings where the archive is PDF (not XBRL) and the EDGAR API is scarce. Public code: github.com/wjlgatech/FDE-os under take-home/sec-filing-intelligence. The Playground tab on this page runs the REAL pipeline via /api/ask.",
    "THE DATA REALITY: 4 real filings — Tesla 10-K FY2025, Tesla 10-Q Q1-2026 and Q2-2026 (Q2 filed 2026-07-23, the day before this build), Apple 10-K FY2025 — fetched with a documented 6-call EDGAR budget (2 discovery + 4 downloads), printed to PDF via headless Chromium (reproducing the purchased-PDF-archive condition), extracted with pdftotext -layout into page-anchored JSON with the PDF SHA256 pinned. CI runs fully offline on the checked-in extractions.",
    "THE SCOREBOARD (all CI-gated, exit non-zero on failure): answer_accuracy 1.0 over 26 hand-verified golden cases; refusal_recall 1.0; refusal_precision 1.0; citation_validity 1.0 (every quoted line re-verified verbatim against the corpus); cross-filing reconciliation PASS. Repo suite 223+ tests.",
    "WHY NOT EMBEDDINGS FOR TABLES: embedding models are optimized to place topically similar text close in vector space — not to encode numeric magnitude, table position, or fine label distinctions. The assignment's own example pair is real in the Tesla 10-K: 'Net income' $3,855M and 'Net income attributable to common stockholders' $3,794M sit three rows apart and would embed nearly identically while differing by $61M. The pipeline parses the table's coordinate system instead (label row × period column), and every answer DISCLOSES the near-miss neighbor it did not pick — that disclosure is a tested behavior. Embeddings remain a documented seam for prose (risk factors, MD&A), where topical similarity is the right objective.",
    "WHERE ARITHMETIC HAPPENS: only in deterministic code (Python Decimal) — growth rates, margins, deltas. The LLM never computes. Example calc step shown in every answer: growth = (3,855 − 7,153) / |7,153| = −46.11%. This determinism is what makes the eval's definition of correct — exact match on value, unit, and period — coherent; a tolerance band would only paper over extraction bugs.",
    "REFUSAL AS A FEATURE: the assignment's own headline example question — 'What is Tesla's net income growth between 2025 and 2026?' — is unanswerable: no FY2026 annual filing exists. The system refuses WITH REASONS: names the unfiled period, the latest annual on file (FY2025), and every period the corpus holds. Same for absent companies (Microsoft, Amazon, NVIDIA, Google, Meta, Netflix → refusal names what IS in the corpus and that adding a company = running the fetch script on its filings). Both refusal recall AND precision are gated at 1.0.",
    "PERIOD MACHINERY: annual (FY columns incl. Apple's September fiscal year), quarterly three-month and six-month YTD columns from 10-Qs, and balance-sheet instants — including the split two-line header ('December 31,  December 31,' with years on the following row) that broke the first parser draft. Bare-quarter questions ('Q2 revenue YoY?') resolve to the latest matching quarter on file, and growth is always computed older → newer.",
    "CROSS-FILING RECONCILIATION (the trust mechanism): the same economic quantity appears in multiple filings, and independent extractions must reconcile — double-entry bookkeeping for an extraction pipeline. On real data: Q1-2026 revenue 22,387 (from the Q1 10-Q) + Q2-2026 revenue 28,236 (from the Q2 10-Q) = 50,623 = the six-month YTD column in the Q2 10-Q, exact to the million; net income likewise (491 + 1,128 = 1,619). The 10-Q cash-flow statement is YTD-only, so its additivity check reports NOT_MEASURED — stated, never faked.",
    "HONEST HISTORY (the parser earned its accuracy): the first probe run scored 13/19. Three real bugs were found and fixed: (1) balance-sheet headers split across two lines were invisible; (2) the VIE note's prose 'in the consolidated balance sheets' masqueraded as a statement title — fixed by requiring heading-shaped full-line matches, which also excludes table-of-contents rows; (3) cash-at-end-of-period rows on the cash-flow statement were answering balance-sheet questions — fixed by restricting instant metrics to AsOf columns. Final: 26/26 hand-verified probes exact.",
    "HONEST WEAKNESSES (volunteered): layout rules are fit to two issuers — a third company is a rule-pack away, and reconciliation failures are the triage signal; scanned-image PDFs need OCR (absent); amended/restated filings would reconcile-FAIL (the alarm working — a human resolves); prose answers are extractive verbatim quotes with page cites, not synthesis; the question parser is pattern-based (an LLM seam exists for phrasing robustness, promotable only through the golden gate).",
    "SCALE ANSWER (measured, not vibed): parsing measured at ~0.1s/filing single-core → the tens-of-thousands archive is roughly one CPU-hour of parsing — throughput is NOT the bottleneck. What breaks first: layout-rule variance across issuers and decades (fix: per-issuer rule packs + a reconciliation-driven triage queue), then the facts store outgrowing JSON (fix: SQLite/Parquet, same schema), then label canonicalization at scale (fix: controlled vocabulary + human-gated mapping proposals).",
    "RELATION TO CASE STUDY #1: same discipline, second proof — deterministic core with LLM seams, golden dataset built before trust is asked for, gates that failed honestly before passing (case 1: a missing policy rule; case 2: three parser bugs), receipts everywhere (verbatim quotes, page anchors, reconciliation), and a live playground running the real code. Case study #1: enterprise-triage-brief.vercel.app. The named-company layer of both lives in the private founding-members vault (see the community page hook).",
  ],
};

if (typeof window !== "undefined") window.BRIEF_DATA = BRIEF_DATA;
if (typeof module !== "undefined") module.exports = { BRIEF_DATA };
