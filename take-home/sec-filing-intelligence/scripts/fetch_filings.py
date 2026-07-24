#!/usr/bin/env python3
"""fetch_filings — the ONLY networked step, run once, EDGAR-budget-documented.

The assignment's reality: the primary corpus is a purchased PDF archive; the
live EDGAR API is a constrained resource. This script respects that boundary:

  * 2 calls to data.sec.gov/submissions/ — "identify which filings exist"
    (explicitly permitted use)
  * 4 calls to download the primary documents
  * TOTAL: 6 requests, ~1s apart, honest User-Agent per SEC policy

The documents are then printed to PDF (headless Chromium) — reproducing the
"bulk PDF archive" condition — and extracted with `pdftotext -layout` into
page-anchored JSON under corpus/extracted/ (checked in, with the PDF SHA256
so provenance survives even though the PDFs themselves are gitignored).

CI never runs this. The pipeline and all tests run on the checked-in
extractions — offline, deterministic.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import time
import urllib.request

UA = "Paul Wu wjlgatech@gmail.com (FDE-os take-home; low-volume)"
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
ARCHIVE = os.path.join(ROOT, "archive")
EXTRACTED = os.path.join(ROOT, "corpus", "extracted")

FILINGS = [
    # (doc_id, cik, accession, primary_doc, company, form, period_end, filed)
    ("tesla-10k-fy2025", "1318605", "0001628280-26-003952", "tsla-20251231.htm",
     "Tesla", "10-K", "2025-12-31", "2026-01-29"),
    ("tesla-10q-q2-2026", "1318605", "0001628280-26-049270", "tsla-20260630.htm",
     "Tesla", "10-Q", "2026-06-30", "2026-07-23"),
    ("tesla-10q-q1-2026", "1318605", "0001628280-26-026673", "tsla-20260331.htm",
     "Tesla", "10-Q", "2026-03-31", "2026-04-23"),
    ("apple-10k-fy2025", "320193", "0000320193-25-000079", "aapl-20250927.htm",
     "Apple", "10-K", "2025-09-27", "2025-10-31"),
]

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"


def fetch(url: str, dest: str) -> None:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r, open(dest, "wb") as f:
        f.write(r.read())
    time.sleep(1)  # stay far under EDGAR's 10 req/s ceiling


def main() -> int:
    os.makedirs(ARCHIVE, exist_ok=True)
    os.makedirs(EXTRACTED, exist_ok=True)
    for doc_id, cik, acc, doc, company, form, period_end, filed in FILINGS:
        htm = os.path.join(ARCHIVE, f"{doc_id}.htm")
        pdf = os.path.join(ARCHIVE, f"{doc_id}.pdf")
        txt = os.path.join(ARCHIVE, f"{doc_id}.txt")
        url = (f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/"
               f"{acc.replace('-', '')}/{doc}")
        if not os.path.exists(htm):
            print(f"fetch {url}")
            fetch(url, htm)
        subprocess.run([CHROME, "--headless", "--disable-gpu",
                        "--no-pdf-header-footer", f"--print-to-pdf={pdf}",
                        f"file://{htm}"], check=True, capture_output=True)
        subprocess.run(["pdftotext", "-layout", pdf, txt], check=True)
        text = open(txt, encoding="utf-8", errors="replace").read()
        pages = [{"page": i + 1, "lines": p.splitlines()}
                 for i, p in enumerate(text.split("\f"))]
        rec = {"doc_id": doc_id, "company": company, "cik": cik, "form": form,
               "period_end": period_end, "filed": filed, "accession": acc,
               "primary_doc": doc, "source_url": url,
               "pdf_sha256": hashlib.sha256(open(pdf, "rb").read()).hexdigest(),
               "extractor": "pdftotext -layout (poppler) over chromium print-to-pdf",
               "pages": pages}
        out = os.path.join(EXTRACTED, f"{doc_id}.json")
        json.dump(rec, open(out, "w"), indent=1)
        print(f"  → {out}: {len(pages)} pages")
    return 0


if __name__ == "__main__":
    sys.exit(main())
