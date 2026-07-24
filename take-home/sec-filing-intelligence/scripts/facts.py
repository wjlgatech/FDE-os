#!/usr/bin/env python3
"""facts — layout-aware financial-statement parsing: PDF text → structured facts.

The assignment's §5 asks the load-bearing question: how do you pull a specific
number out of a financial table, and why that mechanism? Answer implemented
here: DETERMINISTIC layout parsing, not embeddings. An embedding model is
optimized to place topically-similar text near in vector space — it does not
encode numeric magnitude, table position, or the difference between
"Net income" and "Net income attributable to common stockholders" three rows
apart. A financial table is a coordinate system (row label × period column);
we parse the coordinate system.

Mechanism per page of `pdftotext -layout` output:
  1. Detect the period header — duration ("Year Ended December 31," /
     "Three|Six Months Ended June 30,") followed by a year row, or an
     instant header (two full dates → balance-sheet columns).
  2. Detect the scale sentinel ("in millions", "in thousands") — carried
     forward within the document like the statements themselves do.
  3. Under an active header, a line whose trailing numeric tokens COUNT-MATCH
     the period columns becomes one fact per (label, period, value) — with
     page, line, and the verbatim quote for citation.

Facts keep BOTH members of near-miss label pairs as distinct rows; the
question layer must disambiguate explicitly (see qa.py) — never silently.
"""
from __future__ import annotations

import glob
import json
import os
import re

_HERE = os.path.dirname(os.path.abspath(__file__))
EXTRACTED = os.path.join(os.path.dirname(_HERE), "corpus", "extracted")

MONTH_Q = {"March": "Q1", "June": "Q2", "September": "Q3", "December": "Q4"}
_YEAR_RE = re.compile(r"\b(20\d{2})\b")
_FULLDATE_RE = re.compile(
    r"(January|February|March|April|May|June|July|August|September|October|"
    r"November|December)\s+\d{1,2},\s+(20\d{2})")
_MONEY_RE = re.compile(r"\$?\s*\(?-?\d[\d,]*(?:\.\d+)?\)?\s*%?")
_SCALE_RE = re.compile(r"in (millions|thousands|billions)", re.I)
_INSTANT_SPLIT_RE = re.compile(
    r"(?:January|February|March|April|May|June|July|August|September|October|"
    r"November|December)\s+\d{1,2},(?!\s*20\d{2})")
# A statement title is a HEADING: the stripped line is exactly the title (plus
# an optional "(unaudited)"). Full-match kills two real 10-K/10-Q noise classes:
# prose mentions ("…in the consolidated balance sheets were as follows", the VIE
# note p.143) and table-of-contents rows ("Consolidated Balance Sheets   49").
_SECTION_RE = re.compile(
    r"consolidated (?:balance sheets|statements? of (?:operations|income|"
    r"comprehensive income|cash flows))(?: \(unaudited\))?", re.I)


def _page_section(lines: list[str]) -> str | None:
    for line in lines[:20]:
        if _SECTION_RE.fullmatch(line.strip().lower()):
            return line.strip().upper()
    return None


def _parse_money(tok: str):
    t = tok.strip()
    if t.endswith("%"):
        return None  # percent columns are derived, never facts
    neg = "(" in t
    t = t.strip("$() ").replace(",", "")
    if not t or not re.fullmatch(r"-?\d+(?:\.\d+)?", t):
        return None
    v = float(t)
    return -v if neg else v


def _trailing_values(line: str):
    """Split a table line into (label, [values]) — numbers must trail the label."""
    matches = list(_MONEY_RE.finditer(line))
    vals, label_end = [], len(line)
    for m in reversed(matches):
        tail = line[m.end():label_end].strip()
        if tail not in ("", "$"):
            break
        v = _parse_money(m.group())
        if v is None:  # a % token — keep scanning left (MD&A change tables)
            label_end = m.start()
            continue
        vals.insert(0, v)
        label_end = m.start()
    label = line[:label_end].strip().rstrip("$").strip()
    return label, vals


def _header_periods(lines: list[str], i: int, fiscal_year_of) -> list[str] | None:
    """Period columns from a header at line i (+ its year row within 3 lines)."""
    line = lines[i]
    groups = []  # (kind, month) in order of appearance
    for m in re.finditer(r"(Year|Years|Three Months|Six Months|Nine Months)\s+[Ee]nded", line):
        kind = m.group(1)
        after = line[m.end():]
        dm = _FULLDATE_RE.search(after) or re.search(r"(January|February|March|April|May|June|July|August|September|October|November|December)", after)
        month = dm.group(1) if dm else None
        groups.append((kind, month))
    if not groups:
        # A dates row can be the tail of a duration header ("Years ended" on the
        # line above) — that's Apple's shape; never re-read it as an instant header.
        prev = lines[i - 1] if i > 0 else ""
        if re.search(r"[Ee]nded\s*$", prev.strip()):
            return None
        # instant header: a line with >=2 full dates = balance-sheet columns
        dates = _FULLDATE_RE.findall(line)
        if len(dates) >= 2:
            return [f"AsOf-FY{fiscal_year_of(y)}" for _, y in dates]
        # split instant header: "December 31,   December 31," (years on a later row)
        if len(_INSTANT_SPLIT_RE.findall(line)) >= 2:
            for j in range(i + 1, min(i + 4, len(lines))):
                years = _YEAR_RE.findall(lines[j])
                if len(years) >= 2:
                    return [f"AsOf-FY{fiscal_year_of(y)}" for y in years]
        return None
    # find the year row (or dates embedded in header for Apple-style "Years ended")
    for j in range(i, min(i + 4, len(lines))):
        years = _YEAR_RE.findall(lines[j])
        if j == i and len(groups) * 2 > len(years):
            continue
        if len(years) >= 2:
            periods, yi = [], 0
            per_group = len(years) // len(groups)
            for kind, month in groups:
                for _ in range(per_group):
                    if yi >= len(years):
                        break
                    y = years[yi]; yi += 1
                    if kind in ("Year", "Years"):
                        periods.append(f"FY{fiscal_year_of(y)}")
                    elif kind == "Three Months":
                        periods.append(f"{MONTH_Q.get(month, 'Q?')}-{y}")
                    elif kind == "Six Months":
                        periods.append(f"6M-{y}")
                    else:
                        periods.append(f"9M-{y}")
            return periods or None
    return None


def load_facts(extracted_dir: str = EXTRACTED) -> list[dict]:
    facts = []
    for path in sorted(glob.glob(os.path.join(extracted_dir, "*.json"))):
        doc = json.load(open(path))
        fiscal_year_of = lambda y: y  # both Tesla (Dec) and Apple (Sep) label FY by calendar year of period end
        scale = "millions"
        for page in doc["pages"]:
            lines = page["lines"]
            section = _page_section(lines)
            periods = None
            for i, line in enumerate(lines):
                sm = _SCALE_RE.search(line)
                if sm:
                    scale = sm.group(1).lower()
                hp = _header_periods(lines, i, fiscal_year_of)
                if hp:
                    periods = hp
                    continue
                if not periods:
                    continue
                label, vals = _trailing_values(line)
                if (label and label[0].isalpha() and len(vals) == len(periods)
                        and len(vals) >= 2):
                    per_share = bool(re.search(r"\d\.\d\d", line)) and all(
                        abs(v) < 10000 for v in vals) and any("." in t for t in line.split()[-len(vals):])
                    for p, v in zip(periods, vals):
                        facts.append({
                            "company": doc["company"], "doc_id": doc["doc_id"],
                            "form": doc["form"], "filed": doc["filed"],
                            "period_end": doc["period_end"],
                            "label": label, "period": p, "value": v,
                            "section": section,
                            "scale": "per_share_usd" if per_share else scale,
                            "page": page["page"], "line": i + 1,
                            "quote": line.strip(),
                            "source_url": doc["source_url"],
                        })
    return facts


# Canonical metric registry — label match is EXACT (case-insensitive) on the
# cleaned row label, so "Net income" and "Net income attributable to common
# stockholders" stay distinct facts. `duration` metrics live on FY/Qn/6M
# periods; `instant` metrics on AsOf periods.
CANONICALS = {
    "total_revenue": {"labels": ["total revenues", "total net sales"], "kind": "duration"},
    "gross_profit": {"labels": ["gross profit", "total gross profit"], "kind": "duration"},
    "operating_income": {"labels": ["income from operations", "operating income"], "kind": "duration"},
    "net_income": {"labels": ["net income"], "kind": "duration"},
    "net_income_attributable": {"labels": ["net income attributable to common stockholders"], "kind": "duration"},
    "research_development": {"labels": ["research and development"], "kind": "duration"},
    "sga": {"labels": ["selling, general and administrative"], "kind": "duration"},
    "operating_cash_flow": {"labels": ["net cash provided by operating activities"], "kind": "duration"},
    "diluted_eps": {"labels": ["diluted"], "kind": "duration", "per_share": True},
    "cash_and_equivalents": {"labels": ["cash and cash equivalents"], "kind": "instant"},
    "total_assets": {"labels": ["total assets"], "kind": "instant"},
    "total_liabilities": {"labels": ["total liabilities"], "kind": "instant"},
}


def find_metric(facts: list[dict], company: str, canonical: str, period: str):
    """All matching facts + the near-miss candidates that ALSO matched the
    metric's family — the caller must surface ambiguity, not swallow it."""
    spec = CANONICALS[canonical]
    hits, near = [], []
    for f in facts:
        if f["company"].lower() != company.lower():
            continue
        label = f["label"].lower().rstrip(":")
        if spec["kind"] == "instant":
            # An instant metric lives ONLY on balance-sheet (AsOf) columns —
            # the cash-flow statement's "cash at end of period" rows sit under
            # duration columns and must not answer a balance-sheet question.
            if f["period"] != f"AsOf-{period}":
                continue
        elif f["period"] != period:
            continue
        if spec.get("per_share") and f["scale"] != "per_share_usd":
            continue
        if not spec.get("per_share") and f["scale"] == "per_share_usd":
            continue
        if label in spec["labels"]:
            hits.append(f)
        elif any(l in label for l in spec["labels"]):
            near.append(f)  # e.g. "net income attributable to …" when asking net_income
    # Prefer facts from the audited consolidated statements over note/quarterly
    # tables that reuse the same row label (real 10-K noise, observed pp. 131/145).
    stmt = [f for f in hits if f.get("section")]
    if stmt:
        hits = stmt
    if spec["kind"] == "instant":
        bs = [f for f in hits if f.get("section") == "CONSOLIDATED BALANCE SHEETS"]
        if bs:
            hits = bs
    # duplicates of the same (label, value) across statements/pages: keep first
    seen, uniq = set(), []
    for f in hits:
        k = (f["label"].lower(), f["value"])
        if k not in seen:
            seen.add(k)
            uniq.append(f)
    return uniq, near


if __name__ == "__main__":
    fs = load_facts()
    print(f"{len(fs)} facts extracted")
    for c in ("Tesla", "Apple"):
        n = sum(1 for f in fs if f["company"] == c)
        print(f"  {c}: {n}")
