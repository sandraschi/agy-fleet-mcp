# agy-fleet-mcp — Product Requirements Document

**Status:** ACTIVE (v0.1.0)  
**Package version:** **0.1.0** (`pyproject.toml`)  
**Owner:** Sandra Schieder  
**Port:** **10825** (HTTP MCP + `/health`; stdio primary)  
**Category:** Command / config plane

---

## Overview

Fleet MCP **config bridge** for Antigravity CLI. Syncs Cursor's MCP fleet into Gemini/Antigravity JSON paths, diffs configs, validates commands, reads `fleet-registry.json`, and applies Antigravity's ~50-tool budget.

## Problem Statement

Sandra runs 100+ MCP servers in Cursor. Antigravity CLI (`agy`) reads separate JSON configs under `~/.gemini/` with a lower tool budget. Manual copy/paste drifts quickly; no diff, validation, or budget tooling exists in the CLI itself.

## Name collision

| Package | Direction |
|---------|-----------|
| **agy-mcp** (PyPI) | MCP client → invokes `agy` as tools |
| **agy-fleet-mcp** (this repo) | Fleet JSON → configs `agy` consumes |

Repo name **`agy-fleet-mcp`** avoids PyPI `agy-mcp` confusion.

## Target Audience

- Sandra's fleet — keep Cursor and Antigravity MCP lists aligned
- AI agents — automate sync/diff/validate via MCP tools
- fleet-agent-mcp — HTTP MCP at `:10825/mcp` for orchestration

## Success Metrics

| Metric | Target |
|--------|--------|
| `agy_fleet_sync` dry-run before every write | Default `dry_run=true` |
| Cursor → Gemini merge without data loss | Backup on write |
| Tool budget ≤ 50 enabled on Gemini config | `agy_fleet_apply_tool_budget` |
| Validate reports missing binaries | `agy_fleet_validate` per source |
| Zero port collision with avatar-mcp | Port **10825** (not 10793) |

## Requirements

### Functional — ✅ Tested and Working

- **REQ-001:** List config locations (`agy_fleet_list_locations`).
- **REQ-002:** List servers per source (`agy_fleet_list_servers`).
- **REQ-003:** Diff two sources (`agy_fleet_diff`).
- **REQ-004:** Sync merge/replace with filters (`agy_fleet_sync`).
- **REQ-005:** Validate commands + `agy` on PATH (`agy_fleet_validate`).
- **REQ-006:** Read fleet registry (`agy_fleet_registry`).
- **REQ-007:** Tool budget cap (`agy_fleet_apply_tool_budget`).
- **REQ-008:** Stdio + HTTP MCP transports.
- **REQ-009:** `GET /health` on HTTP mode.
- **REQ-010:** Bundled skill `skill://agy-fleet`.
- **REQ-011:** Cursor install via `install-mcp.ps1`.

### Functional — 🔄 Planned

- **REQ-020:** `pipeline_liveness` endpoint for fleet-agent probes.
- **REQ-021:** Glass dashboard (low priority — config plane is tool-first).
- **REQ-022:** Watch mode — re-sync on `~/.cursor/mcp.json` change.
- **REQ-023:** Generate project `.antigravitycli/mcp_config.json` from registry subset.

### Non-Functional

| Area | Requirement |
|------|-------------|
| **Safety** | `dry_run=true` default on sync and budget |
| **Safety** | JSON backup before write (`backup_on_write`) |
| **Security** | Bind `127.0.0.1` only |
| **Portability** | Paths overridable via `AGY_FLEET_MCP_*` env |

## Config locations

| ID | Path |
|----|------|
| `cursor` | `~/.cursor/mcp.json` |
| `gemini` | `~/.gemini/config/mcp_config.json` |
| `antigravity_cli` | `~/.gemini/antigravity-cli/mcp_config.json` |
| `antigravity_ide` | `~/.gemini/antigravity/mcp_config.json` |
| `project` | `./.antigravitycli/mcp_config.json` |

## Technical Architecture

```
Cursor ~/.cursor/mcp.json
        │
        ▼ agy_fleet_sync (merge/replace)
Gemini ~/.gemini/config/mcp_config.json
        │
        ▼ consumed by
Antigravity CLI (agy)
```

HTTP: FastAPI mounts FastMCP at `/mcp` on **10825**.

## Implementation Plan

### Phase 1 — Shipped (0.1.0)

8 tools, sync/validate/budget, tests, registry, install scripts.

### Phase 2 — Next (0.2.0)

- `pipeline_liveness` + startup probe REST
- MCPB GitHub release
- Optional fleet-agent auto-sync recipe

### Phase 3 — Future

- Web UI for diff visualization
- Registry-driven "essential fleet" profiles

## Out of Scope

- Spawning `agy` subprocesses (see PyPI agy-mcp)
- Managing NotebookLM (see notebooklm-fleet-mcp)
- Editing Cursor rules or skills — MCP JSON only

## References

- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- [docs/FLEET_INTEGRATION.md](docs/FLEET_INTEGRATION.md)
- [mcp-central-docs/projects/agy-fleet-mcp/README.md](../mcp-central-docs/projects/agy-fleet-mcp/README.md)
