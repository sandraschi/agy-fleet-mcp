# Fleet-agent auto-sync recipe — agy-fleet-mcp

How to wire `agy-fleet-mcp` into **fleet-agent-mcp** (or any MCP orchestrator) so the
Antigravity / Gemini MCP config stays in sync with Cursor without manual invocation.

## Prerequisites

- `agy-fleet-mcp` served over HTTP: `.\start.ps1 -Serve` → MCP at `http://127.0.0.1:10825/mcp`
- `fleet-agent-mcp` running (bridge to other fleet MCP servers)

## Fleet-agent bridge entry

Register `agy-fleet` in fleet-agent's `FLEET_SERVERS` / bridge config so it can call the tools:

```json
"agy-fleet": {
  "url": "http://127.0.0.1:10825/mcp",
  "description": "agy-fleet-mcp — Antigravity MCP config sync/diff/validate",
  "category": "orchestration",
  "key_tools": [
    "agy_fleet_pipeline_liveness",
    "agy_fleet_sync",
    "agy_fleet_diff",
    "agy_fleet_validate",
    "agy_fleet_apply_tool_budget"
  ]
}
```

## Liveness probe

Use `GET http://127.0.0.1:10825/pipeline/liveness` (or the `agy_fleet_pipeline_liveness`
tool) as a fleet-agent readiness gate. It reports `status: ready | degraded` with per-check
detail: config presence, agy on PATH, fleet registry, and whether the Gemini config respects
the enabled-server budget. A non-zero `issues` list means degraded, not crashed — probe for
`status == "ready"` to gate sync.

Example probe call from fleet-agent:

```json
{
  "server": "agy-fleet",
  "tool": "agy_fleet_pipeline_liveness",
  "arguments": {}
}
```

## Sync workflow (dry-run first)

1. `agy_fleet_diff` — preview drift between `cursor` and `gemini`.
2. `agy_fleet_sync(source="cursor", target="gemini", dry_run=true)` — preview the merge.
3. On user confirm → `agy_fleet_sync(..., dry_run=false)`.
4. `agy_fleet_apply_tool_budget(source="gemini", max_enabled=50, dry_run=true)` → confirm → write.

## Safety rules

- **Never** default `dry_run=false` on `agy_fleet_sync` or `agy_fleet_apply_tool_budget`.
- Always back up before write (`BACKUP_ON_WRITE=true`, the default).
- Bind to `127.0.0.1` only (`AGY_FLEET_MCP_HOST=127.0.0.1`).

## Scheduled re-sync

For a watch-style cadence, wrap the workflow in a fleet-agent scheduled task (or the planned
`watch` mode) that runs `agy_fleet_diff` and only touches `agy_fleet_sync(dry_run=false)` when
the diff is non-empty and the liveness probe is `ready`.
