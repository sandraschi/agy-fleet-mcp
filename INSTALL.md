# Installing agy-fleet-mcp

FastMCP fleet bridge — **sync, diff, validate, and tool-budget** MCP configs for **Antigravity CLI** (`agy`) and Gemini paths. Pushes your Cursor fleet into `~/.gemini/config/mcp_config.json` and project `.antigravitycli/mcp_config.json`.

**Not** [agy-mcp](https://pypi.org/project/agy-mcp/) on PyPI — that package exposes `agy` *as* MCP tools. This repo manages the JSON configs `agy` consumes.

---

## Prerequisites

| Tool | Required for | Windows |
|------|-------------|---------|
| **uv** | Options C–D | `winget install astral-sh.uv` |
| **git** | Clone (C/D) | `winget install Git.Git` |
| **agy** (optional) | Validate only | Antigravity CLI on PATH |

> **Windows:** Close and reopen PowerShell after winget installs so PATH updates apply.

No Google auth, no Node.js — MCP-only server (no glass dashboard).

---

## Option A — Drag and Drop (Claude Desktop)

1. Go to [Releases](https://github.com/sandraschi/agy-fleet-mcp/releases/latest)
2. Download `agy-fleet-mcp*.mcpb` (or build with `just mcpb-pack`)
3. Open Claude Desktop → drag `.mcpb` onto the window → accept install

**Pass criteria:** server appears in MCP list; `agy_fleet_list_locations` returns Cursor + Gemini paths.

---

## Option B — mcpb CLI

Requires Node.js:

```powershell
winget install OpenJS.NodeJS --accept-source-agreements --accept-package-agreements
npx @anthropic-ai/mcpb install https://github.com/sandraschi/agy-fleet-mcp
```

Or pack locally:

```powershell
uv sync
just mcpb-pack
```

---

## Option C — Fastest from source (HTTP MCP)

```powershell
git clone https://github.com/sandraschi/agy-fleet-mcp
cd agy-fleet-mcp
uv sync --extra dev
.\start.ps1 -Serve
```

| Endpoint | URL |
|----------|-----|
| Health | http://127.0.0.1:10825/health |
| MCP HTTP | http://127.0.0.1:10825/mcp |

Port **10825** (was 10793 — conflicts with avatar-mcp; override with `AGY_FLEET_MCP_PORT`).

---

## Option D — MCP client only (stdio)

```powershell
git clone https://github.com/sandraschi/agy-fleet-mcp
cd agy-fleet-mcp
uv sync
.\install-mcp.ps1 cursor
```

Stdio entry:

```powershell
uv run python -m agy_fleet_mcp --stdio
```

Claude Desktop manual JSON (`%APPDATA%\Claude\claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "agy-fleet-mcp": {
      "command": "uv",
      "args": ["run", "--directory", "C:\\path\\to\\agy-fleet-mcp", "python", "-m", "agy_fleet_mcp", "--stdio"],
      "env": { "PYTHONUNBUFFERED": "1", "FASTMCP_BANNER": "0" }
    }
  }
}
```

macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`

Cursor: [docs/CURSOR-MCP.md](docs/CURSOR-MCP.md)

---

## Typical first run

1. `agy_fleet_list_locations` — which config files exist
2. `agy_fleet_diff(left="cursor", right="gemini")` — preview drift
3. `agy_fleet_sync(source="cursor", target="gemini", dry_run=true)` — dry-run merge
4. `agy_fleet_sync(..., dry_run=false)` — write after review
5. `agy_fleet_apply_tool_budget(source="gemini", max_enabled=50)` — Antigravity tool cap

---

## Environment

Prefix **`AGY_FLEET_MCP_`** — see [docs/CONFIGURATION.md](docs/CONFIGURATION.md).

| Variable | Default | Purpose |
|----------|---------|---------|
| `PORT` | `10825` | HTTP bind |
| `CURSOR_MCP_PATH` | `~/.cursor/mcp.json` | Cursor source |
| `GEMINI_MCP_PATH` | `~/.gemini/config/mcp_config.json` | Gemini target |
| `FLEET_REGISTRY_PATH` | `mcp-central-docs/.../fleet-registry.json` | Catalog |

---

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| Port in use | Set `AGY_FLEET_MCP_PORT` or stop conflicting service |
| Sync wrote wrong file | Check `dry_run`; backups created when `backup_on_write=true` |
| `agy` not on PATH | Install Antigravity CLI; validation still works for MCP JSON |

Full guide: [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)

---

## Development

```powershell
just test
just lint
just stdio
just serve
just mcpb-pack
```

See [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md).
