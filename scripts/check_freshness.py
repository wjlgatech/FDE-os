#!/usr/bin/env python3
"""Link-freshness checker for FDE-os references. Stdlib only, CI-safe.

Classifier (matches the living-repo policy the roadmap U1 references):
  - GONE  (fails CI): HTTP 404 / 410, or a DNS/connection failure.
  - WARN  (non-fail): 403 / 405 / 406 / 429 / 999 and other refusals — a bot wall is
          not a dead link. Known bot-walled domains are WARN by default.
  - OK:   2xx / 3xx.

Usage:
  python3 scripts/check_freshness.py README.md field-kits/README.md --report freshness-report.md
Exit code 1 iff any link is GONE.
"""
from __future__ import annotations

import argparse
import re
import sys
import urllib.error
import urllib.request
from urllib.parse import urlparse

# Domains that wall bots with a 4xx but are live in a browser — treat as WARN, never GONE.
BOT_WALLED = (
    "x.com", "twitter.com", "linkedin.com", "scholar.google.com", "openreview.net",
    "img.shields.io", "openai.com", "anthropic.com", "a16z.com", "sequoiacap.com",
    "substack.com", "bloomberry.com",
)
GONE_STATUSES = {404, 410}
WARN_STATUSES = {401, 403, 405, 406, 429, 999}

URL_RE = re.compile(r"https?://[^\s)>\]\"'`]+")
TRAILING = ".,;:!?)]}>\"'"


def extract_urls(paths: list[str]) -> list[tuple[str, str]]:
    """Return (url, source_file) pairs, deduped, order-preserved."""
    seen: set[str] = set()
    out: list[tuple[str, str]] = []
    for path in paths:
        try:
            text = open(path, encoding="utf-8").read()
        except OSError as exc:
            print(f"warning: cannot read {path}: {exc}", file=sys.stderr)
            continue
        for m in URL_RE.finditer(text):
            url = m.group(0).rstrip(TRAILING)
            if url not in seen:
                seen.add(url)
                out.append((url, path))
    return out


def probe(url: str) -> tuple[str, str]:
    """Return (status_class, detail). status_class in {OK, WARN, GONE}."""
    domain = (urlparse(url).hostname or "").lower()
    bot_walled = any(domain == d or domain.endswith("." + d) for d in BOT_WALLED)

    def _request(method: str):
        req = urllib.request.Request(url, method=method, headers={"User-Agent": "Mozilla/5.0 (FDE-os freshness)"})
        return urllib.request.urlopen(req, timeout=15)

    for method in ("HEAD", "GET"):
        try:
            resp = _request(method)
            code = resp.getcode() or 200
            return ("OK", f"{code}")
        except urllib.error.HTTPError as exc:
            code = exc.code
            if code in GONE_STATUSES:
                return ("GONE", f"{code}")
            if bot_walled or code in WARN_STATUSES:
                # bot wall / refusal — try GET once more, else WARN
                if method == "HEAD":
                    continue
                return ("WARN", f"{code} (bot-walled)" if bot_walled else f"{code}")
            # Other 4xx/5xx: WARN (don't fail CI on a flaky upstream)
            if method == "GET":
                return ("WARN", f"{code}")
        except (urllib.error.URLError, OSError) as exc:
            reason = getattr(exc, "reason", exc)
            if "Name or service not known" in str(reason) or "nodename nor servname" in str(reason):
                return ("GONE", "dns-failure")
            if method == "GET":
                return ("WARN", f"transport: {reason}")
    return ("WARN", "unresolved")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="+", help="Markdown files to scan for URLs")
    ap.add_argument("--report", default=None, help="Write a markdown report to this path")
    args = ap.parse_args()

    urls = extract_urls(args.files)
    rows: list[tuple[str, str, str, str]] = []
    gone = 0
    for url, src in urls:
        cls, detail = probe(url)
        if cls == "GONE":
            gone += 1
        rows.append((cls, url, detail, src))

    lines = ["# Link freshness report", ""]
    lines.append(f"Checked {len(rows)} links — {gone} GONE, "
                 f"{sum(1 for r in rows if r[0] == 'WARN')} WARN, "
                 f"{sum(1 for r in rows if r[0] == 'OK')} OK.")
    lines.append("")
    lines.append("| Status | URL | Detail | Source |")
    lines.append("|---|---|---|---|")
    for cls, url, detail, src in sorted(rows, key=lambda r: {"GONE": 0, "WARN": 1, "OK": 2}[r[0]]):
        lines.append(f"| {cls} | {url} | {detail} | {src} |")
    report = "\n".join(lines) + "\n"

    if args.report:
        open(args.report, "w", encoding="utf-8").write(report)
    print(report)

    if gone:
        print(f"FAIL: {gone} dead link(s) (404/410/dns-failure).", file=sys.stderr)
        return 1
    print("OK: no dead links (bot-walled/refused links are warnings, not failures).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
