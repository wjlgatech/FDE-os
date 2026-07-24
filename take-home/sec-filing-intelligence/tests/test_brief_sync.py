"""The brief's vendored pipeline must be byte-identical to the source —
duplication is allowed only with a gate proving sync (house rule, same as
take-home #1's playground)."""
import json
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
VEND = os.path.join(ROOT, "brief", "api", "_agent")
TRIAGE = os.path.abspath(os.path.join(ROOT, "..", "enterprise-agentic-triage", "scripts"))

PAIRS = (
    [(os.path.join(ROOT, "scripts", f), os.path.join(VEND, f))
     for f in ("facts.py", "qa.py")]
    + [(os.path.join(TRIAGE, "graph.py"), os.path.join(VEND, "graph.py"))]
    + [(os.path.join(ROOT, "corpus", "extracted", f),
        os.path.join(VEND, "corpus", "extracted", f))
       for f in sorted(os.listdir(os.path.join(ROOT, "corpus", "extracted")))]
)


class TestVendoredSync(unittest.TestCase):
    def test_vendored_files_byte_identical(self):
        for src, dst in PAIRS:
            with self.subTest(file=os.path.basename(src)):
                self.assertTrue(os.path.exists(dst), f"missing: {dst}")
                with open(src, "rb") as a, open(dst, "rb") as b:
                    self.assertEqual(a.read(), b.read(), f"drifted: {dst}")


class TestAskHandlerCore(unittest.TestCase):
    def test_ask_runs_from_the_vendored_location(self):
        sys.path.insert(0, VEND)
        for m in ("qa", "facts", "graph"):
            sys.modules.pop(m, None)  # force vendored resolution
        from qa import ask
        out = ask("What was Tesla's Q2 revenue change year-over-year?")
        self.assertEqual(out["type"], "numeric")
        self.assertIn("+25.52%", out["answer"])
        json.dumps(out)
        # restore for other suites
        sys.path.pop(0)
        for m in ("qa", "facts", "graph"):
            sys.modules.pop(m, None)


if __name__ == "__main__":
    unittest.main()
