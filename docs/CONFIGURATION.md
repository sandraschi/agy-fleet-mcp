# Configuration — agy-fleet-mcp

Environment prefix: **`AGY_FLEET_MCP_`** (via pydantic-settings; also reads `.env`).

## Network

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST` | `127.0.0.1` | HTTP bind address |
| `PORT` | `10825` | HTTP port (MCP at `/mcp`) |

> Port **10825** avoids collision with avatar-mcp backend on **10793**.

## Config paths

| Variable | Default |
|----------|---------|
| `CURSOR_MCP_PATH` | `~/.cursor/mcp.json` |
| `GEMINI_MCP_PATH` | `~/.gemini/config/mcp_config.json` |
| `ANTIGRAVITY_CLI_MCP_PATH` | `~/.gemini/antigravity-cli/mcp_config.json` |
| `ANTIGRAVITY_IDE_MCP_PATH` | `~/.gemini/antigravity/mcp_config.json` |
| `GEMINI_HOME` | `~/.gemini` |

Project-local path is computed: `{workspace}/.antigravitycli/mcp_config.json`

## Fleet

| Variable | Default | Description |
|----------|---------|-------------|
| `FLEET_REGISTRY_PATH` | `D:/Dev/repos/mcp-central-docs/operations/fleet-registry.json` | Catalog for `agy_fleet_registry` |
| `DEFAULT_SOURCE` | `cursor` | Default sync source ID |
| `DEFAULT_TARGET` | `gemini` | Default sync target ID |
| `MAX_ENABLED_SERVERS` | `50` | Tool budget default |
| `BACKUP_ON_WRITE` | `true` | `.bak` timestamp before write |

## Example `.env`

```env
AGY_FLEET_MCP_PORT=10825
AGY_FLEET_MCP_FLEET_REGISTRY_PATH=D:/Dev/repos/mcp-central-docs/operations/fleet-registry.json
AGY_FLEET_MCP_BACKUP_ON_WRITE=true
```

## MCP transport override

```powershell
$env:MCP_TRANSPORT = "http"
uv run python -m agy_fleet_mcp
```

Equivalent to `--serve`.
