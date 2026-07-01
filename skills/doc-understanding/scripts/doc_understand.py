#!/usr/bin/env python3
"""doc-understanding — messy enterprise docs -> canonical structured representation + parse-quality gate.

The moat named by a real regulated FDE engagement (docs/field-notes/2026-07-01): OCR is not
enough; the hard part is OOXML structure — tables with merged cells, track-changes, headings —
and an honest *parse-quality* score, because Output Quality <= Input Representation Quality.

Formats (pure stdlib — zipfile + ElementTree, no OCR, no binary .doc/.xls):
  .docx  paragraphs, heading levels, tables (gridSpan/vMerge resolved), track-changes counts
  .xlsx  sheets -> dense row grids (sharedStrings + inline strings), merged-range counts
  .md/.markdown/.txt  headings + paragraphs (the trivial case, kept for a uniform interface)
  .csv   one table

Canonical representation (JSON):
  {source, format, blocks: [{type: heading|paragraph|table, ...}],
   revisions: {insertions, deletions, clean}, quality: {coverage, structure, fidelity, overall}}

Gate discipline: no evidence => NO-GO. An empty or unparseable doc scores 0 — never a fake pass.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import re
import sys
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
S_NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"


def _w(tag: str) -> str:
    """Qualified wordprocessingml tag."""
    return f"{{{W_NS}}}{tag}"


def _s(tag: str) -> str:
    """Qualified spreadsheetml tag."""
    return f"{{{S_NS}}}{tag}"


# ----------------------------------------------------------------- DOCX

def _para_text(p: ET.Element) -> str:
    """Visible text of a paragraph: keep w:t and inserted runs, drop w:delText (deleted)."""
    parts: list[str] = []
    for t in p.iter(_w("t")):
        parts.append(t.text or "")
    return "".join(parts)


def _para_style(p: ET.Element) -> str:
    """Paragraph style id (e.g. 'Heading1'), or '' when unstyled."""
    style = p.find(f"{_w('pPr')}/{_w('pStyle')}")
    return style.get(_w("val"), "") if style is not None else ""


def _heading_level(style: str) -> int:
    """Heading level from a style id like Heading2/heading 2; 0 = not a heading."""
    m = re.match(r"heading\s*(\d)", style, re.IGNORECASE)
    return int(m.group(1)) if m else 0


def _cell_values(tc: ET.Element) -> list[str | None]:
    """One w:tc -> its grid slots: text (or None for a vMerge continuation), padded per gridSpan."""
    pr = tc.find(_w("tcPr"))
    span, vmerge_cont = 1, False
    if pr is not None:
        gs = pr.find(_w("gridSpan"))
        if gs is not None:
            span = int(gs.get(_w("val"), "1"))
        vm = pr.find(_w("vMerge"))
        # A vMerge element without val="restart" continues the cell above.
        vmerge_cont = vm is not None and vm.get(_w("val"), "continue") != "restart"
    text = " ".join(filter(None, (_para_text(p) for p in tc.findall(_w("p"))))).strip()
    return [None if vmerge_cont else text] + [None] * (span - 1)


def _table_rows(tbl: ET.Element) -> list[list[str | None]]:
    """Rows with merges resolved: gridSpan pads with None; vMerge-continue cells become None."""
    return [[v for tc in tr.findall(_w("tc")) for v in _cell_values(tc)]
            for tr in tbl.findall(_w("tr"))]


def parse_docx(path: Path) -> dict:
    """Parse a .docx into the canonical representation."""
    with zipfile.ZipFile(path) as zf:
        root = ET.fromstring(zf.read("word/document.xml"))
    body = root.find(_w("body"))
    blocks: list[dict] = []
    for el in (body if body is not None else []):
        if el.tag == _w("p"):
            text = _para_text(el).strip()
            if not text:
                continue
            level = _heading_level(_para_style(el))
            if level:
                blocks.append({"type": "heading", "level": level, "text": text})
            else:
                blocks.append({"type": "paragraph", "text": text})
        elif el.tag == _w("tbl"):
            rows = _table_rows(el)
            merged = sum(1 for r in rows for c in r if c is None)
            blocks.append({"type": "table", "rows": rows, "merged_cells": merged})
    ins = sum(1 for _ in root.iter(_w("ins")))
    dels = sum(1 for _ in root.iter(_w("del")))
    return {
        "source": str(path), "format": "docx", "blocks": blocks,
        "revisions": {"insertions": ins, "deletions": dels, "clean": ins + dels == 0},
    }


# ----------------------------------------------------------------- XLSX

def _shared_strings(zf: zipfile.ZipFile) -> list[str]:
    """The sharedStrings table; rich-text runs are concatenated."""
    if "xl/sharedStrings.xml" not in zf.namelist():
        return []
    root = ET.fromstring(zf.read("xl/sharedStrings.xml"))
    return ["".join(t.text or "" for t in si.iter(_s("t"))) for si in root.findall(_s("si"))]


def _col_index(ref: str) -> int:
    """A1-style column letters -> 0-based index (A=0, AA=26)."""
    n = 0
    for ch in ref:
        if not ch.isalpha():
            break
        n = n * 26 + (ord(ch.upper()) - 64)
    return n - 1


def _cell_value(c: ET.Element, shared: list[str]) -> str | None:
    """One spreadsheet cell -> its string value (shared, inline, or literal), or None."""
    v = c.find(_s("v"))
    if v is None or v.text is None:
        inline = c.find(f"{_s('is')}/{_s('t')}")  # inline strings live under is/t
        return inline.text if inline is not None else None
    return shared[int(v.text)] if c.get("t") == "s" else v.text


def _sheet_grid(root: ET.Element, shared: list[str]) -> list[list[str | None]]:
    """Dense row grid from a worksheet's sparse cell refs."""
    grid: list[list[str | None]] = []
    for row in root.iter(_s("row")):
        cells = {_col_index(c.get("r", "A1")): val
                 for c in row.findall(_s("c"))
                 if (val := _cell_value(c, shared)) is not None}
        width = max(cells, default=-1) + 1
        grid.append([cells.get(i) for i in range(width)])
    return grid


def parse_xlsx(path: Path) -> dict:
    """Parse a .xlsx into the canonical representation (one table block per sheet)."""
    blocks: list[dict] = []
    merged_total = 0
    with zipfile.ZipFile(path) as zf:
        shared = _shared_strings(zf)
        wb = ET.fromstring(zf.read("xl/workbook.xml"))
        names = [sh.get("name", f"sheet{i+1}") for i, sh in enumerate(wb.iter(_s("sheet")))]
        sheet_files = sorted(n for n in zf.namelist()
                             if re.fullmatch(r"xl/worksheets/sheet\d+\.xml", n))
        for i, fn in enumerate(sheet_files):
            root = ET.fromstring(zf.read(fn))
            merged = sum(1 for _ in root.iter(_s("mergeCell")))
            merged_total += merged
            blocks.append({
                "type": "table", "sheet": names[i] if i < len(names) else f"sheet{i+1}",
                "rows": _sheet_grid(root, shared), "merged_cells": merged,
            })
    return {
        "source": str(path), "format": "xlsx", "blocks": blocks,
        "revisions": {"insertions": 0, "deletions": 0, "clean": True},
        "merged_ranges": merged_total,
    }


# ----------------------------------------------------------------- text formats

def parse_markdown(path: Path) -> dict:
    """Markdown/plain text -> headings + paragraphs."""
    blocks: list[dict] = []
    for chunk in re.split(r"\n\s*\n", path.read_text(encoding="utf-8")):
        chunk = chunk.strip()
        if not chunk:
            continue
        m = re.match(r"(#{1,6})\s+(.*)", chunk)
        if m:
            blocks.append({"type": "heading", "level": len(m.group(1)), "text": m.group(2)})
            rest = chunk[m.end():].strip()
            if rest:
                blocks.append({"type": "paragraph", "text": rest})
        else:
            blocks.append({"type": "paragraph", "text": chunk})
    return {"source": str(path), "format": "md", "blocks": blocks,
            "revisions": {"insertions": 0, "deletions": 0, "clean": True}}


def parse_csv(path: Path) -> dict:
    """CSV -> a single table block."""
    with open(path, newline="", encoding="utf-8") as fh:
        rows = [list(r) for r in csv.reader(fh)]
    return {"source": str(path), "format": "csv",
            "blocks": [{"type": "table", "rows": rows, "merged_cells": 0}],
            "revisions": {"insertions": 0, "deletions": 0, "clean": True}}


PARSERS = {".docx": parse_docx, ".xlsx": parse_xlsx, ".md": parse_markdown,
            ".markdown": parse_markdown, ".txt": parse_markdown, ".csv": parse_csv}


def parse(path: str | Path) -> dict:
    """Dispatch by extension; unknown formats refuse honestly instead of guessing."""
    p = Path(path)
    parser = PARSERS.get(p.suffix.lower())
    if parser is None:
        raise ValueError(f"unsupported format '{p.suffix}' — supported: {', '.join(sorted(PARSERS))}. "
                         "Binary .doc/.xls and scanned PDFs need conversion first; refusing to guess.")
    rep = parser(p)
    rep["quality"] = quality(rep)
    return rep


# ----------------------------------------------------------------- parse-quality gate

def quality(rep: dict) -> dict:
    """Score the parse itself (not the document's content) on three 0-1 dimensions.

    coverage  — how much extracted content is non-empty (empty parse -> 0)
    structure — did we recover structure (headings/tables), or just a blob?
    fidelity  — is the text authoritative? unresolved track-changes lower this
    """
    blocks = rep.get("blocks", [])
    texts = [b.get("text", "") for b in blocks if b["type"] in ("heading", "paragraph")]
    cells = [c for b in blocks if b["type"] == "table" for r in b["rows"] for c in r]
    units = texts + cells
    filled = [u for u in units if u not in (None, "")]
    coverage = round(len(filled) / len(units), 3) if units else 0.0

    has_structure = any(b["type"] in ("heading", "table") for b in blocks)
    structure = 1.0 if has_structure else (0.5 if blocks else 0.0)

    rev = rep.get("revisions", {})
    pending = rev.get("insertions", 0) + rev.get("deletions", 0)
    fidelity = round(max(0.0, 1.0 - 0.1 * pending), 3)

    overall = round(0.4 * coverage + 0.3 * structure + 0.3 * fidelity, 3)
    return {"coverage": coverage, "structure": structure, "fidelity": fidelity, "overall": overall}


def gate(rep: dict, threshold: float = 0.7) -> tuple[bool, list[str]]:
    """GO iff overall >= threshold AND something was actually extracted. No evidence => NO-GO."""
    q = rep.get("quality") or quality(rep)
    reasons: list[str] = []
    if not rep.get("blocks"):
        reasons.append("no content extracted — parse produced zero blocks")
    if q["overall"] < threshold:
        reasons.append(f"overall parse quality {q['overall']} < threshold {threshold}")
    if not rep.get("revisions", {}).get("clean", True):
        reasons.append("document has unresolved track-changes — text is not authoritative")
    return (not reasons, reasons)


# ----------------------------------------------------------------- rendering + CLI

def _render_block(b: dict) -> list[str]:
    """Markdown lines for one canonical block (heading, paragraph, or table)."""
    if b["type"] == "heading":
        return ["#" * (b["level"] + 1) + " " + b["text"]]
    if b["type"] == "paragraph":
        return [b["text"] + "\n"]
    lines = [f"**[{b.get('sheet', 'table')}]** {len(b['rows'])} rows, {b['merged_cells']} merged cells"]
    lines += ["| " + " | ".join("·" if c is None else str(c) for c in r) + " |" for r in b["rows"][:20]]
    return lines + [""]


def render_md(rep: dict) -> str:
    """Human-readable view of the canonical representation."""
    q = rep.get("quality", {})
    out = [f"# Parsed: {rep['source']} ({rep['format']})",
           f"quality — coverage {q.get('coverage')} · structure {q.get('structure')} · "
           f"fidelity {q.get('fidelity')} · **overall {q.get('overall')}**", ""]
    rev = rep.get("revisions", {})
    if not rev.get("clean", True):
        out.append(f"⚠ unresolved track-changes: +{rev['insertions']} / -{rev['deletions']}\n")
    for b in rep["blocks"]:
        out.extend(_render_block(b))
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    """CLI: parse <file> [--json] | gate <file> [--threshold]."""
    ap = argparse.ArgumentParser(prog="doc_understand", description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    p_parse = sub.add_parser("parse", help="doc -> canonical representation")
    p_parse.add_argument("file")
    p_parse.add_argument("--json", action="store_true", help="emit canonical JSON (default: markdown)")
    p_gate = sub.add_parser("gate", help="parse-quality gate (exit 1 on NO-GO)")
    p_gate.add_argument("file")
    p_gate.add_argument("--threshold", type=float, default=0.7)
    ns = ap.parse_args(argv)

    rep = parse(ns.file)
    if ns.cmd == "parse":
        print(json.dumps(rep, indent=2) if ns.json else render_md(rep))
        return 0
    ok, reasons = gate(rep, ns.threshold)
    print(f"parse-quality: {rep['quality']['overall']} (threshold {ns.threshold})")
    print("VERDICT: GO" if ok else "VERDICT: NO-GO — " + "; ".join(reasons))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
