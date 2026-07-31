# Walkthrough (5–10 min) — SEC Filing Intelligence

Simple enough for a 15-year-old, evidenced enough for a tech lead. Per section: the
one-liner → the picture → the evidence → the line to land.

---

## Opener (30 sec)

**Say:** "The last AI system here died because executives couldn't trust its numbers. So I
built one where the untrustworthy parts are *impossible*: every number comes with a receipt
you can check yourself, all math is done by a calculator — never by the AI — and when it
can't answer, it says so instead of making something up."

**The picture:** imagine a friend who helps with your homework. The old friend sounded
confident but sometimes invented answers. My friend shows you the exact page of the textbook
every answer came from, does arithmetic on a real calculator, and says "I don't know" when
the book doesn't cover it. Which friend do you trust before an exam?

---

## What it is (60 sec)

**Say:** "Four REAL SEC filings — Tesla's annual report plus two quarterly reports (one filed
the day before I built this), and Apple's annual report. The rules said: treat PDFs as your
data source, not the clean API — because that's the client's reality. So I downloaded the
documents exactly six times (the API budget is written in the code), turned them into PDFs,
and extracted the text with page numbers preserved."

**The picture:** the client bought a warehouse full of paper reports. You don't get the neat
spreadsheet — you get the paper. The assignment is: build the librarian.

---

## The live demo (2 min — run these on the site)

1. **"What was Apple's total revenue in 2025?"** → **$416,161M**, with the exact sentence
   from the filing, the page number, and a link to the real SEC document.
   *"Don't trust me — click the link and Ctrl-F the quote."*
2. **"What is Tesla's net income growth between 2025 and 2026?"** → it **refuses**.
   *"This was the assignment's own first example question — and it's a trick: Tesla's 2026
   annual report doesn't exist yet. The old system would have made up a number. Mine tells
   you why it can't answer and what it CAN."*
3. **"What was Tesla's Q2 revenue change year-over-year?"** → **$22,496M → $28,236M =
   +25.52%**, both quarters cited, the subtraction and division shown step by step.

---

## The three decisions that matter (2 min)

**1. Tables aren't paragraphs — so I don't search them like paragraphs.**
*The picture:* a financial table is like a seating chart — row says WHAT ("Net income"),
column says WHEN ("2025"). You find a seat by row and column, not by asking "which seat
FEELS most similar?". That "feels similar" approach (embeddings) is great for finding a
paragraph ABOUT risks — and terrible at telling apart two look-alike rows. Tesla's real
report has exactly that trap: "Net income" ($3,855M) and "Net income attributable to common
stockholders" ($3,794M), three rows apart, nearly identical as sentences, different by $61M.
My system reads the seating chart — and every answer *tells you about the look-alike row it
didn't pick*. That honesty is a tested feature.

**2. The AI never does math.**
*The picture:* you wouldn't let someone "vibe" your paycheck. Growth rates and margins are
computed by code — a calculator — so the same question gives the same answer, every time.
That's also why my test can demand EXACT answers: there's no "close enough" hiding a bug.

**3. I built my own answer key before trusting the system.**
*The picture:* before you trust a new calculator, you check it on problems you already know
the answers to. I hand-checked **26 questions against the actual filings** — including trick
questions that MUST be refused — and locked them into an automatic test. Scores: accuracy
1.0, refusals caught 1.0, no false refusals 1.0, every quote verified 1.0. And one more
trick: the same number appears in different filings — Q1's report says 22,387, Q2's report
says 28,236 and ALSO says "six-month total: 50,623". Add mine: 22,387 + 28,236 = **50,623.
Exactly.** Two separate documents agreeing is how you know the extraction isn't lying —
that's how accountants have caught errors for 500 years (double-entry bookkeeping).

---

## Where it's weak — say it before they ask (60 sec)

**Say:** "Three honest limits. One: my table-reading rules are tuned to two companies —
a third company means adding rules, and the double-checking system is what tells me where
they break. Two: scanned/photo PDFs would need OCR, which I didn't build. Three: for
wordy questions like 'what risks did management mention?', I quote the document verbatim
instead of summarizing — an AI summarizer could slot in later, but only after it passes the
same 26-question exam as everything else."

---

## Scale (30 sec)

**Say:** "Parsing takes a tenth of a second per filing — the full thirty-thousand-document
archive is about one CPU-hour. Speed isn't what breaks. What breaks first is layout variety
across companies and decades, and the fix is per-company rule packs plus a queue of
reconciliation failures that tells humans exactly where to look."

---

## Close

**Say:** "Same discipline as my first take-home: the boring parts are deterministic, every
answer carries receipts, refusing is a feature, and my own test failed me before it passed
me — my first parser run scored 13 out of 19, and the three bugs it caught are in the commit
history. A system that can't fail its own test isn't being tested."
