# Status — agy-fleet-mcp

**Version:** 0.2.0  
**Last updated:** 2026-08-21  
**Maturity:** Beta — config tools shipped; HTTP secondary to stdio

## Working

- 9 MCP tools (list, diff, sync, validate, registry, budget, pipeline liveness)
- Stdio + HTTP (`/mcp`, `/health`, `/pipeline/liveness`)
- Merge/replace sync with dry-run default + backup
- `pipeline_liveness` REST + MCP tool for fleet-agent probes
- Tests: paths, config store, sync, liveness
- MCPB manifest + assets + `just mcpb-pack`
- Fleet registry + MCD project page
- Port **10825** (avatar collision resolved)

## Planned (0.3.0)

- GitHub MCPB release
- Watch mode — auto re-sync on `~/.cursor/mcp.json` change
- Project-local `.antigravitycli/mcp_config.json` generation from registry subset

## Blockers

- None for config operations
- User must confirm before `dry_run=false` writes
