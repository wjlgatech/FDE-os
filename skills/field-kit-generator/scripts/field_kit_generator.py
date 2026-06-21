#!/usr/bin/env python3
"""field-kit-generator — scaffold and lint Field Kits to the Delta convention.

A Field Kit is the forkable "R" of a TRUE post. This tool enforces the *convention* (the Field
Kit menu + folder layout + names-its-source + marks-unknowns-as-RISKS); the actual skill synthesis
is delegated to `skillfy`/`skill-distillery` (KTD5 — thin wrapper, not a reimplementation). The
convention-enforcement core is deterministic and offline; the skillfy enrichment is optional.

Subcommands:
  generate  scaffold a new field-kits/<slug>/ kit of a menu-valid type, naming its source article
  lint      check a kit folder (or all of field-kits/) against the convention + index

Usage:
  python3 field_kit_generator.py generate <slug> --type "Agent skill" \
      --source "Field Manual 02 — One Name, Three Jobs" --summary "Dev-vs-Delta decision tree"
  python3 field_kit_generator.py lint field-kits/            # lint all kits + index
  python3 field_kit_generator.py lint field-kits/delta-discovery-protocol
"""
from __future__ import annotations

import argparse
import os
import re
import sys

# The Field Kit menu (Delta-TRUE-article-spec.md). A kit is exactly one of these.
KIT_MENU = {
    "Prompt": "PROMPT.md",
    "Agent skill": "SKILL.md",
    "MCP server spec": "SKILL.md",
    "Checklist / SOP": "SKILL.md",
    "Decision tree / framework canvas": "SKILL.md",
    "Eval rubric": "RUBRIC.md",
    "Template": "TEMPLATE.md",
    "Workflow / runbook": "SKILL.md",
}
PRIMARY_DOCS = ("SKILL.md", "PROMPT.md", "TEMPLATE.md", "RUBRIC.md")


# ---------------------------------------------------------------- generate

def scaffold_kit(field_kits_dir: str, slug: str, kit_type: str, source: str, summary: str) -> str:
    """Create field-kits/<slug>/<primary>. Deterministic. Returns the primary doc path.
    Raises ValueError on an off-menu type so the caller sees the menu."""
    if kit_type not in KIT_MENU:
        raise ValueError(
            f"'{kit_type}' is not in the Field Kit menu. Pick one of:\n  - "
            + "\n  - ".join(KIT_MENU)
        )
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", slug):
        raise ValueError(f"slug must be kebab-case [a-z0-9-]: got '{slug}'")
    kit_dir = os.path.join(field_kits_dir, slug)
    os.makedirs(kit_dir, exist_ok=True)
    primary = KIT_MENU[kit_type]
    path = os.path.join(kit_dir, primary)

    if primary == "SKILL.md":
        body = (
            f"---\nname: {slug}\n"
            f"description: {summary} Use when ... (fill in). Marks unknowns as RISKS, never invents.\n"
            f"---\n\n# {slug}\n\n"
            f"> Field Kit ({kit_type}) for: **{source}**.\n\n"
            "## When to run this\n\n- (fill in the trigger conditions)\n\n"
            "## How to run it\n\n1. (fill in step 1)\n\n"
            "## Risks & unknowns (do NOT invent — list gaps)\n\n- (mark every gap as a RISK)\n\n"
            f"## Provenance\n\nDistilled for the Delta series from **{source}**. Synthesis via "
            "`skillfy` / `skill-distillery`; this scaffold enforces the Field Kit convention.\n"
        )
    else:
        kind = {"PROMPT.md": "prompt", "TEMPLATE.md": "template", "RUBRIC.md": "eval rubric"}[primary]
        body = (
            f"# {slug} ({kit_type})\n\n"
            f"> Field Kit ({kit_type}) for: **{source}**. {summary}\n\n"
            f"## How to run it\n\n(fill in how to use this {kind})\n\n"
            "## Risks & unknowns (do NOT invent — list gaps)\n\n- (mark every gap as a RISK)\n\n"
            f"## Provenance\n\nDistilled for the Delta series from **{source}**.\n"
        )
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(body)
    return path


# ---------------------------------------------------------------- lint

def lint_kit(kit_dir: str) -> list[str]:
    """Return a list of convention problems for one kit folder (empty = passes)."""
    problems: list[str] = []
    slug = os.path.basename(kit_dir.rstrip("/"))
    present = [d for d in PRIMARY_DOCS if os.path.isfile(os.path.join(kit_dir, d))]
    if not present:
        problems.append(f"{slug}: no primary doc ({'/'.join(PRIMARY_DOCS)})")
        return problems
    text = ""
    for d in present:
        with open(os.path.join(kit_dir, d), encoding="utf-8") as fh:
            text += fh.read() + "\n"
    low = text.lower()
    # names a source article
    if not re.search(r"field manual|delta|source|provenance|distilled|for:\s*\*\*", low):
        problems.append(f"{slug}: does not name its source article")
    # has run instructions
    if not re.search(r"how to run|how to use|when to run|## how|run it", low):
        problems.append(f"{slug}: no run instructions")
    # acknowledges RISKS / unknowns
    if "risk" not in low and "unknown" not in low:
        problems.append(f"{slug}: no RISKS/unknowns acknowledgement (never-invent rule)")
    return problems


def lint_index(field_kits_dir: str) -> list[str]:
    """Every kit subdir must appear in field-kits/README.md; lint each kit."""
    problems: list[str] = []
    readme = os.path.join(field_kits_dir, "README.md")
    index_text = ""
    if os.path.isfile(readme):
        with open(readme, encoding="utf-8") as fh:
            index_text = fh.read()
    else:
        problems.append("field-kits/README.md (index) is missing")

    for name in sorted(os.listdir(field_kits_dir)):
        kit_dir = os.path.join(field_kits_dir, name)
        if not os.path.isdir(kit_dir):
            continue
        problems.extend(lint_kit(kit_dir))
        if index_text and name not in index_text:
            problems.append(f"{name}: not listed in the field-kits/README.md index")
    return problems


# ---------------------------------------------------------------- cli

def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)

    g = sub.add_parser("generate")
    g.add_argument("slug")
    g.add_argument("--type", required=True, dest="kit_type")
    g.add_argument("--source", required=True)
    g.add_argument("--summary", required=True)
    g.add_argument("--field-kits", default="field-kits")

    l = sub.add_parser("lint")
    l.add_argument("target", help="a kit folder, or field-kits/ to lint all + index")

    args = ap.parse_args()

    if args.cmd == "generate":
        try:
            path = scaffold_kit(args.field_kits, args.slug, args.kit_type, args.source, args.summary)
        except ValueError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2
        print(f"scaffolded {path} — fill the (fill in) sections, then run skillfy to synthesise.")
        print("Remember: add the kit to field-kits/README.md's index table.")
        return 0

    # lint
    base = os.path.basename(args.target.rstrip("/"))
    problems = lint_index(args.target) if base in ("field-kits", "") or os.path.isfile(
        os.path.join(args.target, "README.md")) else lint_kit(args.target)
    if problems:
        print("FAIL — Field Kit convention problems:")
        for p in problems:
            print(f"  - {p}")
        return 1
    print("OK — Field Kit(s) pass the convention lint.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
