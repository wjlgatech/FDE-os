#!/usr/bin/env python3
"""snowflake-os · sync — the ONLY networked component.

Fetches the public learn.snowflake.com catalogue into a committed, offline
snapshot (`snowflake-os/snapshot/catalog.json`). Every other engine in
snowflake-os reads the snapshot and never touches the network, so `make check`
stays offline, deterministic, and fast.

    python3 snowflake-os/scripts/sync.py fetch            # refresh the snapshot
    python3 snowflake-os/scripts/sync.py fetch --limit 5  # smoke test
    python3 snowflake-os/scripts/sync.py drift            # live vs snapshot; exit 3 on drift

Design rules this file obeys (docs/REPO_PLAYBOOK.md):

  * spec-as-data       — WHAT to fetch lives in data/sources.yml, not in here.
  * hostile-DOM        — anchor on URL codes and visible LABEL TEXT. Never on a
                         CSS class: this is a Gatsby/styled-components build and
                         every class name is a content hash that rotates on deploy.
  * no-evidence-means-no — a field whose label is missing is recorded as None and
                         counted as UNMEASURED. We never infer a plausible value.
  * provenance         — every record carries the URL it came from, the sha256 of
                         the exact bytes parsed, and the fetch timestamp.
  * human-gated        — this writes a file. Merging it is a human's PR.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ROOT / "data" / "sources.yml"
SNAPSHOT = ROOT / "snapshot" / "catalog.json"
SCHEMA = "snowflake-os/catalog@1"

# ─────────────────────────── html primitives (stdlib only) ───────────────────


def strip_tags(fragment: str) -> str:
    """Visible text of an HTML fragment, whitespace-collapsed."""
    no_code = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", fragment)
    no_comments = re.sub(r"(?s)<!--.*?-->", " ", no_code)
    text = html.unescape(re.sub(r"(?s)<[^>]+>", " ", no_comments))
    return re.sub(r"\s+", " ", text).strip()


def value_after_label(page: str, label: str, window: int = 400) -> str | None:
    """Text that follows a visible label. The label is the stable anchor.

    Returns None — never a guess — when the label is absent, so callers can
    record the field as UNMEASURED.
    """
    idx = page.find(label)
    if idx < 0:
        return None
    idx += len(label)
    # Resume at the next tag boundary so a half-consumed `</span>` can't leak
    # into the value as the literal text "/span>".
    close = page.find(">", idx)
    if 0 <= close <= idx + 40:
        idx = close + 1
    return strip_tags(page[idx : idx + window]) or None


def first_h1(page: str) -> str | None:
    m = re.search(r"(?is)<h1[^>]*>(.*?)</h1>", page)
    return strip_tags(m.group(1)) if m else None


ORIGIN = "https://learn.snowflake.com"


def hrefs(page: str) -> list[str]:
    """All hrefs, normalised to site-absolute paths.

    The catalogue mixes `/en/courses/X/` with `https://learn.snowflake.com/en/courses/X/`
    for the same target. Matching only the relative form silently drops half the
    graph — which is exactly how a track ends up with an empty sequence.
    """
    out = []
    for h in re.findall(r'href="([^"]+)"', page):
        h = h.strip().split("?")[0].split("#")[0]
        if h.startswith(ORIGIN):
            h = h[len(ORIGIN) :]
        if h.startswith("/"):
            out.append(h)
    return out


def has_badge(page: str, word: str) -> bool:
    """A pill/badge is a short standalone element whose entire text is `word`."""
    return bool(re.search(r">\s*" + re.escape(word) + r"\s*<", page, re.I))


# ─────────────────────────────── fetching ────────────────────────────────────


class Fetcher:
    """Serial, rate-limited, cached GET. The one seam that touches the network."""

    def __init__(self, user_agent: str, delay: float, timeout: float):
        self.user_agent, self.delay, self.timeout = user_agent, delay, timeout
        self._last = 0.0
        self.pages: dict[str, str] = {}
        self._final: dict[str, str] = {}

    def get(self, url: str) -> str:
        return self._fetch(url)[1]

    def resolve(self, url: str) -> str:
        """Final URL after redirects — how a legacy slug reveals its canonical code."""
        return self._fetch(url)[0]

    def _fetch(self, url: str) -> tuple[str, str]:
        if url in self.pages:
            return self._final.get(url, url), self.pages[url]
        wait = self.delay - (time.monotonic() - self._last)
        if wait > 0:
            time.sleep(wait)
        req = urllib.request.Request(url, headers={"User-Agent": self.user_agent})
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            final = resp.geturl()
        self._last = time.monotonic()
        self.pages[url] = body
        self._final[url] = final
        return final, body


def provenance(url: str, page: str, when: str) -> dict:
    return {
        "url": url,
        "sha256": hashlib.sha256(page.encode("utf-8")).hexdigest(),
        "fetched_at": when,
    }


# ─────────────────────────────── parsers ─────────────────────────────────────

# A canonical code is the ALL-CAPS identifier the catalogue itself publishes
# (OD-ESS-DWW, ILT-PDE). Curated track pages still link legacy lowercase slugs
# (uni-essdww101) that 301 to the canonical page — see resolve_course_slug.
COURSE_HREF = re.compile(r"^/en/courses/([A-Za-z0-9][A-Za-z0-9\-]*)/?$")
CANONICAL_CODE = re.compile(r"^[A-Z0-9][A-Z0-9\-]*$")
CERT_HREF = re.compile(r"^/en/certifications/([a-zA-Z0-9\-]+)/?$")


def course_slugs(page: str) -> list[str]:
    """Every course slug a page links to, in document order, deduped."""
    seen, out = set(), []
    for h in hrefs(page):
        if (m := COURSE_HREF.match(h)) and m.group(1) not in seen:
            seen.add(m.group(1))
            out.append(m.group(1))
    return out


def discover_courses(index: str) -> list[str]:
    """Canonical course codes from URL paths on the catalogue index."""
    return sorted(s for s in course_slugs(index) if CANONICAL_CODE.match(s))


def discover_certifications(index: str) -> list[str]:
    slugs = {
        m.group(1)
        for h in hrefs(index)
        if (m := CERT_HREF.match(h)) and m.group(1) not in {"snowpro-examreg"}
    }
    return sorted(slugs)


def resolve_course_slug(slug: str, fetcher: "Fetcher") -> tuple[str | None, str]:
    """Map a linked slug to its canonical catalogue code.

    Returns (code_or_None, how). Snowflake's curated track pages link legacy
    slugs (`uni-essdww101`) which 301 to the canonical page (`OD-ESS-DWW`).
    Matching on the literal slug yields an EMPTY track sequence — a silent,
    plausible-looking wrong answer. We follow the redirect and record how we
    got there; an unresolvable slug returns None and is reported, never dropped.
    """
    if CANONICAL_CODE.match(slug):
        return slug, "direct"
    try:
        final = fetcher.resolve(f"https://learn.snowflake.com/en/courses/{slug}/")
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError):
        return None, "unresolved:fetch-failed"
    if m := re.search(r"/en/courses/([A-Za-z0-9\-]+)/?$", final):
        code = m.group(1)
        if CANONICAL_CODE.match(code):
            return code, "redirect"
    return None, "unresolved:no-canonical-target"


def parse_course(code: str, url: str, page: str, when: str) -> dict:
    """One course detail page → a record. Missing label ⇒ None ⇒ UNMEASURED."""
    effort_raw = value_after_label(page, "Estimated Effort (hours)", window=300)
    hours, difficulty = None, None
    if effort_raw:
        if m := re.search(r"(\d+(?:\.\d+)?)", effort_raw):
            hours = float(m.group(1))
            hours = int(hours) if hours.is_integer() else hours
        if m := re.search(r"\(\s*([A-Za-z ]+?)\s*\)", effort_raw):
            difficulty = m.group(1).strip()

    stated_code = value_after_label(page, "Course Number", window=120)
    if stated_code:
        stated_code = stated_code.split(" ")[0].strip()

    # Summary: the prose the page leads with, after the <h1>. Strip tags over
    # the WHOLE remainder before slicing — slicing raw HTML first can cut inside
    # a <style> block and leak emotion CSS into the summary as body text.
    title = first_h1(page)
    summary = None
    if title:
        summary = strip_tags(page.split("</h1>", 1)[-1])[:600] or None

    delivery = (
        "instructor-led"
        if has_badge(page, "Instructor Led") or code.startswith("ILT-")
        else "on-demand"
    )
    return {
        "code": code,
        "title": title,
        "url": url,
        "delivery": delivery,
        "free": has_badge(page, "Free"),
        "effort_hours": hours,
        "difficulty": difficulty,
        # Cross-check: the code in the URL vs the code the page states. A
        # mismatch is surfaced, never silently reconciled.
        "code_confirmed_on_page": (stated_code == code) if stated_code else None,
        "summary": summary,
        "provenance": provenance(url, page, when),
    }


def parse_certification(slug: str, url: str, page: str, when: str) -> dict:
    text = strip_tags(page)
    exam_code = None
    if m := re.search(r"\b([A-Z]{3}-[A-Z]?\d{2})\b", text):
        exam_code = m.group(1)

    tests: list[str] = []
    if m := re.search(r"ability to:?\s*(.+?)(?:CANDIDATE|Access the Exam|RECOMMENDED)", text, re.I):
        for seg in re.split(r"\s*•\s*", m.group(1)):
            seg = seg.strip(" .;")
            # The last bullet runs into the next ALL-CAPS section heading
            # ("… Model Registry SNOWPRO SPECIALTY: GEN AI"). Cut there.
            seg = re.split(r"\s(?=(?:[A-Z]{4,}[:®\s]){2,})", seg)[0].strip(" .;")
            if len(seg) > 25:
                tests.append(seg)
        tests = tests[:8]

    candidate = None
    if m := re.search(r"CANDIDATE\s*(.+?)(?:RECOMMENDED|Access the Exam)", text, re.I):
        candidate = m.group(1).strip()[:500] or None

    # Every exam page carries the SAME boilerplate FAQ quoting $175 (Core) and
    # $375 (Advanced series). Specialty pricing is simply not published there.
    # So we attribute a price ONLY to the family the sentence actually names,
    # and leave Specialty as None = UNMEASURED rather than borrowing a number
    # that happens to be sitting on the page.
    lower = slug.lower()
    cost = None
    if ("adv" in lower or "advanced" in lower) and re.search(
        r"Advanced Certification series is \$(\d+)", text
    ):
        cost = int(re.search(r"Advanced Certification series is \$(\d+)", text).group(1))
    elif "core" in lower and re.search(r"Core Certification cost is \$(\d+)", text):
        cost = int(re.search(r"Core Certification cost is \$(\d+)", text).group(1))

    # Snowflake publishes the same exam as several localised pages. They are one
    # exam, not five, and a "how many certifications?" answer must not count pages.
    lang = next(
        (code for marker, code in
         (("jpn", "ja"), ("-esp", "es"), ("-fra", "fr"), ("kor", "ko")) if marker in lower),
        "en",
    )
    return {
        "slug": slug,
        "exam_code": exam_code,
        "title": first_h1(page),
        "url": url,
        "kind": "practice-exam" if "practice" in lower else "certification",
        "language": lang,
        "tests": tests,
        "tests_measured": bool(tests),
        "candidate_profile": candidate,
        "exam_cost_usd": cost,
        "exam_cost_measured": cost is not None,
        "provenance": provenance(url, page, when),
    }


def parse_track(spec: dict, page: str, when: str, fetcher: "Fetcher") -> dict:
    """A track page lists its courses in the site's own curated order."""
    sequence, aliases, unresolved = [], {}, []
    for slug in course_slugs(page):
        if slug in {"", "en"}:
            continue
        code, how = resolve_course_slug(slug, fetcher)
        if code is None:
            unresolved.append({"slug": slug, "reason": how})
            continue
        if how == "redirect":
            aliases[slug] = code
        if code not in sequence:
            sequence.append(code)
    return {
        "slug": spec["slug"],
        "title": spec.get("title") or first_h1(page),
        "url": spec["url"],
        "sequence": sequence,
        "sequence_published": bool(sequence),
        "sequence_source": "site-curated order on the track page",
        "sequence_note": None
        if sequence
        else "not published in HTML — the track page links the catalogue and exam registration, not its courses",
        "legacy_slug_aliases": aliases,
        "unresolved_links": unresolved,
        "provenance": provenance(spec["url"], page, when),
    }


def parse_role(spec: dict, page: str, when: str) -> dict:
    """A role journey page.

    HONEST EDGE: as of the 2026-08-03 sync these twelve pages describe the role
    in prose and link to the *catalogue* — they do NOT enumerate their courses in
    HTML. So `courses` is empty and `courses_published` says why. Snowflake's
    role→course mapping is not machine-readable; snowflake-os supplies its own
    in data/competencies.yml, labelled `curated`, rather than inventing one here
    and passing it off as Snowflake's.
    """
    linked = [s for s in course_slugs(page) if s not in {"", "en"}]
    cert_slugs = [m.group(1) for h in hrefs(page) if (m := CERT_HREF.match(h))]
    body = strip_tags(page.split("</h1>", 1)[-1]) if "</h1>" in page else ""
    return {
        "slug": spec["slug"],
        "title": first_h1(page),
        "url": spec["url"],
        "summary": body[:500] or None,
        "courses": sorted(set(linked)),
        "courses_published": bool(linked),
        "courses_note": None
        if linked
        else "not published in HTML — page links the catalogue, not individual courses",
        "certifications": sorted(set(cert_slugs)),
        "provenance": provenance(spec["url"], page, when),
    }


# ──────────────────────────────── commands ───────────────────────────────────


def load_sources() -> dict:
    import yaml  # deferred: only the networked path needs a third-party parser

    with SOURCES.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def cmd_fetch(args: argparse.Namespace) -> int:
    spec = load_sources()
    f = spec["fetch"]
    fetcher = Fetcher(f["user_agent"], f["delay_seconds"], f["timeout_seconds"])
    when = datetime.now(timezone.utc).isoformat(timespec="seconds")
    eps = spec["entry_points"]

    def say(msg: str) -> None:
        if not args.quiet:
            print(msg, file=sys.stderr)

    say("· index: courses")
    course_index = fetcher.get(eps["courses"])
    codes = discover_courses(course_index)
    say("· index: certifications")
    cert_index = fetcher.get(eps["certifications"])
    cert_slugs = discover_certifications(cert_index)
    if args.limit:
        codes, cert_slugs = codes[: args.limit], cert_slugs[: args.limit]

    courses, failures = [], []
    for i, code in enumerate(codes, 1):
        url = f"https://learn.snowflake.com/en/courses/{code}/"
        say(f"  [{i}/{len(codes)}] {code}")
        try:
            courses.append(parse_course(code, url, fetcher.get(url), when))
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as e:
            failures.append({"kind": "course", "id": code, "url": url, "error": str(e)})

    certifications = []
    for i, slug in enumerate(cert_slugs, 1):
        url = f"https://learn.snowflake.com/en/certifications/{slug}/"
        say(f"  cert [{i}/{len(cert_slugs)}] {slug}")
        try:
            certifications.append(parse_certification(slug, url, fetcher.get(url), when))
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as e:
            failures.append({"kind": "certification", "id": slug, "url": url, "error": str(e)})

    tracks = []
    for t in spec.get("tracks", []) if not args.limit else spec.get("tracks", [])[: args.limit]:
        say(f"  track {t['slug']}")
        try:
            tracks.append(parse_track(t, fetcher.get(t["url"]), when, fetcher))
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as e:
            failures.append({"kind": "track", "id": t["slug"], "url": t["url"], "error": str(e)})

    roles = []
    for r in spec.get("roles", []) if not args.limit else spec.get("roles", [])[: args.limit]:
        say(f"  role {r['slug']}")
        try:
            roles.append(parse_role(r, fetcher.get(r["url"]), when))
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as e:
            failures.append({"kind": "role", "id": r["slug"], "url": r["url"], "error": str(e)})

    # Curated (not scraped) — labelled so a reader can tell the difference.
    tiers = spec.get("certification_tiers", {})
    for cert in certifications:
        cert["tier"] = next(
            (tier for tier, ids in tiers.items() if cert.get("exam_code") in ids), None
        )
        cert["tier_source"] = "curated:data/sources.yml"

    measured = sum(1 for c in courses if c["effort_hours"] is not None)
    exams = [c for c in certifications if c["kind"] == "certification"]
    distinct_exams = len({c["exam_code"] for c in exams if c["exam_code"]})
    snapshot = {
        "schema": SCHEMA,
        "source": {
            "origin": spec["origin"],
            "robots": spec.get("robots"),
            "fetched_at": when,
            "sync_tool": "snowflake-os/scripts/sync.py",
            "partial": bool(args.limit),
        },
        "counts": {
            "courses": len(courses),
            "certification_pages": len(certifications),
            "distinct_exams": distinct_exams,
            "tracks": len(tracks),
            "tracks_with_published_sequence": sum(1 for t in tracks if t["sequence_published"]),
            "roles": len(roles),
            "roles_with_published_courses": sum(1 for r in roles if r["courses_published"]),
            "courses_with_measured_effort": measured,
            "courses_effort_unmeasured": len(courses) - measured,
            "exams_with_measured_cost": sum(1 for c in exams if c["exam_cost_measured"]),
            "exams_cost_unmeasured": sum(1 for c in exams if not c["exam_cost_measured"]),
            "fetch_failures": len(failures),
        },
        "failures": failures,
        "courses": courses,
        "certifications": certifications,
        "tracks": tracks,
        "roles": roles,
    }
    out = Path(args.out) if args.out else SNAPSHOT
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(snapshot, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    c = snapshot["counts"]
    print(
        f"snapshot written: {out}\n"
        f"  courses {c['courses']} · exams {c['distinct_exams']} "
        f"({c['certification_pages']} pages incl. localisations) · "
        f"tracks {c['tracks']} · roles {c['roles']}\n"
        f"  MEASURED   effort {c['courses_with_measured_effort']}/{c['courses']} · "
        f"exam cost {c['exams_with_measured_cost']} · "
        f"track sequences {c['tracks_with_published_sequence']}/{c['tracks']}\n"
        f"  UNMEASURED effort {c['courses_effort_unmeasured']} · "
        f"exam cost {c['exams_cost_unmeasured']} · "
        f"role course-lists {c['roles'] - c['roles_with_published_courses']}/{c['roles']} · "
        f"failures {c['fetch_failures']}"
    )
    return 1 if failures else 0


def cmd_drift(args: argparse.Namespace) -> int:
    """Is the committed snapshot still true? Freshness measured, never promised."""
    if not SNAPSHOT.exists():
        print("no snapshot — run `sync.py fetch` first", file=sys.stderr)
        return 2
    snap = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    spec = load_sources()
    f = spec["fetch"]
    fetcher = Fetcher(f["user_agent"], f["delay_seconds"], f["timeout_seconds"])

    live_codes = set(discover_courses(fetcher.get(spec["entry_points"]["courses"])))
    snap_codes = {c["code"] for c in snap["courses"]}
    added, removed = sorted(live_codes - snap_codes), sorted(snap_codes - live_codes)

    changed = []
    sample = [c for c in snap["courses"] if c["code"] in live_codes][: args.sample]
    for c in sample:
        page = fetcher.get(c["url"])
        live_sha = hashlib.sha256(page.encode("utf-8")).hexdigest()
        if live_sha != c["provenance"]["sha256"]:
            changed.append(c["code"])

    print(f"snapshot fetched_at: {snap['source']['fetched_at']}")
    print(f"courses added upstream:   {added or '—'}")
    print(f"courses removed upstream: {removed or '—'}")
    print(f"content changed ({len(sample)} sampled): {changed or '—'}")
    drifted = bool(added or removed or changed)
    print("VERDICT: DRIFT — re-run `sync.py fetch`" if drifted else "VERDICT: FRESH")
    return 3 if drifted else 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    fetch = sub.add_parser("fetch", help="refresh the offline snapshot")
    fetch.add_argument("--limit", type=int, default=0, help="only N of each kind (smoke test)")
    fetch.add_argument("--out", help="write elsewhere (default: snapshot/catalog.json)")
    fetch.add_argument("--quiet", action="store_true")
    fetch.set_defaults(fn=cmd_fetch)

    drift = sub.add_parser("drift", help="compare live catalogue against the snapshot")
    drift.add_argument("--sample", type=int, default=8, help="detail pages to hash-compare")
    drift.set_defaults(fn=cmd_drift)

    args = p.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    raise SystemExit(main())
