"""Tests for field-kit-generator. Run:
  python3 -m unittest discover -s skills/field-kit-generator/tests -p 'test_*.py'

Oracle: the lint must PASS the real Post #1 kit (delta-discovery-protocol) and FAIL a malformed one.
"""
import importlib.util
import os
import tempfile
import unittest

_HERE = os.path.dirname(__file__)
_SCRIPT = os.path.join(_HERE, "..", "scripts", "field_kit_generator.py")
_REPO = os.path.abspath(os.path.join(_HERE, "..", "..", ".."))
_spec = importlib.util.spec_from_file_location("fkg", _SCRIPT)
fkg = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(fkg)


class TestLintOnReferenceKit(unittest.TestCase):
    def test_existing_post1_kit_passes(self):
        kit = os.path.join(_REPO, "field-kits", "delta-discovery-protocol")
        self.assertEqual(fkg.lint_kit(kit), [], "the reference kit must pass its own convention lint")

    def test_real_index_lints_clean(self):
        # The whole field-kits/ dir (kits + index) should be clean on main.
        problems = fkg.lint_index(os.path.join(_REPO, "field-kits"))
        self.assertEqual(problems, [], f"field-kits/ should lint clean; got {problems}")


class TestLintCatchesMalformed(unittest.TestCase):
    def test_missing_primary_doc(self):
        with tempfile.TemporaryDirectory() as d:
            os.makedirs(os.path.join(d, "empty-kit"))
            problems = fkg.lint_kit(os.path.join(d, "empty-kit"))
            self.assertTrue(any("no primary doc" in p for p in problems))

    def test_no_source_no_risks_flagged(self):
        with tempfile.TemporaryDirectory() as d:
            kit = os.path.join(d, "bare-kit")
            os.makedirs(kit)
            with open(os.path.join(kit, "SKILL.md"), "w") as fh:
                fh.write("# bare\nHow to run it: just do the thing.\n")  # has run, no source, no risks
            problems = fkg.lint_kit(kit)
            self.assertTrue(any("source" in p for p in problems))
            self.assertTrue(any("RISKS" in p for p in problems))

    def test_kit_not_in_index_flagged(self):
        with tempfile.TemporaryDirectory() as d:
            with open(os.path.join(d, "README.md"), "w") as fh:
                fh.write("# Field Kits\n| Kit |\n|---|\n")  # index mentions no kit
            kit = os.path.join(d, "orphan-kit")
            os.makedirs(kit)
            with open(os.path.join(kit, "SKILL.md"), "w") as fh:
                fh.write("# orphan\nProvenance: from Field Manual 99.\nHow to run it: x.\nRisks: none known.\n")
            problems = fkg.lint_index(d)
            self.assertTrue(any("not listed in" in p for p in problems))


class TestGenerate(unittest.TestCase):
    def test_off_menu_type_rejected_with_menu(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError) as ctx:
                fkg.scaffold_kit(d, "x", "Banana", "FM 1", "s")
            self.assertIn("Field Kit menu", str(ctx.exception))

    def test_scaffold_passes_own_lint(self):
        # A freshly scaffolded kit must itself satisfy the lint (names source, run, RISKS).
        with tempfile.TemporaryDirectory() as d:
            path = fkg.scaffold_kit(d, "demo-kit", "Agent skill",
                                    "Field Manual 02 — One Name, Three Jobs", "A demo decision tree")
            self.assertTrue(path.endswith("demo-kit/SKILL.md"))
            self.assertEqual(fkg.lint_kit(os.path.dirname(path)), [])

    def test_scaffold_type_picks_right_primary(self):
        with tempfile.TemporaryDirectory() as d:
            p = fkg.scaffold_kit(d, "rub", "Eval rubric", "FM 3", "scoring")
            self.assertTrue(p.endswith("rub/RUBRIC.md"))

    def test_bad_slug_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):
                fkg.scaffold_kit(d, "Bad Slug", "Agent skill", "FM 1", "s")


if __name__ == "__main__":
    unittest.main()
