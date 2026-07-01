# Field Note — the regulated agentic pipeline (a real FDE engagement)

> **Source:** a real FDE engagement recap (pharma / FDA-regulated clinical trials; five pods —
> CRA, ICF, CLS, BioA, SDTM — with OpenAI as the deploying partner). Provided by Paul, 2026-07-01.
> This is the **flywheel working**: a real engagement → transferable lessons → improve Objectives 1 & 2.

## The one-line learning

A real, multi-pod, regulated agentic engagement **independently arrived at FDE-os's core bets** —
*validation is core infrastructure*, *workflow fragmentation is the root problem*, *structure beats
models* — which is the strongest possible external validation that the toolkit is pointed at the real
bottlenecks. It also names one moat FDE-os has **no tool for yet**: document parsing.

## The cross-cutting pattern (transferable — this is the deep structure)

```
Documents + Enterprise Systems
        → Extraction / Parsing
        → Structured (canonical) Representation
        → Agentic Reasoning
        → Validation Layers
        → Human Review
        → Regulated Output / Business Action
```

This pipeline recurred across **all five pods** despite different surface tasks. That recurrence is
the signal: it's the **architecture of regulated knowledge work**, not a pharma quirk.

## Transferable vs domain-specific (the FDE meta-skill: separate the two)

| # | Lesson from the engagement | Transferable? | Why / FDE-os mapping |
|---|---|---|---|
| 1 | **Workflow fragmentation is the root problem** (10–12 systems; value = ↓ search+switching+synthesis) | ✅ **Deep structure** | Any enterprise FDE engagement. Maps to **`invisible-workflow-mapper`** — the workflow *is* the product; "add another dashboard" is the anti-pattern. |
| 2 | **Validation loops are non-negotiable** (generate → validate → feedback → retry) | ✅ **Deep structure** | This *is* FDE-os's eval-as-gate thesis: **`true-scorer` · `criteria-scorer` · `rag-eval-harness` · `eval-loop`**. The engagement calls it "core infrastructure, not a patch." |
| 3 | **Human-in-the-loop mandatory in regulated work** (accountability can't be delegated to a probabilistic system) | ✅ **Deep structure** | `invisible-workflow-mapper`'s **regulated-signoff** archetype + its `evidence_ritual` / `kill_points` dimensions. Verified: our tool classified this engagement as regulated-signoff. |
| 4 | **Structure > Models** (data quality dominates outcomes; canonical representation first) | ✅ **Deep structure** | The canonical-data-layer idea. Partial in **`knowledgefy`** (prose → spine) and **`jd-compiler`** (JD → canonical competency model). |
| 5 | **Retrieval-constrained generation** (text-to-SQL needs schema+examples+validation) | ✅ **Mostly transferable** | The grounding discipline behind **`rag-eval-harness`**. The *text-to-SQL* instance is narrower but the pattern (constrain + ground + validate) is universal. |
| 6 | **Cost + routing is first-class** (model evaluation + routing strategy) | ✅ **Transferable** | The `/free-llm` fallback-chain discipline (NIM → Groq → Gemini → …), ordered for correctness then cost. |
| 7 | **Document parsing is the real moat** (tables, OOXML, track-changes, regulatory templates; OCR ≠ enough) | ✅ **Transferable problem** — ✅ **now [`doc-understanding`](../../skills/doc-understanding/)** | Was the gap (`knowledgefy` ingests prose, not messy enterprise docs); closed the same week this note landed — OOXML → canonical rep + parse-quality gate. |
| — | USDM, SDTM, ICF, CRA, BioA, CLS; FDA submission rules; Snowflake migration; country templates | ❌ **Domain-specific** | Clinical-trial canonical models, roles, and regulatory specifics. *Do not* generalize these — they're the surface, not the structure. The FDE skill is knowing which is which. |

## Impact on the three pillars

**📘 Learning (Objective 1 — course).** This engagement is a ready-made **capstone case study**: the
cross-cutting pipeline is a curriculum module ("the regulated agentic pipeline"), and the
transferable-vs-domain table above is a worked example of the single most important FDE meta-skill —
*separating deep structure from surface*. It also **confirms the JD-compiler finding** that
*evaluation* (Cluster 3) and *workflow/discovery* (Cluster 5) are the load-bearing clusters: a real
engagement spends its hardest effort exactly there.

**🛠️ Tooling (Objective 2).** Two outcomes, both honest:
- **Validated:** the entire eval suite + `invisible-workflow-mapper` + the grounding focus map 1:1 to
  what the engagement calls "core infrastructure." We didn't guess the bottlenecks — a real engagement
  hit the same ones.
- **Gap exposed → closed:** **document parsing** ("the real technical moat") — FDE-os had nothing here
  when this note was written; [`skills/doc-understanding`](../../skills/doc-understanding/) now covers it.
  Remaining runner-up gap: a runtime *generate→validate→retry* loop template (distinct from `eval-loop`,
  which scores artifact *versions*).

**🌱 Community (Objective 3 — flywheel).** This *is* the flywheel turning: a real engagement became a
durable, reusable artifact (this note) that improves the course and the toolkit. It's exactly the
war-story shape the Community door (`contribute.html`) collects — and it demonstrates the value
proposition: an FDE who had internalized FDE-os would have walked into this engagement already knowing
to *map the fragmented workflow first* and *treat validation as core infra*, instead of discovering it
across five pods.

## The one move it recommends

Build a **document-understanding skill** (the named moat): messy enterprise docs (PDF/DOCX/XLSX, merged
tables, track-changes) → a **canonical structured representation** + a parse-quality **eval gate**
(because *Output Quality ≤ Input Representation Quality*). It closes the biggest tooling gap *and*
instantiates lessons #4, #5, and #7 at once. **Built the same week:
[`skills/doc-understanding`](../../skills/doc-understanding/)** — the flywheel closed its loop.
