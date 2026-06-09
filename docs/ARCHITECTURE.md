# Architecture — agy-fleet-mcp

## Config plane (not execution plane)

```
┌─────────────────┐     agy_fleet_sync      ┌──────────────────────────┐
│ Cursor          │ ───────────────────────►│ Gemini / Antigravity     │
│ ~/.cursor/      │     merge / replace     │ ~/.gemini/.../mcp_*.json │
│ mcp.json        │                         └───────────┬──────────────┘
└─────────────────┘                                     │
                                                        ▼
                                              Antigravity CLI (agy)
                                              reads MCP server entries
```

**agy-fleet-mcp** never spawns `agy`. It reads/writes JSON config files.

## vs agy-mcp (PyPI)

| | agy-fleet-mcp | agy-mcp |
|---|---------------|---------|
| Direction | Fleet JSON → agy configs | agy CLI → MCP tools |
| Transport | stdio / HTTP :10825 | stdio |
| Use case | Sync 100+ fleet servers into agy | Call agy from Cursor |

## Module layout

| Module | Responsibility |
|--------|----------------|
| `paths.py` | Resolve location IDs → filesystem paths |
| `config_store.py` | Parse/write MCP JSON; backup on write |
| `sync.py` | Diff, merge, replace, tool budget |
| `validate.py` | Check `command`/`args`; `agy` on PATH |
| `fleet_registry.py` | Summarize fleet-registry.json |
| `server.py` | FastMCP tool registration |
| `app.py` | FastAPI + `/mcp` mount |

## Sync semantics

- **merge** — add/update servers from source; keep target-only entries
- **replace** — target becomes source set (destructive)
- **dry_run** — default `true`; returns planned diff without write
- **include/exclude** — filter server names
- **only_enabled** — skip disabled entries from source

## Tool budget

Antigravity recommends ~50 enabled MCP tools. `apply_tool_budget`:

1. Sort by `priority` list first
2. Enable up to `max_enabled`
3. Set `disabled: true` on remainder

## Transports

| Mode | Entry |
|------|-------|
| stdio | `python -m agy_fleet_mcp --stdio` |
| HTTP | `python -m agy_fleet_mcp --serve` → uvicorn :10825 |
