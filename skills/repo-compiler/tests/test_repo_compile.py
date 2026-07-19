"""repo-compiler tests — pure functions, offline fixtures, no network ever. Stdlib unittest."""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
from repo_compile import (  # noqa: E402
    build_graph, build_skill, classify, needs_refresh, slugify, validate_graph,
)

FIXTURE = {
    "repo": "example/awesome-agents",
    "sha": "a" * 40,
    "default_branch": "main",
    "stars": 12345,
    "description": "A curated collection of agent tools.",
    "topics": ["mcp", "ai-agents"],
    "license": "MIT",
    "pushed_at": "2026-07-01T00:00:00Z",
    "html_url": "https://github.com/example/awesome-agents",
    "readme": (
        "# Awesome Agents\n\nIntro text with a [link](https://example.com/a).\n\n"
        "## Servers\n\nMore [evidence](https://example.com/b).\n\n"
        "### Filesystem\n\ndetail\n\n"
        "## Clients\n\n```md\n# not-a-heading (fenced)\n[not-a-link](https://x.y)\n```\n"
    ),
}


class TestGraphExtraction(unittest.TestCase):
    def test_graph_has_repo_topics_concepts_evidence(self):
        g = build_graph(FIXTURE, "why")
        self.assertEqual({n["type"] for n in g["nodes"]},
                         {"repo", "topic", "concept", "evidence"})
        labels = [n["label"] for n in g["nodes"] if n["type"] == "concept"]
        self.assertEqual(labels, ["Awesome Agents", "Servers", "Filesystem", "Clients"])

    def test_code_fences_do_not_pollute_graph(self):
        g = build_graph(FIXTURE)
        self.assertTrue(all("not-a-heading" not in n["label"] for n in g["nodes"]))
        self.assertTrue(all(n.get("source_url") != "https://x.y" for n in g["nodes"]))

    def test_heading_nesting_produces_part_of_chain(self):
        g = build_graph(FIXTURE)
        edges = {(e["from"], e["to"]) for e in g["edges"] if e["rel"] == "part_of"}
        self.assertIn(("c-filesystem", "c-servers"), edges)      # h3 under h2
        self.assertIn(("c-servers", "c-awesome-agents"), edges)  # h2 under h1

    def test_provenance_is_sha_pinned(self):
        g = build_graph(FIXTURE)
        concept = next(n for n in g["nodes"] if n["type"] == "concept")
        self.assertIn(f"/blob/{'a' * 40}/README.md", concept["source_url"])
        self.assertEqual(g["source"]["sha"], "a" * 40)

    def test_validate_passes_on_good_graph(self):
        self.assertEqual(validate_graph(build_graph(FIXTURE)), [])

    def test_validate_catches_dangling_edge_and_missing_provenance(self):
        g = build_graph(FIXTURE)
        g["edges"].append({"from": "ghost", "to": "nowhere", "rel": "cites"})
        g["nodes"][0] = dict(g["nodes"][0], source_url="")
        errs = validate_graph(g)
        self.assertTrue(any("dangling" in e for e in errs))
        self.assertTrue(any("provenance" in e for e in errs))


class TestClassificationAndSkill(unittest.TestCase):
    def test_classify(self):
        cases = [
            ("A curated collection of agent tools.", "curated-index"),
            ("A community driven registry service", "registry"),
            ("Open source AI engineering platform: evals, observability", "platform"),
            ("The fast, Pythonic way to build MCP servers", "framework"),
            ("The definitive roadmap to becoming an FDE", "learning-resource"),
            ("Does something unusual", "tool"),
        ]
        for desc, expected in cases:
            with self.subTest(desc=desc):
                self.assertEqual(classify({"description": desc, "topics": []}), expected)

    def test_skill_has_honest_edges_and_pinned_source(self):
        s = build_skill(FIXTURE, "why we cite it")
        self.assertTrue(s["notGoodAt"], "every skill must carry a non-empty notGoodAt")
        self.assertEqual(s["kind"], "curated-index")
        self.assertEqual(s["integration"]["as"], "discovery-source")
        self.assertEqual(s["source"]["sha"], "a" * 40)
        self.assertIn("why we cite it", s["useWhen"])

    def test_missing_license_adds_honest_edge(self):
        s = build_skill(dict(FIXTURE, license=None))
        self.assertTrue(any("license unclear" in n for n in s["notGoodAt"]))


class TestFreshness(unittest.TestCase):
    def test_needs_refresh_only_on_sha_change(self):
        self.assertTrue(needs_refresh("abc", "def"))
        self.assertFalse(needs_refresh("abc", "abc"))
        self.assertTrue(needs_refresh(None, "abc"))

    def test_slugify_stable(self):
        self.assertEqual(slugify("PrefectHQ/fastmcp"), "prefecthq-fastmcp")


if __name__ == "__main__":
    unittest.main()
