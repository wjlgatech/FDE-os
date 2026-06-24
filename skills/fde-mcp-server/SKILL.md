---
name: fde-mcp-server
description: A minimal, dependency-free Model Context Protocol (MCP) server (stdio, JSON-RPC 2.0) that exposes FDE-os's own skills as callable MCP tools — score a draft against the TRUE rubric, evaluate a RAG set. Use it as a runnable reference for the common JD requirement "1+ Claude MCP integrations", to wire FDE-os capabilities into Claude Desktop / Claude Code, or as a skeleton for building your own enterprise MCP server. Stdlib-only; no network.
---

# fde-mcp-server

> A real, runnable **Claude MCP integration** — the thing the CVS Agentic AI Engineer JD lists as a
> hard requirement ("1+ Claude MCP integrations"). It speaks the Model Context Protocol over stdio
> and exposes FDE-os's skills as tools, so it dogfoods the repo *and* is a copy-able skeleton for an
> enterprise MCP server.

## What it exposes (MCP tools)

- **`true_score`** — score a draft against the TRUE rubric (wraps `true-scorer`). Args: `text` or
  `draft_path`.
- **`rag_eval`** — evaluate a RAG eval set (wraps `rag-eval-harness`). Args: `eval_set` (inline) or
  `eval_set_path`, `k`, `thresholds`.

## Protocol

Newline-delimited JSON-RPC 2.0 over stdin/stdout (the MCP stdio transport). Implements
`initialize`, `notifications/initialized`, `ping`, `tools/list`, `tools/call`. Tool-execution
failures come back as `isError` results (so the model sees them); unknown methods are JSON-RPC
errors. Protocol version negotiated from the client's `initialize` (default `2025-06-18`).

## Run / wire it into an MCP host

The host spawns it; you point the host at the script. Example `mcpServers` config (Claude Desktop /
Claude Code style):

```json
{
  "mcpServers": {
    "fde-os": {
      "command": "python3",
      "args": ["skills/fde-mcp-server/scripts/server.py"]
    }
  }
}
```

Drive it by hand (a full handshake) to see it work:

```bash
printf '%s\n%s\n%s\n' \
  '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18"}}' \
  '{"jsonrpc":"2.0","id":2,"method":"tools/list"}' \
  '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"true_score","arguments":{"draft_path":"Delta-01-field-manual.md"}}}' \
  | python3 skills/fde-mcp-server/scripts/server.py
```

## Extend it (the JD-prep exercise)

To satisfy the JD with *your own* integration, add a tool to the `TOOLS` registry: a `name`, a
`description`, a JSON-Schema `inputSchema`, and a `handler(args) -> str`. Point it at a real
enterprise capability (a DB query, a ticket action, a knowledge lookup). Keep the deterministic
core dependency-free; reach for network only inside a handler that needs it.

## Verify

```bash
python3 -m unittest discover -s skills/fde-mcp-server/tests -p 'test_*.py'
```

11 tests: `initialize` (+ version negotiation), `tools/list` schema, notification → no response,
unknown-method JSON-RPC error, `ping`, and `tools/call` actually invoking the wrapped skills
(`true_score` PASS on Post #1, `rag_eval` on an inline set, error results for unknown tool / bad args).

## Provenance

Built for FDE-os as the concrete tool of the CVS prep's Cluster 1 (agentic systems & MCP). Wraps
`true-scorer` and `rag-eval-harness`; stdlib-only, offline, per the repo convention.
