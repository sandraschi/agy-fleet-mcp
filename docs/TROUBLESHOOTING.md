# Troubleshooting — agy-fleet-mcp

## Port 10825 already in use

```powershell
$env:AGY_FLEET_MCP_PORT = "10830"
.\start.ps1 -Serve
```

Default **10825** — not **10793** (avatar-mcp backend occupies 10793).

## Sync wrote unexpected servers

1. Check you used `dry_run=true` on first call.
2. Verify `source` and `target` IDs in tool args.
3. Look for backup: `{config}.bak.{timestamp}` next to target file.
4. Use `agy_fleet_diff` before and after.

## Gemini config empty after sync

- Confirm `~/.gemini/config/mcp_config.json` parent dirs exist.
- `merge` mode won't remove target-only servers; `replace` will.
- Check `include`/`exclude` filters weren't too aggressive.

## agy not found (validate)

`agy_fleet_validate` reports `agy` status separately from MCP server commands. Install Antigravity CLI and add to PATH — sync still works without `agy`.

## Cursor install not showing server

1. `.\install-mcp.ps1 print` — verify JSON block.
2. Reload Cursor MCP (restart or MCP panel refresh).
3. Confirm `uv` path in generated config matches your install.

## Confused with agy-mcp PyPI

| Symptom | Package |
|---------|---------|
| "Expose agy goals as MCP tools" | agy-mcp (PyPI) |
| "Sync Cursor fleet into Gemini JSON" | agy-fleet-mcp (this repo) |

Run `agy_fleet_help` for in-chat clarification.

## HTTP MCP connection refused

Start backend first:

```powershell
.\start.ps1 -Serve
curl http://127.0.0.1:10825/health
```

Stdio mode does not open a port.
