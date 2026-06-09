# agy-fleet skill

Use **agy-fleet-mcp** when the user wants to wire MCP servers into Antigravity CLI (`agy`) or keep Cursor and Gemini MCP configs in sync.

## When to use

- "sync my fleet into antigravity"
- "diff cursor vs gemini mcp config"
- "cap antigravity tools to 50"
- "validate mcp servers before agy runs"

## Do not confuse with agy-mcp

- **agy-mcp** (PyPI): exposes `agy` as MCP tools for Cursor
- **agy-fleet-mcp** (this repo): manages MCP *config files* that `agy` consumes

## Recommended flow

1. `agy_fleet_list_locations` — see which config files exist
2. `agy_fleet_diff(left="cursor", right="gemini")` — preview drift
3. `agy_fleet_sync(source="cursor", target="gemini", dry_run=true)` — dry-run merge
4. `agy_fleet_sync(..., dry_run=false)` — write after user confirms
5. `agy_fleet_apply_tool_budget(source="gemini", max_enabled=50)` — respect Antigravity tool limits

## Paths

- Cursor: `~/.cursor/mcp.json`
- Gemini shared: `~/.gemini/config/mcp_config.json`
- Project-local agy: `./.antigravitycli/mcp_config.json`
