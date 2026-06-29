import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import jd_compile as jc  # noqa: E402

SAMPLE_A = """
# FDE — AI Lab
Strong software engineering, shipping production systems in Python and TypeScript.
Build agentic systems orchestrating LLM workflows; MCP servers; evaluations and fine-tuning.
Deploy across cloud, VPC, and on-premises with Docker and Kubernetes. Vector databases: Pinecone.
Customer-facing, high agency. 6+ years, including technical leadership; define playbooks and mentor.
"""

SAMPLE_B = """
# Agent Engineer — Cloud GTM
Production-grade agentic workflows: multi-agent systems and Model Context Protocol (MCP) servers.
Evaluation pipelines and observability. LangGraph, CrewAI, Google ADK. Vertex AI, GKE. Python.
Partner with sales and stakeholders. Convert friction points into reusable modules.
"""


class TestCompileOne(unittest.TestCase):
    def setUp(self):
        self.a = jc.compile_jd(SAMPLE_A, "lab")

    def test_core_clusters_detected(self):
        for c in ("production_swe", "enterprise_deploy", "modern_ai_stack", "agentic_design", "fde_craft", "leadership"):
            self.assertIn(c, self.a["required_clusters"], c)

    def test_specific_tools_extracted(self):
        self.assertIn("mcp", self.a["tools"]["protocols"])
        self.assertIn("pinecone", self.a["tools"]["vector_dbs"])
        self.assertIn("docker", self.a["tools"]["deploy"])
        self.assertIn("python", self.a["tools"]["languages"])

    def test_years_parsed(self):
        self.assertEqual(self.a["years_max"], 6)

    def test_empty_tool_categories_dropped(self):
        # no category should be present with an empty list
        self.assertTrue(all(v for v in self.a["tools"].values()))


class TestCrossCompile(unittest.TestCase):
    def test_universal_and_frequency(self):
        cross = jc.cross_compile([jc.compile_jd(SAMPLE_A, "lab"), jc.compile_jd(SAMPLE_B, "gtm")])
        self.assertEqual(cross["n"], 2)
        # agentic design + modern AI stack appear in BOTH -> universal
        self.assertIn("Agentic system design", cross["universal_clusters"])
        # MCP demanded by both
        self.assertEqual(cross["tool_freq"]["protocols"]["mcp"], 2)
        # GCP-only tool shows once
        self.assertEqual(cross["tool_freq"]["agent_frameworks"].get("google adk"), 1)

    def test_tool_freq_sorted_desc(self):
        cross = jc.cross_compile([jc.compile_jd(SAMPLE_A, "a"), jc.compile_jd(SAMPLE_B, "b")])
        for cat, d in cross["tool_freq"].items():
            counts = list(d.values())
            self.assertEqual(counts, sorted(counts, reverse=True))


class TestNotes(unittest.TestCase):
    def test_to_note_has_headings_for_concepts(self):
        note = jc.to_note(jc.compile_jd(SAMPLE_B, "gtm"), source="http://example.com/jd")
        self.assertIn("# gtm — FDE competency profile", note)
        self.assertIn("## Agentic system design", note)
        self.assertIn("Named tools and frameworks", note)
        self.assertIn("http://example.com/jd", note)

    def test_cross_note_lists_universal(self):
        cross = jc.cross_compile([jc.compile_jd(SAMPLE_A, "a"), jc.compile_jd(SAMPLE_B, "b")])
        note = jc.cross_note(cross)
        self.assertIn("cross-company synthesis", note)
        self.assertIn("Universal competencies", note)
        self.assertIn("required by 2/2", note.replace("**", ""))


if __name__ == "__main__":
    unittest.main()
