"""hub_query tests — offline fixture registry, no coupling to generated artifacts. Stdlib unittest."""
import contextlib
import io
import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
from hub_query import diagnose, find, load_registry, main, render_skill  # noqa: E402


def skill(name, kind, one, use=(), stars=100):
    return {
        "id": f"skill-{name.replace('/', '-')}", "name": name, "kind": kind, "oneLine": one,
        "stars": stars, "license": "MIT", "notGoodAt": ["something honest"],
        "useWhen": list(use),
        "integration": {"as": "workflow-organ", "how": "wire behind a seam"},
        "source": {"repo": name, "sha": "b" * 40, "url": f"https://github.com/{name}"},
    }


SKILLS = [
    skill("acme/langfuse-like", "platform", "LLM observability and evals platform",
          use=["eval-obs organ"], stars=500),
    skill("acme/fastmcp-like", "framework", "build MCP servers fast", stars=900),
    skill("acme/awesome-like", "curated-index", "curated collection of MCP servers", stars=100),
]


class TestFind(unittest.TestCase):
    def test_find_ranks_relevant_first(self):
        res = find("observability evals", SKILLS)
        self.assertTrue(res)
        self.assertEqual(res[0][1]["name"], "acme/langfuse-like")
        self.assertEqual(res[0][0], 1.0)

    def test_find_ties_break_by_stars_then_name(self):
        res = find("mcp servers", SKILLS)
        names = [s["name"] for _, s in res]
        self.assertLess(names.index("acme/fastmcp-like"), names.index("acme/awesome-like"))

    def test_find_no_match_returns_empty_and_diagnose_names_vocab(self):
        self.assertEqual(find("quantum knitting", SKILLS), [])
        d = diagnose(SKILLS)
        self.assertIn("curated-index", d)
        self.assertIn("repos.yml", d)

    def test_render_includes_honest_edge_and_pinned_source(self):
        out = render_skill(SKILLS[0], 0.5)
        self.assertIn("not good at: something honest", out)
        self.assertIn("@ bbbbbbbb", out)


class TestCLI(unittest.TestCase):
    def _registry(self, tmpdir):
        p = os.path.join(tmpdir, "hub-skills.json")
        with open(p, "w", encoding="utf-8") as f:
            json.dump({"contractVersion": "1.0", "skills": SKILLS}, f)
        return p

    def _run(self, argv):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = main(argv)
        return code, out.getvalue(), err.getvalue()

    def test_cli_find_and_recipe_and_list(self):
        with tempfile.TemporaryDirectory() as d:
            reg = self._registry(d)
            code, out, _ = self._run(["--registry", reg, "find", "observability"])
            self.assertEqual(code, 0)
            self.assertIn("langfuse-like", out)
            code, out, _ = self._run(["--registry", reg, "recipe", "fastmcp"])
            self.assertEqual(code, 0)
            self.assertIn("build MCP servers fast", out)
            code, out, _ = self._run(["--registry", reg, "list"])
            self.assertEqual(code, 0)
            self.assertEqual(out.count("→"), 3)

    def test_cli_zero_match_exits_2_with_diagnostic(self):
        with tempfile.TemporaryDirectory() as d:
            reg = self._registry(d)
            code, out, _ = self._run(["--registry", reg, "find", "quantum", "knitting"])
        self.assertEqual(code, 2)
        self.assertIn("no match", out)

    def test_cli_missing_registry_exits_1(self):
        with tempfile.TemporaryDirectory() as d:
            code, _, err = self._run(["--registry", os.path.join(d, "nope.json"), "list"])
        self.assertEqual(code, 1)
        self.assertIn("repo_compile.py all", err)

    def test_load_registry_reads_real_shape(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(load_registry(self._registry(d))[0]["kind"], "platform")


if __name__ == "__main__":
    unittest.main()
