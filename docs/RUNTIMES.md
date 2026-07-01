# FDE-os across runtimes — author once, run on four

Objective 2's headline promise: the same skills run on every AI coding agent. The portable unit is
the **`SKILL.md` skill** (Markdown frontmatter + dependency-free Python) — so one `skills/` tree
serves every runtime, with a thin per-runtime manifest on top. No skill is rewritten per agent.

| Runtime | How it loads FDE-os | Status |
|---|---|---|
| **Claude Code** | `.claude-plugin/plugin.json` + `marketplace.json` → `/plugin marketplace add wjlgatech/FDE-os` then `/plugin install fde-os@fde-os`. MCP server auto-wired. | ✅ **Ready** ([PLUGIN.md](PLUGIN.md)) |
| **Codex** | `.codex-plugin/plugin.json` (`"skills": "./skills/"` + an `interface` block) → installs the **same** skills natively. | ✅ **Ready** (this PR) |
| **Hermes** | Hermes reads `SKILL.md` skill directories from its skills folder — the **identical** frontmatter format FDE-os already uses. Drop-in, zero adaptation. | ✅ **Ready** (drop-in, below) |
| **OpenClaw** | OpenClaw uses a TypeScript plugin SDK with a build/release pipeline (npm/clawhub) — not a static manifest. A real wrapper effort, not a one-file add. | ⏳ **Deferred** (scoped below) |

## Why one skills/ tree works for three of four

Claude Code, Codex, and Hermes all consume the **same atomic unit**: a directory with a `SKILL.md`
whose frontmatter is `name` + `description` (+ optional `allowed-tools`). FDE-os's ten skills already
use exactly that shape (verified against an installed Hermes skill). So:

- **Claude** reads `.claude-plugin/plugin.json` → `skills/`
- **Codex** reads `.codex-plugin/plugin.json` → `skills/`  ← *the same directory*
- **Hermes** reads `skills/<name>/SKILL.md` directly

The two manifests are kept in lockstep by CI (`tests/test_plugin_manifest.py`): same `name` + `version`,
both pointing at `./skills/`. Change a skill once; all three runtimes get it.

## Install per runtime

**Claude Code**
```text
/plugin marketplace add wjlgatech/FDE-os
/plugin install fde-os@fde-os
```

**Codex** — install from the repo; Codex reads `.codex-plugin/plugin.json` and registers the skills
in `skills/`. (The `fde-mcp-server` can be added as an MCP server in your Codex config, pointing at
`skills/fde-mcp-server/scripts/server.py`.)

**Hermes** — the skills are already in Hermes' format. From a clone:
```bash
# symlink (stays in sync with the repo) or copy each skill dir into Hermes' skills folder
for s in skills/*/; do ln -s "$(pwd)/$s" ~/.hermes/skills/; done
```
Hermes' agent guide is `AGENTS.md` (which this repo ships), so the skills are documented to the agent
on load. Needs Python 3.11+ for the runnable cores.

## OpenClaw — what it would take (deferred, scoped honestly)

OpenClaw is **not** a drop-in: its plugin system is a TypeScript SDK (`@openclaw/*`) with a gateway
protocol, a build step, and npm/clawhub publication (see `openclaw/` `test/plugin-*`). Porting FDE-os
means authoring a thin TS plugin that shells out to the Python skill cores (or reimplements the
deterministic ones in TS) and conforms to the SDK's extension boundary. That's a real unit of work,
tracked as the remaining cross-runtime gap — not faked with a static manifest here.

## The principle

The skill is the **seam**: a stable, swappable unit the runtimes plug into. Because the unit is
plain Markdown + stdlib Python, three of four runtimes need only a manifest, not a rewrite — which is
the whole point of "author once, run on four." OpenClaw needs an adapter because its boundary is a
typed SDK, not a file convention; naming that honestly is the difference between a claim and a demo.
