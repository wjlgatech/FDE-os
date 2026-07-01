"""Tests for fde-mcp-server. Run:
  python3 -m unittest discover -s skills/fde-mcp-server/tests -p 'test_*.py'

Checks MCP protocol correctness on the pure handle_request dispatch + that the dogfooded tools
actually invoke the underlying skills.
"""
import importlib.util
import os
import unittest

_HERE = os.path.dirname(__file__)
_SCRIPT = os.path.join(_HERE, "..", "scripts", "server.py")
_REPO = os.path.abspath(os.path.join(_HERE, "..", "..", ".."))
_spec = importlib.util.spec_from_file_location("server", _SCRIPT)
srv = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(srv)


def _req(method, params=None, req_id=1):
    r = {"jsonrpc": "2.0", "id": req_id, "method": method}
    if params is not None:
        r["params"] = params
    return r


class TestProtocol(unittest.TestCase):
    def test_initialize(self):
        resp = srv.handle_request(_req("initialize", {"protocolVersion": "2025-06-18"}))
        self.assertEqual(resp["result"]["serverInfo"]["name"], "fde-os")
        self.assertIn("tools", resp["result"]["capabilities"])
        self.assertEqual(resp["result"]["protocolVersion"], "2025-06-18")

    def test_initialize_defaults_version_when_absent(self):
        resp = srv.handle_request(_req("initialize", {}))
        self.assertEqual(resp["result"]["protocolVersion"], srv.PROTOCOL_VERSION)

    def test_tools_list_exposes_all_skills_with_schema(self):
        resp = srv.handle_request(_req("tools/list"))
        names = {t["name"] for t in resp["result"]["tools"]}
        self.assertEqual(names, {"true_score", "rag_eval", "criteria_score",
                                 "eval_loop", "invisible_workflow_map", "jd_compile", "doc_gate"})
        for t in resp["result"]["tools"]:
            self.assertEqual(t["inputSchema"]["type"], "object")
            self.assertTrue(t["description"])

    def test_new_tools_callable(self):
        # criteria_score returns a verdict
        r = srv.handle_request(_req("tools/call", {
            "name": "criteria_score",
            "arguments": {"text": "We cut latency 40%.", "criteria": [{"type": "must_contain_number", "question": "n"}]},
        }))
        self.assertFalse(r["result"].get("isError"))
        self.assertIn("VERDICT", r["result"]["content"][0]["text"])
        # invisible_workflow_map returns a map
        r2 = srv.handle_request(_req("tools/call", {
            "name": "invisible_workflow_map",
            "arguments": {"signals": [{"dimension": "decider", "observation": "VP decides", "confidence": 0.8}]},
        }))
        self.assertFalse(r2["result"].get("isError"))
        self.assertIn("Invisible Workflow Map", r2["result"]["content"][0]["text"])
        # doc_gate parses a repo doc and returns a verdict
        r3 = srv.handle_request(_req("tools/call", {
            "name": "doc_gate", "arguments": {"path": "README.md"},
        }))
        self.assertFalse(r3["result"].get("isError"))
        self.assertIn("VERDICT", r3["result"]["content"][0]["text"])

    def test_notification_returns_none(self):
        # notifications/initialized is a notification (no id) -> no response
        self.assertIsNone(srv.handle_request({"jsonrpc": "2.0", "method": "notifications/initialized"}))

    def test_unknown_method_is_jsonrpc_error(self):
        resp = srv.handle_request(_req("does/not/exist"))
        self.assertEqual(resp["error"]["code"], srv.ERR_METHOD_NOT_FOUND)

    def test_ping(self):
        resp = srv.handle_request(_req("ping"))
        self.assertEqual(resp["result"], {})


class TestToolsCall(unittest.TestCase):
    def test_true_score_pass_on_post1(self):
        resp = srv.handle_request(_req("tools/call", {
            "name": "true_score",
            "arguments": {"draft_path": "Delta-01-field-manual.md"},
        }))
        text = resp["result"]["content"][0]["text"]
        self.assertIn("PASS", text)
        self.assertNotIn("isError", resp["result"])

    def test_true_score_block_on_weak_text(self):
        resp = srv.handle_request(_req("tools/call", {
            "name": "true_score",
            "arguments": {"text": "# thought\nan abstract idea, no model, no asset, no exercise."},
        }))
        self.assertIn("BLOCK", resp["result"]["content"][0]["text"])

    def test_rag_eval_inline_set(self):
        resp = srv.handle_request(_req("tools/call", {
            "name": "rag_eval",
            "arguments": {
                "eval_set": [{
                    "query": "q",
                    "retrieved": [{"id": "c1", "text": "metformin treats diabetes", "relevant": True}],
                    "gold_context_ids": ["c1"],
                    "answer": "metformin treats diabetes",
                }],
                "k": 5,
                "thresholds": {"recall@k": 0.7, "grounding": 0.8},
            },
        }))
        text = resp["result"]["content"][0]["text"]
        self.assertIn("recall@k", text)
        self.assertIn("PASS", text)

    def test_unknown_tool_is_error_result(self):
        resp = srv.handle_request(_req("tools/call", {"name": "nope", "arguments": {}}))
        self.assertTrue(resp["result"]["isError"])
        self.assertIn("unknown tool", resp["result"]["content"][0]["text"])

    def test_bad_arguments_is_error_result(self):
        # true_score with neither text nor draft_path -> tool error surfaced as isError result
        resp = srv.handle_request(_req("tools/call", {"name": "true_score", "arguments": {}}))
        self.assertTrue(resp["result"]["isError"])


if __name__ == "__main__":
    unittest.main()
