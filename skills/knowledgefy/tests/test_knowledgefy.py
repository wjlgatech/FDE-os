"""Tests for knowledgefy. Stdlib unittest — run: python3 -m unittest discover -s skills -p 'test_*.py'

Covers U2's four scenarios: happy path, no-network invariant, empty vault, determinism.
"""
import importlib.util
import json
import os
import socket
import tempfile
import unittest

_HERE = os.path.dirname(__file__)
_SCRIPT = os.path.join(_HERE, "..", "scripts", "knowledgefy.py")
_spec = importlib.util.spec_from_file_location("knowledgefy", _SCRIPT)
kf = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(kf)


def _write(d, name, text):
    p = os.path.join(d, name)
    with open(p, "w", encoding="utf-8") as fh:
        fh.write(text)
    return p


class TestKnowledgefy(unittest.TestCase):
    def test_happy_path_concepts_and_evidence(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "a.md", "# Origin\nPalantir's Delta role, per Qureshi https://nabeelqu.co/x\n## Dev vs Delta\nSee https://blog.palantir.com/dev\n")
            _write(d, "b.md", "# Labs\nOpenAI roles https://a16z.com/services\n")
            _write(d, "c.md", "# Economics\nSequoia [services](https://sequoiacap.com/article)\n")
            g = kf.build_graph(d)
            concepts = [n for n in g["nodes"] if n["type"] == "concept"]
            evidence = [n for n in g["nodes"] if n["type"] == "evidence"]
            # 4 headings across 3 files -> 4 concepts
            self.assertEqual(len(concepts), 4)
            # 4 distinct urls -> 4 evidence nodes
            self.assertEqual(len(evidence), 4)
            # nesting: "Dev vs Delta" (l2) part_of "Origin" (l1)
            part_of = [e for e in g["edges"] if e["type"] == "part_of"]
            self.assertEqual(len(part_of), 1)
            # every evidence node is cited by exactly one concept here
            cites = [e for e in g["edges"] if e["type"] == "cites"]
            self.assertEqual(len(cites), 4)
            # markdown-link label is captured
            self.assertTrue(any(n.get("label") == "services" for n in evidence))

    def test_html_has_no_external_scripts(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "a.md", "# X\nhttps://example.com/y\n")
            g = kf.build_graph(d)
            doc = kf.render_html(g)
            # no external script/style/link references -> works offline from file://
            self.assertNotIn("src=\"http", doc)
            self.assertNotIn("href=\"http", doc.split("<script")[0])  # no external stylesheet
            self.assertIn("application/json", doc)  # data embedded inline

    def test_no_network_invariant(self):
        # Disable all socket creation; a base build must still succeed.
        orig = socket.socket

        def _boom(*a, **k):
            raise OSError("network disabled for test")

        socket.socket = _boom
        try:
            with tempfile.TemporaryDirectory() as d:
                _write(d, "a.md", "# Concept\nEvidence https://example.com/a\n")
                g = kf.build_graph(d)
                self.assertEqual(g["counts"]["concepts"], 1)
                self.assertEqual(g["counts"]["evidence"], 1)
        finally:
            socket.socket = orig

    def test_empty_vault_is_valid_empty_graph(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "empty.md", "")
            _write(d, "noheadings.md", "just prose, no headings, no urls\n")
            g = kf.build_graph(d)
            self.assertEqual(g["nodes"], [])
            self.assertEqual(g["edges"], [])
            self.assertEqual(g["counts"], {"concepts": 0, "evidence": 0, "edges": 0})

    def test_determinism_byte_identical(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "a.md", "# A\nhttps://example.com/1\n# B\nhttps://example.com/2\n")
            j1 = json.dumps(kf.build_graph(d), indent=2, sort_keys=True)
            j2 = json.dumps(kf.build_graph(d), indent=2, sort_keys=True)
            self.assertEqual(j1, j2)

    def test_code_fences_ignored(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "a.md", "# Real\nlive https://example.com/real\n```\n# Not a heading\nhttps://example.com/infence\n```\n")
            g = kf.build_graph(d)
            self.assertEqual(g["counts"]["concepts"], 1)  # fenced "# Not a heading" ignored
            self.assertEqual(g["counts"]["evidence"], 1)  # fenced url ignored


if __name__ == "__main__":
    unittest.main()
