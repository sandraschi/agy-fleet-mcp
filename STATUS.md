# Status — agy-fleet-mcp

**Version:** 0.1.0  
**Last updated:** 2026-06-09  
**Maturity:** Beta — config tools shipped; HTTP secondary to stdio

## Working

- 8 MCP tools (list, diff, sync, validate, registry, budget)
- Stdio + HTTP (`/mcp`, `/health`)
- Merge/replace sync with dry-run default + backup
- Tests: paths, config store, sync
- MCPB manifest + assets + `just mcpb-pack`
- Fleet registry + MCD project page
- Port **10825** (avatar collision resolved)

## Planned (0.2.0)

- `pipeline_liveness` REST + MCP tool
- GitHub MCPB release
- fleet-agent auto-sync recipe doc

## Blockers

- None for config operations
- User must confirm before `dry_run=false` writes
