# FDE-os as a Claude Code plugin

The whole toolkit installs as one Claude Code plugin: the ten skills, the
`engagement-readiness` workflow, and the `fde-mcp-server` (wired so its seven tools are callable the
moment you install). The repo root **is** the plugin — `.claude-plugin/plugin.json` declares it and
`.claude-plugin/marketplace.json` makes it installable straight from GitHub.

## Install

```text
/plugin marketplace add wjlgatech/FDE-os
/plugin install fde-os@fde-os
```

(`fde-os@fde-os` = the `fde-os` plugin from the `fde-os` marketplace.) Restart Claude Code if it
prompts. That's it — no clone, no pip.

## What you get

- **Skills** (auto-discovered from `skills/`): `true-scorer`, `criteria-scorer`, `rag-eval-harness`,
  `eval-loop`, `knowledgefy`, `jd-compiler`, `invisible-workflow-mapper`, `field-kit-generator`,
  `fde-mcp-server`.
- **MCP server** (`fde-os`, auto-started): seven callable tools — `true_score`, `rag_eval`,
  `criteria_score`, `eval_loop`, `invisible_workflow_map`, `jd_compile`. Needs **Python 3.11+** on
  your PATH (the server is dependency-free stdlib).
- **Workflow**: `workflows/engagement-readiness` — composes adoption-fit + eval into one GO/NO-GO.

## How it's wired

```jsonc
// .claude-plugin/plugin.json
{
  "name": "fde-os",
  "mcpServers": {
    "fde-os": { "type": "stdio", "command": "python3",
                "args": ["${CLAUDE_PLUGIN_ROOT}/skills/fde-mcp-server/scripts/server.py"] }
  }
}
```

`${CLAUDE_PLUGIN_ROOT}` resolves to wherever Claude Code installs the plugin, so the MCP path works on
any machine. The manifests are CI-checked (`tests/test_plugin_manifest.py`) — a broken manifest fails
the build, never a user's install.

## Local / dev install

From a clone, point the marketplace at the local path instead:

```text
/plugin marketplace add /absolute/path/to/FDE-os
/plugin install fde-os@fde-os
```

## Cross-runtime note

This is the **Claude Code** package. The same `skills/` tree also ships a **Codex** manifest
(`.codex-plugin/plugin.json`) and is a **drop-in for Hermes** (identical `SKILL.md` format) — see
[`RUNTIMES.md`](RUNTIMES.md) for all four runtimes. OpenClaw needs a TypeScript adapter and is the
remaining gap.
