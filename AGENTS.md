# Agent guide — agy-fleet-mcp

## Role

**Config plane** for Antigravity CLI MCP JSON — not an `agy` subprocess wrapper (see PyPI `agy-mcp`).

## Before coding

1. Read [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).
2. Never default `dry_run=false` on sync/budget tools.
3. Port default **10825** — do not use 10793 (avatar-mcp).

## Key files

| Path | Purpose |
|------|---------|
| `src/agy_fleet_mcp/server.py` | MCP tools |
| `src/agy_fleet_mcp/sync.py` | Merge/replace/budget |
| `src/agy_fleet_mcp/paths.py` | Config location IDs |
| `src/agy_fleet_mcp/config_store.py` | JSON read/write + backup |
| `src/agy_fleet_mcp/validate.py` | Command validation |
| `manifest.json` | MCPB identity |

## Adding a tool

1. Implement logic in appropriate module.
2. Register `@mcp.tool()` in `server.py`.
3. Update `docs/TOOLS.md` and `manifest.json`.
4. Add `assets/prompts/examples.json` entry.

## Tests

```powershell
uv run pytest
uv run ruff check src/ tests/
```

## Docs

Fleet standard: short `README.md`, staged `docs/`, root `INSTALL.md`, `PRD.md`, `CHANGELOG.md`.
