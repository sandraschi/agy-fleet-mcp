# Changelog

All notable changes to **agy-fleet-mcp** are documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

### Added
- Fleet documentation stack: `INSTALL.md`, `PRD.md`, `CHANGELOG.md`, `llms-full.txt`, `AGENTS.md`, `STATUS.md`.
- Staged `docs/` index: ARCHITECTURE, CONFIGURATION, TOOLS, TROUBLESHOOTING, DEVELOPMENT, CURSOR-MCP, FASTMCP_FEATURES.
- MCPB assets: `assets/icon.png`, `assets/prompts/*`, `.mcpbignore`, `just mcpb-pack`.
- MCD project page: `mcp-central-docs/projects/agy-fleet-mcp/`.

### Changed
- **Port** — HTTP MCP moved from **10793** (avatar-mcp collision) to **10825** (`AGY_FLEET_MCP_PORT`).
- `README.md` — fleet short form with TOC and doc table.
- `fleet-registry.json` — port **10825**.
- `operations/WEBAPP_PORTS.md` — **10825** registered.

## [0.1.0] — 2026-06-09

### Added
- **FastMCP 3.2** config bridge for Antigravity CLI (`agy`) and Gemini MCP JSON paths.
- **8 MCP tools** — list locations/servers, diff, sync, validate, registry read, tool budget.
- **Config sources** — `cursor`, `gemini`, `antigravity_cli`, `antigravity_ide`, `project`.
- **Sync modes** — merge/replace, dry-run default, include/exclude filters.
- **Tool budget** — `agy_fleet_apply_tool_budget` caps enabled servers (~50 Antigravity limit).
- **HTTP transport** — FastAPI + MCP at `/mcp`, `GET /health`.
- **Bundled skill** — `skills/agy-fleet/SKILL.md`.
- **Tests** — paths, config store, sync.
- **Install** — `install-mcp.ps1`, `start.ps1`, Cursor MCP wiring.

### Notes
- **Not** [agy-mcp](https://pypi.org/project/agy-mcp/) on PyPI — opposite direction (config plane, not agy-as-tool).
- Stdio is the primary transport for Cursor; HTTP optional for fleet-agent.
