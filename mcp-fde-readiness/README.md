# mcp-fde-readiness — an MCP server (Anthropic's exact FDE deliverable)

A tiny, dependency-free **Model Context Protocol server over stdio** — the literal artifact an
Anthropic FDE ships ("MCP servers, sub-agents, agent skills"). It exposes the FDE **readiness
rubric** as callable tools, so any MCP host can score a candidate's readiness for an Anthropic/OpenAI
FDE role and name the gaps. Same rubric (`../readiness-rubric.json`) that powers the human
self-assessment at [`/readiness.html`](../readiness.html) — **one source of truth, two surfaces**
(agent + human).

## Tools
| tool | does |
|---|---|
| `readiness_rubric` | returns the rubric (dimensions + items) |
| `readiness_score(answers)` | `{item_id: true/false}` → per-dimension %, overall, a **go-to-apply gate**, and gaps |
| `evidence_tier(text)` | classify a piece of evidence: `claimed` / `observed` / `attested` |

The gate encodes the thesis: strong overall **and** you can't pass without the two non-self-issuable
rungs — a **shipped** system (observed) and a **vouch** (attested). 93% with no vouch still returns
`NOT YET`.

## Run it
```bash
python3 mcp-fde-readiness/server.py     # newline-delimited JSON-RPC 2.0 over stdio
```

Wire it into an MCP host (Claude Desktop / Claude Code / Cursor) — `examples/mcp.json`:
```json
{ "mcpServers": {
    "fde-readiness": { "command": "python3", "args": ["mcp-fde-readiness/server.py"] }
} }
```

Smoke-test the transport by hand:
```bash
printf '%s\n' \
 '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}' \
 '{"jsonrpc":"2.0","id":2,"method":"tools/list"}' \
 | python3 mcp-fde-readiness/server.py
```

## Verify
```bash
python3 -m unittest discover -s mcp-fde-readiness/tests -p 'test_*.py'
```
14 tests: MCP protocol (initialize / tools-list / tools-call / ping / notification / unknown-method
+ unknown-tool errors) and the scoring gate (all-yes = ready; strong-but-no-vouch blocks and names
the self-issue rung; no-ship blocks; evidence-tier classification).

_Design note: `handle_request` is a pure `req → resp` function (unit-testable without real stdio);
the stdio loop is a thin wrapper. Dependency-free stdlib, offline. Sibling to `skills/fde-mcp-server`._
