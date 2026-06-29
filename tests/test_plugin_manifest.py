"""Repo-level invariants for the Claude Code plugin packaging.

Keeps `.claude-plugin/plugin.json` + `marketplace.json` honest: valid JSON, the bundled MCP-server
path actually exists, every skill is discoverable (has a name in its SKILL.md), and the marketplace
source resolves to the plugin root. A broken manifest should fail CI, not a user's `/plugin install`.
"""
import json
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def _load(rel):
    with open(os.path.join(ROOT, rel), encoding="utf-8") as fh:
        return json.load(fh)


class TestPluginManifest(unittest.TestCase):
    def setUp(self):
        self.plugin = _load(".claude-plugin/plugin.json")
        self.market = _load(".claude-plugin/marketplace.json")

    def test_plugin_required_fields(self):
        for key in ("name", "version", "description"):
            self.assertIn(key, self.plugin)
            self.assertTrue(self.plugin[key])

    def test_mcp_server_command_path_exists(self):
        servers = self.plugin.get("mcpServers", {})
        self.assertIn("fde-os", servers)
        args = servers["fde-os"]["args"]
        # resolve ${CLAUDE_PLUGIN_ROOT} to the repo root and confirm the script is there
        rel = args[0].replace("${CLAUDE_PLUGIN_ROOT}/", "")
        self.assertTrue(os.path.isfile(os.path.join(ROOT, rel)), f"MCP server missing: {rel}")

    def test_every_skill_is_discoverable(self):
        skills_dir = os.path.join(ROOT, "skills")
        names = re.compile(r"^name:\s*\S+", re.M)
        for entry in os.listdir(skills_dir):
            sp = os.path.join(skills_dir, entry, "SKILL.md")
            if os.path.isfile(sp):
                with open(sp, encoding="utf-8") as fh:
                    self.assertRegex(fh.read(), names, f"{entry}/SKILL.md needs a name: frontmatter")

    def test_marketplace_lists_plugin_and_source_resolves(self):
        plugins = self.market.get("plugins", [])
        self.assertTrue(plugins)
        entry = plugins[0]
        self.assertEqual(entry["name"], self.plugin["name"])
        src = entry["source"]
        self.assertTrue(os.path.isfile(os.path.join(ROOT, src, ".claude-plugin", "plugin.json")),
                        f"marketplace source {src!r} must resolve to the plugin root")


if __name__ == "__main__":
    unittest.main()
