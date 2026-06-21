---
name: field-kit-generator
description: Scaffold and lint a Delta Field Kit to convention. Use when a Delta Field Manual is ready to ship its one forkable asset, or to check that an existing kit names its source, has run instructions, and marks unknowns as RISKS. Enforces the Field Kit menu + folder layout; delegates the actual skill synthesis to skillfy/skill-distillery (a thin wrapper, not a reimplementation).
---

# field-kit-generator

> The convention-keeper for the "R" of every TRUE post. It does NOT synthesise the skill — that's
> `skillfy`'s job (KTD5). It enforces the **Field Kit menu**, the **folder layout**, and the rules:
> *name your source article, mark every unknown as a RISK, never invent.*

## The Field Kit menu (a kit is exactly one)

Prompt · Agent skill · MCP server spec · Checklist / SOP · Decision tree / framework canvas ·
Eval rubric · Template · Workflow / runbook. An off-menu type is rejected with the menu shown.

## Generate a kit scaffold

```bash
python3 skills/field-kit-generator/scripts/field_kit_generator.py generate <slug> \
  --type "Agent skill" \
  --source "Field Manual 02 — One Name, Three Jobs" \
  --summary "A Dev-vs-Delta decision tree"
```

Creates `field-kits/<slug>/<primary>` (`SKILL.md` / `PROMPT.md` / `TEMPLATE.md` / `RUBRIC.md` by
type) pre-seeded with the convention sections (names the source, a how-to-run, a **Risks &
unknowns** block, provenance). Then: fill the `(fill in)` sections — or hand the scaffold to
`skillfy` to synthesise the real content — and **add the kit to `field-kits/README.md`'s index**.

## Lint kits

```bash
python3 skills/field-kit-generator/scripts/field_kit_generator.py lint field-kits/            # all + index
python3 skills/field-kit-generator/scripts/field_kit_generator.py lint field-kits/<slug>      # one kit
```

Flags: missing primary doc, no named source, no run instructions, no RISKS/unknowns
acknowledgement, and (for the whole dir) any kit absent from the README index. This is the
index-lint U1 referenced; wire it into CI alongside link-freshness when convenient.

## How an agent uses this (the two layers)

1. **Scaffold** with `generate` to get a convention-correct skeleton.
2. **Synthesise** the substance with `skillfy`/`skill-distillery` (this tool deliberately does not
   reimplement that). `skillfy` brings the honest-edges / discernment-check shape.
3. **Lint** before publishing — a kit that doesn't name its source or mark RISKS does not ship.

## Verify

```bash
python3 -m unittest discover -s skills/field-kit-generator/tests -p 'test_*.py'
```

Oracle: the lint **passes the real Post #1 kit** (`delta-discovery-protocol`) and **fails** a
malformed one; off-menu types and bad slugs are rejected; a scaffold passes its own lint.

## Provenance

Built for FDE-os (roadmap U8, KTD5). The skill that mints Field Kits is itself convention, not
content — the content comes from `skillfy`.
