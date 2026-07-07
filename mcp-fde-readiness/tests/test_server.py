"""Tests for mcp-fde-readiness. Run:
  python3 -m unittest discover -s mcp-fde-readiness/tests -p 'test_*.py'
Covers MCP protocol correctness on the pure handle_request dispatch + the readiness scoring gate.
"""
import importlib.util
import json
import os
import unittest

_HERE = os.path.dirname(__file__)
_SCRIPT = os.path.join(_HERE, "..", "server.py")
_spec = importlib.util.spec_from_file_location("rdserver", _SCRIPT)
srv = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(srv)


def _req(method, params=None, rid=1):
    r = {"jsonrpc": "2.0", "id": rid, "method": method}
    if params is not None:
        r["params"] = params
    return r


def _all_yes():
    rub = srv.load_rubric()
    return {it["id"]: True for d in rub["dimensions"] for it in d["items"]}


class TestProtocol(unittest.TestCase):
    def test_initialize(self):
        r = srv.handle_request(_req("initialize", {"protocolVersion": "2025-06-18"}))
        self.assertEqual(r["result"]["serverInfo"]["name"], "fde-readiness")
        self.assertIn("tools", r["result"]["capabilities"])
        self.assertEqual(r["result"]["protocolVersion"], "2025-06-18")

    def test_initialize_defaults_version(self):
        r = srv.handle_request(_req("initialize", {}))
        self.assertEqual(r["result"]["protocolVersion"], srv.PROTOCOL_VERSION)

    def test_tools_list(self):
        r = srv.handle_request(_req("tools/list"))
        names = {t["name"] for t in r["result"]["tools"]}
        self.assertEqual(names, {"readiness_rubric", "readiness_score", "evidence_tier"})
        for t in r["result"]["tools"]:
            self.assertEqual(t["inputSchema"]["type"], "object")
            self.assertTrue(t["description"])

    def test_notification_returns_none(self):
        self.assertIsNone(srv.handle_request({"jsonrpc": "2.0", "method": "notifications/initialized"}))

    def test_ping(self):
        self.assertEqual(srv.handle_request(_req("ping"))["result"], {})

    def test_unknown_method_errors(self):
        self.assertEqual(srv.handle_request(_req("nope"))["error"]["code"], srv.ERR_METHOD_NOT_FOUND)

    def test_unknown_tool_errors(self):
        r = srv.handle_request(_req("tools/call", {"name": "ghost", "arguments": {}}))
        self.assertEqual(r["error"]["code"], srv.ERR_METHOD_NOT_FOUND)


class TestScoring(unittest.TestCase):
    def test_all_yes_is_ready(self):
        r = srv.handle_request(_req("tools/call", {"name": "readiness_score", "arguments": {"answers": _all_yes()}}))
        text = r["result"]["content"][0]["text"]
        self.assertIn("READY TO APPLY", text)

    def test_strong_but_no_vouch_blocks(self):
        # everything checked EXCEPT the vouch → not ready; names the self-issue rung
        ans = _all_yes(); ans["p_vouch"] = False
        rub = srv.load_rubric()
        rep = srv.score(rub, ans)
        self.assertFalse(rep["go"])
        self.assertIn("vouch", rep["missing_flags"])
        self.assertIn("can't self-issue", rep["verdict"])

    def test_no_ship_blocks(self):
        ans = _all_yes(); ans["p_ship"] = False
        rep = srv.score(srv.load_rubric(), ans)
        self.assertFalse(rep["go"])
        self.assertIn("ship", rep["missing_flags"])

    def test_empty_answers_low_overall(self):
        rep = srv.score(srv.load_rubric(), {})
        self.assertFalse(rep["go"])
        self.assertEqual(rep["overall"], 0.0)

    def test_readiness_score_requires_object(self):
        r = srv.handle_request(_req("tools/call", {"name": "readiness_score", "arguments": {"answers": "yes"}}))
        self.assertTrue(r["result"].get("isError"))

    def test_evidence_tier_classifies(self):
        self.assertEqual(srv.evidence_tier("A teammate signed a reference / vouch for me")["tier"], "attested")
        self.assertEqual(srv.evidence_tier("It's shipped and live in production at a URL")["tier"], "observed")
        self.assertEqual(srv.evidence_tier("I am great at Python")["tier"], "claimed")

    def test_rubric_tool_returns_valid_json(self):
        r = srv.handle_request(_req("tools/call", {"name": "readiness_rubric", "arguments": {}}))
        parsed = json.loads(r["result"]["content"][0]["text"])
        self.assertIn("dimensions", parsed)


if __name__ == "__main__":
    unittest.main()
