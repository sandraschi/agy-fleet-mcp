# Cursor MCP — agy-fleet-mcp

## Install script

```powershell
.\install-mcp.ps1 cursor
```

Writes to `%USERPROFILE%\.cursor\mcp.json` under `mcpServers.agy-fleet-mcp`.

## Manual entry

```json
{
  "mcpServers": {
    "agy-fleet-mcp": {
      "command": "C:\\Users\\sandr\\.local\\bin\\uv.exe",
      "args": [
        "--directory",
        "D:\\Dev\\repos\\agy-fleet-mcp",
        "run",
        "python",
        "-m",
        "agy_fleet_mcp",
        "--stdio"
      ],
      "env": {
        "PYTHONUNBUFFERED": "1",
        "FASTMCP_BANNER": "0",
        "FASTMCP_UPDATE_CHECK": "0"
      }
    }
  }
}
```

Adjust `uv.exe` and repo path for your machine.

## Other clients

`install-mcp.ps1` supports: `claude`, `cursor`, `windsurf`, `zed`, `antigravity`, `gemini`, `lmstudio`, `code`, `print`.

```powershell
.\install-mcp.ps1 gemini
```

Syncs install into Gemini shared config — distinct from `agy_fleet_sync` tool (install adds this server; sync copies entire fleet).

## HTTP from Cursor

Cursor typically uses stdio. For HTTP MCP:

1. `.\start.ps1 -Serve`
2. Point client at `http://127.0.0.1:10825/mcp`

## Typical agent session

After install, ask the agent:

1. "List MCP config locations"
2. "Diff cursor vs gemini"
3. "Dry-run sync cursor to gemini"
4. "Apply tool budget on gemini with max 50"

## Coexistence

Safe alongside **agy-mcp** (PyPI) if both installed — different server names and purposes.
