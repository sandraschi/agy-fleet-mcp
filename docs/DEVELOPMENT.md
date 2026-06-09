# Development — agy-fleet-mcp

## Setup

```powershell
cd D:\Dev\repos\agy-fleet-mcp
uv sync --extra dev
```

## Commands

| Command | Purpose |
|---------|---------|
| `uv run pytest` | Run tests |
| `uv run ruff check src/ tests/` | Lint |
| `uv run ruff format src/ tests/` | Format |
| `.\start.ps1 -Stdio` | Stdio MCP |
| `.\start.ps1 -Serve` | HTTP :10825 |
| `.\install-mcp.ps1 cursor` | Wire Cursor |
| `just test` | pytest via justfile |
| `just mcpb-pack` | Claude Desktop bundle |

## Project layout

```
agy-fleet-mcp/
├── src/agy_fleet_mcp/   # Python package
├── tests/               # pytest
├── skills/agy-fleet/    # Bundled skill
├── assets/              # MCPB icon + prompts
├── manifest.json        # MCPB + install-mcp
└── docs/                # Staged documentation
```

## Adding a config location

1. Add path to `Settings` in `config.py`
2. Register in `paths.py` `resolve_location` mapping
3. Extend `Literal` types in `server.py` tool signatures
4. Document in `docs/TOOLS.md` and `llms-full.txt`

## Tests

- `test_paths.py` — location resolution
- `test_config_store.py` — JSON round-trip
- `test_sync.py` — diff/merge/budget

Use temp directories; never write real `~/.cursor/mcp.json` in tests.

## MCPB

```powershell
just mcpb-pack
# → dist/agy-fleet-mcp-v0.1.0.mcpb
```

Validate with `check-readme-structure.ps1 -Strict` from mcp-central-docs.
