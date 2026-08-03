#!/usr/bin/env python3
"""snowflake-os · gate — the repo auditing its own knowledge base.

Pure stdlib, offline, deterministic. Exit 0 = PASS, 1 = FAIL.

    python3 snowflake-os/scripts/gate.py
    python3 snowflake-os/scripts/gate.py --json

Nine checks. Each is a thing that would otherwise rot silently:

  1. build-freshness      compiled artifact still matches its YAML source (sha256)
  2. referential-integrity every course/exam code in the curation exists upstream
  3. provenance-complete   every scraped record carries url + sha256 + fetched_at
  4. no-fake-passes        nothing is recorded as measured while holding no value
  5. role-coverage         every role's competencies exist and have ≥1 real course
  6. competency-reachable  no orphan competency — each is reachable from a role
  7. alternatives-valid    every alternatives group has ≥2 members in its competency
  8. unmeasured-declared   everything upstream withholds is counted, not hidden
  9. curated-share-bounded the curated share of mappings stays under the ceiling

Check 9 is the one that keeps us honest as the map grows: it is easy to "cover"
a role by inventing mappings. The ceiling makes that a build failure.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from catalog import CATALOG, COMPETENCIES, Catalog  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
YAML_SRC = ROOT / "data" / "competencies.yml"
CURATED_CEILING = 0.40


class Gate:
    def __init__(self) -> None:
        self.checks: list[dict] = []
        self.cat = Catalog()

    def check(self, name: str, ok: bool, detail: str) -> None:
        self.checks.append({"check": name, "ok": bool(ok), "detail": detail})

    # ── the nine ─────────────────────────────────────────────────────────────

    def build_freshness(self) -> None:
        recorded = self.cat.spec.get("source", {}).get("sha256")
        actual = hashlib.sha256(YAML_SRC.read_bytes()).hexdigest()
        self.check(
            "build-freshness",
            recorded == actual,
            "competencies.json matches competencies.yml"
            if recorded == actual
            else "STALE — run `python3 snowflake-os/scripts/build.py`",
        )

    def referential_integrity(self) -> None:
        bad = []
        for comp in self.cat.spec["competencies"]:
            for m in comp["courses"]:
                if m["code"] not in self.cat.courses:
                    bad.append(f"{comp['id']} → course {m['code']}")
            for e in comp["exams"]:
                if e["code"] not in self.cat.exams:
                    bad.append(f"{comp['id']} → exam {e['code']}")
        self.check(
            "referential-integrity",
            not bad,
            "every curated code exists in the snapshot" if not bad else f"dangling: {'; '.join(bad)}",
        )

    def provenance_complete(self) -> None:
        missing = []
        groups = ("courses", "certifications", "tracks", "roles")
        for g in groups:
            for rec in self.cat.raw[g]:
                p = rec.get("provenance") or {}
                if not (p.get("url") and p.get("sha256") and p.get("fetched_at")):
                    missing.append(f"{g}:{rec.get('code') or rec.get('slug')}")
        total = sum(len(self.cat.raw[g]) for g in groups)
        self.check(
            "provenance-complete",
            not missing,
            f"all {total} scraped records carry url+sha256+fetched_at"
            if not missing
            else f"{len(missing)} without provenance: {', '.join(missing[:5])}",
        )

    def no_fake_passes(self) -> None:
        """A `*_measured: true` flag must be backed by an actual value."""
        bad = []
        for c in self.cat.raw["certifications"]:
            if c.get("exam_cost_measured") and c.get("exam_cost_usd") is None:
                bad.append(f"{c['slug']}:cost")
            if c.get("tests_measured") and not c.get("tests"):
                bad.append(f"{c['slug']}:tests")
        for t in self.cat.raw["tracks"]:
            if t.get("sequence_published") and not t.get("sequence"):
                bad.append(f"track:{t['slug']}")
        for r in self.cat.raw["roles"]:
            if r.get("courses_published") and not r.get("courses"):
                bad.append(f"role:{r['slug']}")
        self.check(
            "no-fake-passes",
            not bad,
            "no record claims to be measured while empty" if not bad else f"fake passes: {', '.join(bad)}",
        )

    def role_coverage(self) -> None:
        bad = []
        for role, spec in self.cat.roles.items():
            for cid in list(spec.get("core", [])) + list(spec.get("supporting", [])):
                if cid not in self.cat.competencies:
                    bad.append(f"{role} → unknown competency {cid}")
                elif not self.cat.competency_courses(cid):
                    bad.append(f"{role} → {cid} has no real course")
        self.check(
            "role-coverage",
            not bad,
            f"all {len(self.cat.roles)} roles map to competencies backed by real courses"
            if not bad
            else "; ".join(bad),
        )

    def competency_reachable(self) -> None:
        reachable = {
            cid
            for spec in self.cat.roles.values()
            for cid in list(spec.get("core", [])) + list(spec.get("supporting", []))
        }
        orphans = sorted(set(self.cat.competencies) - reachable)
        self.check(
            "competency-reachable",
            not orphans,
            "every competency is reachable from at least one role"
            if not orphans
            else f"orphan competencies (no role needs them): {', '.join(orphans)}",
        )

    def alternatives_valid(self) -> None:
        bad = []
        for cid, groups in self.cat.spec.get("alternatives", {}).items():
            if cid not in self.cat.competencies:
                bad.append(f"unknown competency {cid}")
                continue
            mapped = {c["code"] for c in self.cat.competency_courses(cid)}
            for group in groups:
                present = [c for c in group if c in mapped]
                if len(present) < 2:
                    bad.append(f"{cid}: {group} has {len(present)} member(s) mapped — not an alternative")
        self.check(
            "alternatives-valid",
            not bad,
            "every alternatives group has ≥2 members in its competency"
            if not bad
            else "; ".join(bad),
        )

    def unmeasured_declared(self) -> None:
        c = self.cat.raw["counts"]
        declared = {
            "course effort": c["courses_effort_unmeasured"],
            "exam cost": c["exams_cost_unmeasured"],
            "role course lists": c["roles"] - c["roles_with_published_courses"],
            "track sequences": c["tracks"] - c["tracks_with_published_sequence"],
        }
        # The point is not that the number is zero — it is that it is COUNTED.
        self.check(
            "unmeasured-declared",
            all(v is not None for v in declared.values()),
            "unmeasured tallied: " + " · ".join(f"{k}={v}" for k, v in declared.items()),
        )

    def curated_share_bounded(self) -> None:
        total = sum(len(c["courses"]) + len(c["exams"]) for c in self.cat.spec["competencies"])
        curated = sum(
            1
            for c in self.cat.spec["competencies"]
            for m in c["courses"] + c["exams"]
            if m["basis"] == "curated"
        )
        share = curated / total if total else 0.0
        self.check(
            "curated-share-bounded",
            share <= CURATED_CEILING,
            f"{curated}/{total} mappings curated ({share:.0%}) — ceiling {CURATED_CEILING:.0%}",
        )

    def satellites_licensed(self) -> None:
        """A satellite with no usable licence must be marked unvendorable.

        Snowflake-Labs/coco-skills ships no LICENSE at all, and subagent-cortex-code
        ships one GitHub cannot identify. Default copyright means we may link and
        describe, not copy. This check makes that a build failure rather than a
        good intention — if someone flips `vendorable: true` on either, the gate
        catches it before any code is lifted.
        """
        bad = []
        for s in self.cat.satellites.get("satellites", []):
            risky = s.get("license") in (None, "NONE", "NOASSERTION")
            if risky and s.get("vendorable", True):
                bad.append(f"{s['slug']} (licence {s.get('license')}) is marked vendorable")
            if risky and not s.get("caution"):
                bad.append(f"{s['slug']} has a risky licence but no `caution` note")
        n = len(self.cat.satellites.get("satellites", []))
        self.check(
            "satellites-licensed",
            not bad,
            f"all {n} satellites carry a licence verdict; unlicensed ones are quarantined"
            if not bad
            else "; ".join(bad),
        )

    def run(self) -> dict:
        for fn in (
            self.build_freshness,
            self.referential_integrity,
            self.provenance_complete,
            self.no_fake_passes,
            self.role_coverage,
            self.competency_reachable,
            self.alternatives_valid,
            self.unmeasured_declared,
            self.curated_share_bounded,
            self.satellites_licensed,
        ):
            fn()
        passed = sum(1 for c in self.checks if c["ok"])
        return {
            "checks": self.checks,
            "passed": passed,
            "total": len(self.checks),
            "verdict": "PASS" if passed == len(self.checks) else "FAIL",
        }


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--json", action="store_true")
    args = p.parse_args(argv)

    for path in (CATALOG, COMPETENCIES):
        if not Path(path).exists():
            print(f"missing artifact: {path}", file=sys.stderr)
            return 1

    result = Gate().run()
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print("snowflake-os · knowledge-base integrity gate")
        for c in result["checks"]:
            print(f"  {'✓' if c['ok'] else '✗'} {c['check']:<24} {c['detail']}")
        print(f"\n{result['verdict']} — {result['passed']}/{result['total']} checks")
    return 0 if result["verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
