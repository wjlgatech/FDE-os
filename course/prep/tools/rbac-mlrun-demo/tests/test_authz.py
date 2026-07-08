"""The authZ eval-gate — a (subject, action, resource, project) → allow/deny table that must pass.

Run:  python3 -m unittest discover -s course/prep/tools/rbac-mlrun-demo/tests -p 'test_*.py'
This is the "gate" from the article: no policy change merges without its test going green.
"""
import base64
import json
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import pdp  # noqa: E402
import pep  # noqa: E402

POLICY = pdp.load_policy()


def subj(*grants):
    return {"sub": "t", "grants": [{"role": r, "project": p} for r, p in grants]}


def allow(s, action, resource, project):
    return pdp.decide(POLICY, s, action, resource, project).allow


# The table: (label, subject, action, resource, project, expected_allow)
TABLE = [
    ("viewer reads a model in its project",        subj(("viewer", "demo")),        "read",   "model",           "demo",  True),
    ("viewer CANNOT run a function",               subj(("viewer", "demo")),        "run",    "function",        "demo",  False),
    ("developer runs a function in its project",   subj(("developer", "demo")),     "run",    "function",        "demo",  True),
    ("developer runs a Nuclio function",           subj(("developer", "demo")),     "run",    "nuclio_function", "demo",  True),
    ("developer deploys a function",               subj(("developer", "demo")),     "deploy", "function",        "demo",  True),
    ("developer CANNOT run outside its project",   subj(("developer", "demo")),     "run",    "function",        "other", False),
    ("developer CANNOT delete a model",            subj(("developer", "demo")),     "delete", "model",           "demo",  False),
    ("project-admin deletes in its project",       subj(("project-admin", "demo")), "delete", "model",           "demo",  True),
    ("project-admin CANNOT act cross-project",     subj(("project-admin", "demo")), "delete", "model",           "other", False),
    ("platform-admin does anything, anywhere",     subj(("platform-admin", "*")),   "delete", "artifact",        "other", True),
    ("unknown role is denied (deny-by-default)",   subj(("data-wizard", "demo")),   "read",   "model",           "demo",  False),
    ("no grants at all is denied",                 subj(),                          "read",   "project",         "demo",  False),
    ("multi-role: dev on demo + viewer on prod",   subj(("developer", "demo"), ("viewer", "prod")), "read", "model", "prod", True),
    ("multi-role: cannot run on the viewer-only project", subj(("developer", "demo"), ("viewer", "prod")), "run", "function", "prod", False),
]


class TestAuthorizationTable(unittest.TestCase):
    def test_table(self):
        failures = []
        for label, s, action, resource, project, expected in TABLE:
            got = allow(s, action, resource, project)
            if got != expected:
                failures.append(f"{label}: expected {'ALLOW' if expected else 'DENY'}, got {'ALLOW' if got else 'DENY'}")
        self.assertEqual(failures, [], "\n" + "\n".join(failures))


class TestDenyByDefaultProperties(unittest.TestCase):
    def test_empty_policy_denies_everything(self):
        empty = {"policy_version": "x", "roles": {}}
        self.assertFalse(pdp.decide(empty, subj(("developer", "demo")), "read", "model", "demo").allow)

    def test_action_and_resource_both_must_match(self):
        # developer has run:function; run:model is NOT granted
        self.assertFalse(allow(subj(("developer", "demo")), "run", "model", "demo"))


class TestPEP(unittest.TestCase):
    def _token(self, claims):
        return base64.urlsafe_b64encode(json.dumps(claims).encode()).decode().rstrip("=")

    def test_enforce_maps_groups_and_audits(self):
        pep.AUDIT.clear()
        tok = self._token({"sub": "alice", "groups": ["developer:demo"]})
        res = pep.enforce(POLICY, pep.parse_claims(tok), "run", "function", "demo")
        self.assertTrue(res["allow"])
        self.assertEqual(res["status"], 200)
        self.assertEqual(len(pep.AUDIT), 1)
        self.assertEqual(pep.AUDIT[0]["decision"], "allow")
        self.assertTrue(pep.AUDIT[0]["policy_version"])

    def test_enforce_denies_and_returns_403(self):
        tok = self._token({"sub": "bob", "groups": ["viewer:demo"]})
        res = pep.enforce(POLICY, pep.parse_claims(tok), "delete", "model", "demo")
        self.assertFalse(res["allow"])
        self.assertEqual(res["status"], 403)

    def test_garbage_token_has_no_grants_denies(self):
        res = pep.enforce(POLICY, pep.parse_claims("not-a-real-token"), "read", "model", "demo")
        self.assertFalse(res["allow"])


if __name__ == "__main__":
    unittest.main()
