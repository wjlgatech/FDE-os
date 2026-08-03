"""Unit tests for the snowflake-os engines.

These test BEHAVIOUR, not the snapshot's exact contents — the catalogue is
resynced from a live site, so asserting "58 courses" would make a normal upstream
change look like a code regression. What must never change is the discipline:
claimed evidence scores zero, alternatives collapse, zero results are loud,
provenance is complete, and the gate fails when it should.
"""
from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SFOS = HERE.parent
ROOT = SFOS.parent
SCRIPTS = SFOS / "scripts"
sys.path.insert(0, str(SCRIPTS))


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


catalog = _load("catalog")
pathfinder = _load("pathfinder")
readiness = _load("readiness")
gate = _load("gate")
graph = _load("graph")
sync = _load("sync")


class PlanArgs:
    def __init__(self, **kw):
        self.role = kw.get("role")
        self.exam = kw.get("exam")
        self.competency = kw.get("competency")
        self.have = kw.get("have", "")
        self.free_only = kw.get("free_only", False)
        self.core_only = kw.get("core_only", False)
        self.max_hours = kw.get("max_hours")
        self.json = False


class TestSnapshotShape(unittest.TestCase):
    def setUp(self):
        self.cat = catalog.Catalog()

    def test_every_course_has_provenance(self):
        for c in self.cat.courses.values():
            p = c["provenance"]
            self.assertTrue(p["url"].startswith("https://learn.snowflake.com/"))
            self.assertEqual(len(p["sha256"]), 64)
            self.assertTrue(p["fetched_at"])

    def test_localised_exam_pages_collapse_to_distinct_exams(self):
        pages = [c for c in self.cat.raw["certifications"] if c["kind"] == "certification"]
        self.assertLess(len(self.cat.exams), len(pages),
                        "localised pages must collapse — otherwise we overcount exams")
        for code, e in self.cat.exams.items():
            self.assertEqual(e["exam_code"], code)

    def test_unmeasured_is_counted_not_hidden(self):
        for key in ("courses_effort_unmeasured", "exams_cost_unmeasured",
                    "roles_with_published_courses", "tracks_with_published_sequence"):
            self.assertIn(key, self.cat.raw["counts"])

    def test_specialty_exam_cost_is_unmeasured_not_borrowed(self):
        """Every exam page repeats a FAQ quoting $175/$375. A Specialty exam must
        not inherit either number just because it sits on the same page."""
        for e in self.cat.exams.values():
            if e["tier"] == "specialty":
                self.assertIsNone(e["exam_cost_usd"])
                self.assertFalse(e["exam_cost_measured"])


class TestCatalogQueries(unittest.TestCase):
    def setUp(self):
        self.cat = catalog.Catalog()

    def test_search_ranks_title_hits(self):
        hits = self.cat.search(["snowpark"])
        self.assertTrue(hits)
        self.assertIn("snowpark", hits[0]["title"].lower() + hits[0]["code"].lower())

    def test_zero_results_is_loud(self):
        rc = subprocess.run(
            [sys.executable, str(SCRIPTS / "catalog.py"), "find", "quantum", "knitting"],
            capture_output=True, text=True, cwd=ROOT)
        self.assertEqual(rc.returncode, 2)
        self.assertIn("vocabulary", rc.stderr)

    def test_alternatives_collapse_reduces_required_hours(self):
        """platform-foundations maps the same course in two delivery modes; the
        requirement must cost the cheaper one once, not both."""
        mapped = sum(c["effort_hours"] or 0
                     for c in self.cat.competency_courses("platform-foundations"))
        required = self.cat.required_hours("platform-foundations")
        self.assertLess(required, mapped)

    def test_requirement_units_cover_every_mapped_course(self):
        for cid in self.cat.competencies:
            in_units = {c for u in self.cat.requirement_units(cid) for c in u["codes"]}
            mapped = {c["code"] for c in self.cat.competency_courses(cid)}
            self.assertEqual(in_units, mapped, f"{cid} lost or invented a course")


class TestPathfinder(unittest.TestCase):
    def setUp(self):
        self.cat = catalog.Catalog()

    def test_platform_foundations_leads(self):
        plan = pathfinder.build_plan(self.cat, PlanArgs(role="forward-deployed-engineer"))
        self.assertEqual(plan["steps"][0]["competency"], "platform-foundations")

    def test_free_only_excludes_paid_and_says_so(self):
        plan = pathfinder.build_plan(self.cat, PlanArgs(role="ml-engineer", free_only=True))
        for s in plan["steps"]:
            for c in s["courses"]:
                self.assertTrue(c["free"])
        self.assertTrue(plan["honesty"]["excluded_paid"])

    def test_have_removes_completed_courses(self):
        base = pathfinder.build_plan(self.cat, PlanArgs(role="data-analyst"))
        first = base["steps"][0]["courses"][0]["code"]
        after = pathfinder.build_plan(self.cat, PlanArgs(role="data-analyst", have=first))
        self.assertNotIn(first, [c["code"] for s in after["steps"] for c in s["courses"]])

    def test_budget_truncates_and_reports_what_it_dropped(self):
        plan = pathfinder.build_plan(
            self.cat, PlanArgs(role="forward-deployed-engineer", free_only=True, max_hours=5))
        self.assertLessEqual(plan["totals"]["hours"], 5)
        self.assertTrue(plan["honesty"]["dropped_for_budget"])

    def test_plan_reports_its_curated_share(self):
        plan = pathfinder.build_plan(self.cat, PlanArgs(role="forward-deployed-engineer"))
        self.assertIsNotNone(plan["honesty"]["curated_share"])

    def test_unknown_goal_fails_loudly(self):
        with self.assertRaises(SystemExit):
            pathfinder.build_plan(self.cat, PlanArgs(role="chief-vibes-officer"))
        with self.assertRaises(SystemExit):
            pathfinder.build_plan(self.cat, PlanArgs(exam="XXX-C99"))

    def test_plan_only_recommends_courses_the_gate_can_credit(self):
        """Plan and gate must agree: every planned course belongs to a requirement
        unit of a competency the role actually needs."""
        role = "forward-deployed-engineer"
        plan = pathfinder.build_plan(self.cat, PlanArgs(role=role))
        spec = self.cat.roles[role]
        creditable = {
            code
            for cid in spec["core"] + spec["supporting"]
            for u in self.cat.requirement_units(cid)
            for code in u["codes"]
        }
        for s in plan["steps"]:
            for c in s["courses"]:
                self.assertIn(c["code"], creditable)


class TestReadiness(unittest.TestCase):
    def setUp(self):
        self.cat = catalog.Catalog()

    def _contract(self, completions):
        return {"candidate": "t", "role": "forward-deployed-engineer", "completions": completions}

    def test_claimed_completions_score_zero(self):
        """The whole point. Claiming everything must not pass."""
        every = [{"course": c} for c in self.cat.courses]  # no evidence on any
        r = readiness.score(self.cat, self._contract(every), 0.6)
        self.assertEqual(r["verdict"], "NO-GO")
        self.assertEqual(r["evidence_summary"]["verified"], 0)
        for comp in r["competencies"]:
            self.assertEqual(comp["verified_hours"], 0)

    def test_evidence_classes(self):
        self.assertEqual(readiness.evidence_class({"badge_url": "x"})[0], "verified")
        self.assertEqual(readiness.evidence_class({"completion_id": "x"})[0], "verified")
        self.assertEqual(readiness.evidence_class({"verifier": "x"})[0], "verified")
        self.assertEqual(readiness.evidence_class({"status": "planned"})[0], "planned")
        self.assertEqual(readiness.evidence_class({"completed_on": "2026-01-01"})[0], "self")

    def test_planned_does_not_count_even_with_a_badge(self):
        """status=planned wins over a stray badge field — intent is not completion."""
        cls, _ = readiness.evidence_class({"status": "planned", "badge_url": "x"})
        self.assertEqual(cls, "planned")

    def test_unknown_course_codes_are_reported_not_silently_dropped(self):
        r = readiness.score(self.cat, self._contract([{"course": "NOPE-1", "badge_url": "x"}]), 0.6)
        self.assertIn("NOPE-1", r["evidence_summary"]["unknown_course_codes"])

    def test_verified_evidence_can_reach_go(self):
        example = json.loads((SFOS / "examples" / "fde-ready.json").read_text(encoding="utf-8"))
        self.assertEqual(readiness.score(self.cat, example, 0.6)["verdict"], "GO")

    def test_mixed_evidence_example_is_no_go(self):
        example = json.loads((SFOS / "examples" / "fde-readiness.json").read_text(encoding="utf-8"))
        self.assertEqual(readiness.score(self.cat, example, 0.6)["verdict"], "NO-GO")

    def test_unknown_role_fails_loudly(self):
        with self.assertRaises(SystemExit):
            readiness.score(self.cat, {"role": "nope", "completions": []}, 0.6)

    def test_duplicate_evidence_cannot_exceed_the_requirement(self):
        """Satisfying both sides of an alternatives pair must not double-count."""
        units = self.cat.requirement_units("platform-foundations")
        pair = next(u for u in units if u["kind"] == "alternatives")
        both = [{"course": c, "badge_url": "x"} for c in pair["codes"]]
        r = readiness.score(self.cat, self._contract(both), 0.6)
        comp = next(c for c in r["competencies"] if c["competency"] == "platform-foundations")
        self.assertLessEqual(comp["verified_hours"], comp["required_hours"])


class TestGate(unittest.TestCase):
    def test_gate_passes_on_the_committed_artifacts(self):
        result = gate.Gate().run()
        failed = [c for c in result["checks"] if not c["ok"]]
        self.assertEqual(result["verdict"], "PASS", f"failing checks: {failed}")

    def test_gate_detects_a_dangling_reference(self):
        """A validator that never fires on you is not checking anything."""
        g = gate.Gate()
        g.cat.spec["competencies"][0]["courses"].append({"code": "NOT-A-COURSE", "basis": "curated"})
        g.referential_integrity()
        self.assertFalse(g.checks[-1]["ok"])

    def test_gate_detects_a_fake_pass(self):
        g = gate.Gate()
        g.cat.raw["certifications"][0]["exam_cost_measured"] = True
        g.cat.raw["certifications"][0]["exam_cost_usd"] = None
        g.no_fake_passes()
        self.assertFalse(g.checks[-1]["ok"])

    def test_gate_detects_an_unlicensed_satellite_marked_vendorable(self):
        g = gate.Gate()
        for s in g.cat.satellites["satellites"]:
            if s["license"] in (None, "NONE", "NOASSERTION"):
                s["vendorable"] = True
                break
        g.satellites_licensed()
        self.assertFalse(g.checks[-1]["ok"])

    def test_gate_detects_curated_share_over_the_ceiling(self):
        g = gate.Gate()
        for comp in g.cat.spec["competencies"]:
            for m in comp["courses"]:
                m["basis"] = "curated"
        g.curated_share_bounded()
        self.assertFalse(g.checks[-1]["ok"])


class TestGraph(unittest.TestCase):
    def test_graph_is_deterministic(self):
        a = json.dumps(graph.build_graph(catalog.Catalog()), sort_keys=False)
        b = json.dumps(graph.build_graph(catalog.Catalog()), sort_keys=False)
        self.assertEqual(a, b)

    def test_every_edge_points_at_a_real_node(self):
        g = graph.build_graph(catalog.Catalog())
        ids = {n["id"] for n in g["nodes"]}
        for e in g["edges"]:
            self.assertIn(e["source"], ids)
            self.assertIn(e["target"], ids)

    def test_html_payload_is_parseable_json_not_html_entities(self):
        """The bug this pins: html-escaping the payload made JSON.parse throw and
        the page render blank with no console error."""
        html = graph.render_html(graph.build_graph(catalog.Catalog()))
        start = html.index('type="application/json">') + len('type="application/json">')
        payload = html[start:html.index("</script>", start)]
        self.assertNotIn("&quot;", payload)
        self.assertEqual(json.loads(payload.replace("<\\/", "</"))["schema"], "snowflake-os/graph@1")


class TestSyncParsers(unittest.TestCase):
    """Parser unit tests run on fixtures — no network in the test suite."""

    def test_hrefs_normalise_absolute_and_relative(self):
        page = ('<a href="/en/courses/OD-X/"></a>'
                '<a href="https://learn.snowflake.com/en/courses/OD-Y/"></a>'
                '<a href="https://example.com/other"></a>')
        self.assertEqual(sync.course_slugs(page), ["OD-X", "OD-Y"])

    def test_value_after_label_does_not_leak_a_partial_tag(self):
        page = '<span>Course Number</span><span>OD-ESS-DWW</span>'
        self.assertEqual(sync.value_after_label(page, "Course Number", 80).split()[0], "OD-ESS-DWW")

    def test_missing_label_returns_none_not_a_guess(self):
        self.assertIsNone(sync.value_after_label("<p>nothing here</p>", "Estimated Effort (hours)"))

    def test_strip_tags_removes_style_blocks(self):
        self.assertEqual(sync.strip_tags("<style>.a{color:red}</style><p>hi</p>"), "hi")

    def test_canonical_code_rejects_legacy_slug(self):
        self.assertTrue(sync.CANONICAL_CODE.match("OD-ESS-DWW"))
        self.assertFalse(sync.CANONICAL_CODE.match("uni-essdww101"))


class TestBuildFreshness(unittest.TestCase):
    def test_check_mode_passes_on_committed_artifacts(self):
        rc = subprocess.run([sys.executable, str(SCRIPTS / "build.py"), "--check"],
                            capture_output=True, text=True, cwd=ROOT)
        self.assertEqual(rc.returncode, 0, rc.stderr)

    def test_check_mode_is_stale_when_the_source_changes(self):
        src = SFOS / "data" / "competencies.yml"
        original = src.read_bytes()
        try:
            src.write_bytes(original + b"\n# a change nobody rebuilt\n")
            rc = subprocess.run([sys.executable, str(SCRIPTS / "build.py"), "--check"],
                                capture_output=True, text=True, cwd=ROOT)
            self.assertEqual(rc.returncode, 3)
            self.assertIn("STALE", rc.stderr)
        finally:
            src.write_bytes(original)


class TestWorkflow(unittest.TestCase):
    def test_not_yet_ships_a_remediation_plan(self):
        rc = subprocess.run(
            [sys.executable, "workflows/snowflake-enablement/run.py",
             "workflows/snowflake-enablement/examples/candidate.json", "--json"],
            capture_output=True, text=True, cwd=ROOT)
        self.assertEqual(rc.returncode, 2)
        report = json.loads(rc.stdout)
        self.assertEqual(report["verdict"], "NOT-YET")
        self.assertIsNotNone(report["remediation_plan"], "a refusal must carry the way forward")

    def test_staff_verdict_on_a_verified_candidate(self):
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
            fh.write((SFOS / "examples" / "fde-ready.json").read_text(encoding="utf-8"))
            path = fh.name
        try:
            rc = subprocess.run(
                [sys.executable, "workflows/snowflake-enablement/run.py", path, "--json"],
                capture_output=True, text=True, cwd=ROOT)
            self.assertEqual(rc.returncode, 0, rc.stdout + rc.stderr)
            self.assertEqual(json.loads(rc.stdout)["verdict"], "STAFF")
        finally:
            os.unlink(path)


if __name__ == "__main__":
    unittest.main()
