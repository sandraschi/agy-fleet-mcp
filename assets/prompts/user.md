# agy-fleet-mcp — user tutorials (Claude Desktop)

## First-time setup

```powershell
git clone https://github.com/sandraschi/agy-fleet-mcp
cd agy-fleet-mcp
uv sync
```

Install MCPB or use `install-mcp.ps1 cursor`. No `agy` required for config sync.

## Sync Cursor fleet into Gemini

1. Ask: *"List MCP config locations"*
2. Ask: *"Diff cursor vs gemini mcp configs"*
3. Ask: *"Dry-run merge cursor into gemini"*
4. Review output → *"Apply sync with dry_run false"*

## Cap Antigravity tools

> Apply tool budget on gemini: max 50 enabled, priority calibre-mcp, arxiv-mcp, notebooklm-fleet-mcp

Always dry-run first.

## Validate before agy session

> Validate gemini mcp config and check if agy is on PATH

## Project-local agy config

> Sync cursor to project antigravity config in D:\Dev\repos\my-project

Use `target="project"` and `workspace` path.

## MCPB

```powershell
just mcpb-pack
```

Drag `dist/agy-fleet-mcp-v0.1.0.mcpb` into Claude Desktop.

## Port note

HTTP MCP uses **10825**, not 10793 (avatar-mcp). Override: `AGY_FLEET_MCP_PORT`.

## Not agy-mcp

If you want to *call agy as tools from Cursor*, install PyPI **agy-mcp** instead. This package only manages JSON configs.

---

*Expand with before/after diff examples and recovery from bad sync via backup files.*
