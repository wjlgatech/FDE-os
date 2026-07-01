---
name: doc-understanding
description: Parse messy enterprise documents (DOCX with merged tables + track-changes, XLSX with shared strings + merged ranges, plus markdown/CSV) into one canonical structured JSON representation, then score the parse itself with a parse-quality gate (coverage · structure · fidelity) — because Output Quality ≤ Input Representation Quality. Use before feeding any enterprise doc to an agent, a RAG pipeline, or knowledgefy: NO-GO on empty parses and on documents with unresolved track-changes (the text is not authoritative). Pure stdlib, deterministic, offline.
---

# doc-understanding

> Built to close the gap named by a **real regulated FDE engagement**
> ([field note, 2026-07-01](../../docs/field-notes/2026-07-01-regulated-agentic-pipeline.md)):
> *"document parsing is the real technical moat — tables, OOXML, track-changes; OCR ≠ enough."*
> This instantiates lessons #4 (structure > models), #5 (constrain + validate), and #7 (the moat).

## Why this exists

Every enterprise engagement starts with documents — protocols, contracts, trackers — and agents
downstream can only be as good as the representation they're fed (**Output Quality ≤ Input
Representation Quality**). The failure mode isn't "can't read the file"; it's *silently wrong
structure*: a merged header cell mis-attributed, a deleted clause still present, a spreadsheet
column shifted. So this skill does two things, and the second is the point:

1. **Parse** → one canonical representation (`blocks` of headings/paragraphs/tables), regardless
   of source format.
2. **Gate the parse itself** — coverage (did we extract content?), structure (headings/tables, or a
   blob?), fidelity (is the text authoritative? unresolved track-changes say no). **No evidence ⇒
   NO-GO**; an empty parse never passes.

## What it handles (pure stdlib — zipfile + ElementTree)

| Format | Extracted | The hard part it resolves |
|---|---|---|
| `.docx` | headings (level), paragraphs, tables | `gridSpan`/`vMerge` merged cells → `None`-padded grid; `w:ins`/`w:del` counted, deleted text excluded |
| `.xlsx` | one dense row-grid per sheet | sharedStrings (incl. rich-text runs), inline strings, sparse cell refs → dense grid, merged ranges counted |
| `.md` `.txt` | headings + paragraphs | (trivial case, kept for one uniform interface) |
| `.csv` | one table | — |
| `.pdf` `.doc` `.xls` | **refused honestly** | conversion/OCR is a different tool; guessing would fake coverage |

## Run it

```bash
S=skills/doc-understanding/scripts/doc_understand.py

python3 $S parse protocol.docx            # human-readable markdown view
python3 $S parse sites.xlsx --json        # canonical JSON (feed to agents / knowledgefy)
python3 $S gate protocol.docx             # parse-quality gate — exit 1 on NO-GO
python3 $S gate tracker.xlsx --threshold 0.8
```

Also exposed as the `doc_gate` tool on the [fde-mcp-server](../fde-mcp-server/) (pass a repo-relative
`path`), so any MCP client can gate a document before reasoning over it.

## The gate, precisely

`quality(rep)` scores three 0–1 dimensions; `overall = 0.4·coverage + 0.3·structure + 0.3·fidelity`.
`gate(rep, threshold=0.7)` returns NO-GO with itemized reasons when: zero blocks extracted, overall
below threshold, or unresolved track-changes (each pending revision costs fidelity 0.1). A NO-GO means
*fix the input* (accept/reject revisions, unmerge the layer, convert the format) — not "lower the bar."

## Composes with

- **`knowledgefy`** — parse → canonical JSON → prose/markdown → knowledge spine.
- **`rag-eval-harness`** — gate the corpus *before* indexing; garbage parses poison retrieval silently.
- **`workflows/engagement-readiness`** — a future third AND-gate: workflow mapped ∧ retrieval grounded ∧ **inputs parse-clean**.

## Tests

```bash
python3 -m pytest skills/doc-understanding/tests -q   # 10 tests; fixtures are real OOXML zips, not mocks
```
