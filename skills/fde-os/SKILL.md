---
name: fde-os
description: "The FDE-os master tool — one front door to the whole toolkit: ship gates, evals, knowledge compilers, the external-tooling hub, the reference agent runtime, and the MCP surface. Route any FDE ask to the right skill; every example below is real, offline, and CI-verified."
---

# /FDE-os — the master tool (one front door, twelve engines)

FDE-os is a **plugin that is also a repo**: install it (or clone it) and you get 12 deterministic,
offline, stdlib-only skills, two MCP servers, a compiled external-tooling hub, and a reference
agent runtime — every one gated by tests and exit codes. This skill is the THIN ROUTER over them:
all logic lives in the tested engines under `skills/`; this file only tells you (or any agent)
which engine answers which ask.

**The contract that makes it FDE-os:** no evidence ⇒ No · claimed ≠ measured · an honest ❌ beats a
fake ✅ · every gate exits non-zero on failure so CI can enforce it. The examples below are parsed
out of this file and executed by `skills/fde-os/tests/test_master_examples.py` — if a demo rots,
the build goes red.

## 0. Get it

```text
Claude Code plugin:  /plugin marketplace add wjlgatech/FDE-os   → skills auto-discover
Codex:               .codex-plugin/plugin.json points at the same skills/ tree
Any agent w/ shell:  git clone https://github.com/wjlgatech/FDE-os && cd FDE-os && make check
MCP (any client):    python3 skills/fde-mcp-server/scripts/server.py   (stdio JSON-RPC)
```

## 1. Route the ask

| You want… | Run |
|---|---|
| **Gate a draft before shipping** (TRUE rubric: Teach/Reproduce/Understand/Engage) | `score.py <draft.md>` — exits 1 on BLOCK |
| **Gate against your own criteria** (rubric-as-data) | `criteria_score.py score <artifact> <criteria.json>` |
| **Grade retrieval + grounding** (precision/recall/MRR/grounding/citations) | `rag_eval.py score <eval_set.json> --k 5` |
| **GO/NO-GO an engagement on measured outcomes** (claimed never passes) | `outcome_score.py score <contract.json>` — exits 2 on NO-GO |
| **Compile prose → provenance-pinned knowledge graph** | `knowledgefy.py build <vault> --out <dir>` |
| **Compile a job description → competency map + prep plan** | `jd_compile.py compile <jd.md>` |
| **Find external tooling** (7 compiled top-rated repos, honest notGoodAt edges) | `hub_query.py find <need>` · `recipe <repo>` · `list` |
| **Parse enterprise docs safely** (DOCX/XLSX/MD → gated canonical JSON) | `doc-understanding` skill — refuses PDFs honestly |
| **Improve an artifact iteratively, revert on regression** | `eval-loop` skill — git is the memory |
| **Map an org's invisible decision workflow** | `invisible-workflow-mapper` skill |
| **Compose gates into one verdict** | `workflows/engagement-readiness/run.py <engagement.json>` |
| **Run/inspect the reference agent runtime** (durable graph, HITL, verifiable citations) | `take-home/deloitte-agentic-triage/scripts/run.py` then `eval.py` |
| **Expose all of it to an MCP client** | `fde-mcp-server` — 8 tools incl. `hub_find`, `true_score`, `rag_eval` |

## 2. Verified demos (run from the repo root — each is CI-tested)

### Ship gates — score before you ship

```bash
# A real draft that FAILS the gate (R=0: no kit link, no run instructions) — exit 1, honestly
python3 skills/true-scorer/scripts/score.py docs/marketing/context-starved-short-post.md  # exit 1
# Scores-mode PASS: total >= 10 and every letter >= 2 — exit 0
python3 skills/true-scorer/scripts/score.py --scores T=3,R=2,U=3,E=2  # exit 0
# Your own rubric as data: 3/4 criteria pass -> still BLOCK (word count over) — exit 1
python3 skills/criteria-scorer/scripts/criteria_score.py score docs/marketing/context-starved-short-post.md docs/marketing/viral-post-criteria.json  # exit 1
```

### Evals — retrieval, grounding, and outcomes

```bash
# RAG eval on the pharmacy example: precision@5 0.5, grounding 1.0, citation coverage 1.0
python3 skills/rag-eval-harness/scripts/rag_eval.py score skills/rag-eval-harness/examples/pharmacy-rag-eval.json --k 5  # exit 0
# Outcome contract: 2 measured passes, 1 claimed (reported, never counts) -> GO
python3 skills/outcome-contract/scripts/outcome_score.py score skills/outcome-contract/examples/acme-receptionist.json  # exit 0
```

### Knowledge compilers — prose and JDs become structures

```bash
# A note vault -> concept/evidence graph with provenance edges (16 concepts, 32 edges)
python3 skills/knowledgefy/scripts/knowledgefy.py build knowledge/vault/snowflake-summit-2026 --out /tmp/fdeos-demo-graph  # exit 0
# A captured JD -> competency clusters (frameworks, vector DBs, eval-obs, patterns)
python3 skills/jd-compiler/scripts/jd_compile.py compile course/target-jds/agentic-ai-engineer-senior-consultant.md  # exit 0
```

### The hub — external tooling on trigger, never in context

```bash
# Rank compiled repos against a need (term-overlap, deterministic)
python3 skills/repo-compiler/scripts/hub_query.py find observability evals  # exit 0
# Full integration recipe for one repo — SHA-pinned source + honest notGoodAt
python3 skills/repo-compiler/scripts/hub_query.py recipe fastmcp  # exit 0
# Zero matches NEVER fail silent: a diagnostic names the available vocabulary — exit 2
python3 skills/repo-compiler/scripts/hub_query.py find quantum knitting  # exit 2
```

### Composition + MCP — gates chain, tools surface

```bash
# Two skills AND-ed into one GO/NO-GO (adoption-fit AND correctness)
python3 workflows/engagement-readiness/run.py workflows/engagement-readiness/examples/engagement.json  # exit 0
# The whole toolkit as MCP tools over stdio JSON-RPC
printf '{"jsonrpc":"2.0","id":1,"method":"tools/list"}\n' | python3 skills/fde-mcp-server/scripts/server.py  # exit 0
```

### The reference runtime — an agent with receipts

```bash
# 12 requests through the durable triage graph (checkpoints, HITL pauses, traces)
python3 take-home/deloitte-agentic-triage/scripts/run.py --out /tmp/fdeos-demo-run  # exit 0
# Grade it against labeled ground truth: five metrics, escalation recall gated at 1.0
python3 take-home/deloitte-agentic-triage/scripts/eval.py --run-dir /tmp/fdeos-demo-run  # exit 0
# The GOLDEN set: 47 cases, 11 tag families — found a missing policy rule on day one
python3 take-home/deloitte-agentic-triage/scripts/run.py --requests take-home/deloitte-agentic-triage/data/golden/golden-requests.jsonl --out /tmp/fdeos-golden-run  # exit 0
python3 take-home/deloitte-agentic-triage/scripts/eval.py --run-dir /tmp/fdeos-golden-run --ground-truth take-home/deloitte-agentic-triage/data/golden/golden-truth.json  # exit 0
```

## 3. Report results faithfully

Relay each engine's verdict verbatim (PASS/BLOCK, GO/NO-GO, exit code) — a BLOCK is a working
feature, not an error to apologize for. If an ask routes to no engine, say so and point at the
hub (`hub_query.py find …`) or at `AGENTS.md` — never improvise a fake capability.

## 4. See also

`AGENTS.md` (the backbone + conventions) · `knowledge/hub/` (compiled external toolsets) ·
`docs/field-notes/` (what real engagements taught) · live surfaces:
https://fde-os-journey.vercel.app (graded delivery history) ·
https://deloitte-triage-brief.vercel.app (the runtime, presented).
