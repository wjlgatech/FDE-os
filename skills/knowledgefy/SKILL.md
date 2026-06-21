---
name: knowledgefy
description: Turn a local, heterogeneous PROSE research vault (Markdown notes, synthesis docs) into a navigable, offline knowledge spine — deterministically, with no engine and no network. Use when you have a folder or file of prose research and want a queryable concept+evidence graph (graph.json + self-contained HTML) without a running graph database or live web calls. NOT for GFM-table awesome-lists (use living-repo) or when a heavyweight engine + avatars are wanted (use dreammaketrue/kgfy).
---

# knowledgefy

> Local-first, offline, deterministic: a prose vault → knowledge spine.
> Principle: **prose already carries structure** — headings are concepts, citations are evidence.
> Decompress that structure deterministically, with no engine and no network.

## When to run this

- You have a local research vault as prose (Markdown synthesis, notes, a literature dump) and
  want a navigable spine the rest of your pipeline can consume.
- You need it **offline and reproducible** — no Neo4j, no paid engine, no live web.
- The input is *prose*, not GFM tables.

## Why this exists (the verified gap)

- `living-repo` is deterministic and offline but parses **GFM tables only** — on a prose vault it
  extracts almost nothing (measured: 5 nodes from a 228-line vault, missing all headings/citations).
- `dreammaketrue`/`kgfy` ingests local files but needs a **running engine (Neo4j)** and is not a
  deterministic, no-network base path.

`knowledgefy` fills exactly that narrow gap and nothing more.

## What it produces

- `*.graph.json` — normalized, deduped, deterministically ordered. Node types:
  - `concept` — one per Markdown heading, with `level` and `source_file`; nested headings get a
    `part_of` edge to their parent.
  - `evidence` — one per cited URL (inline `[text](url)` **and** bare `https://…`), with a `cites`
    edge from the enclosing concept.
- `*.html` — a self-contained view (no external scripts) that works from `file://`: a concept
  outline on the left, the cited sources for a selected concept on the right.

## What it does NOT do (honest edges)

- **No semantic edges.** Only structural relationships (`part_of` from nesting, `cites` from
  citations). Concept-to-concept "supports/contradicts/causes" edges are out of the deterministic
  base path — they belong to an optional NIM-enrich pass (not implemented here).
- **No confidence scoring.** Banding evidence by source reliability is the *consumer's* job
  (e.g. building the FDE spine maps each source to the vault's reliability ledger). knowledgefy
  emits the raw structure.
- **No network, ever, on the base path.** If you want live enrichment, that is a separate opt-in.

## How to run

```bash
python3 skills/knowledgefy/scripts/knowledgefy.py build <vault.md | vault_dir/> \
  --out knowledge/spine.graph.json --html knowledge/spine.html
```

Single file or a directory (recurses `**/*.md`). Code-fenced blocks are ignored, so example
snippets don't pollute the graph.

## Verify

```bash
python3 -m unittest discover -s skills/knowledgefy/tests -p 'test_*.py'
```

Covers: happy-path concept/evidence extraction, the no-network invariant, empty-vault safety,
byte-for-byte determinism, and code-fence exclusion.

## Provenance

Built for FDE-os (roadmap KTD3, U2). Output contract borrowed from `knowledge-graph` and
`living-repo`; the deterministic prose parse is the part neither of those covers.
