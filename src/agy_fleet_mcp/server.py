"""FastMCP server: fleet MCP config bridge for Antigravity CLI."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Literal

from fastmcp import FastMCP
from fastmcp.server.providers.skills import SkillsDirectoryProvider

from agy_fleet_mcp.config import Settings, load_settings
from agy_fleet_mcp.config_formats import build_config_for_location, extract_servers_for_location
from agy_fleet_mcp.config_store import read_json, server_summary, write_json
from agy_fleet_mcp.fleet_registry import registry_summary
from agy_fleet_mcp.paths import list_locations, resolve_location
from agy_fleet_mcp.sync import apply_tool_budget, diff_servers, sync_configs
from agy_fleet_mcp.validate import agy_binary_status, validate_servers

LocationId = Literal["cursor", "gemini", "antigravity_cli", "antigravity_ide", "project", "opencode", "claude"]

log = logging.getLogger(__name__)

mcp = FastMCP(
    "agy-fleet-mcp",
    instructions=(
        "Fleet MCP bridge for Antigravity CLI (agy). "
        "Sync, diff, and validate MCP server configs between Cursor, Gemini, Antigravity, and OpenCode paths. "
        "Distinct from PyPI agy-mcp (which exposes agy as MCP tools). "
        "Use agy_fleet_sync to push Cursor fleet entries into ~/.gemini/config/mcp_config.json "
        "or project .antigravitycli/mcp_config.json."
    ),
)

_skills_dir = Path(__file__).resolve().parent.parent.parent / "skills"
if _skills_dir.is_dir():
    mcp.add_provider(SkillsDirectoryProvider(roots=[_skills_dir]))


def _settings() -> Settings:
    return load_settings()


@mcp.tool()
def agy_fleet_help() -> dict[str, str]:
    """Overview of agy-fleet-mcp and how it differs from agy-mcp."""
    return {
        "package": "agy-fleet-mcp",
        "purpose": "Sync and manage MCP fleet configs for Antigravity CLI consumption",
        "not_this": "agy-mcp on PyPI wraps agy as MCP tools for Cursor — opposite direction",
        "default_source": "cursor",
        "default_target": "gemini",
        "docs": "See README.md and docs/FLEET_INTEGRATION.md in the repo",
    }


@mcp.tool()
def agy_fleet_list_locations(workspace: str = "") -> dict[str, Any]:
    """List known MCP config locations and whether each file exists."""
    settings = _settings()
    ws = Path(workspace).resolve() if workspace else None
    locations = list_locations(settings, ws)
    return {
        "locations": [
            {
                "id": loc.id,
                "label": loc.label,
                "path": str(loc.path),
                "exists": loc.exists,
                "kind": loc.kind,
            }
            for loc in locations
        ]
    }


@mcp.tool()
def agy_fleet_list_servers(
    source: LocationId = "cursor",
    workspace: str = "",
) -> dict[str, Any]:
    """List MCP servers defined in a config source."""
    settings = _settings()
    ws = Path(workspace).resolve() if workspace else None
    loc = resolve_location(source, settings, ws)
    if not loc.exists:
        return {"source": source, "path": str(loc.path), "exists": False, "servers": []}
    data = read_json(loc.path)
    servers = extract_servers_for_location(source, data)
    summaries = [server_summary(name, entry) for name, entry in sorted(servers.items()) if isinstance(entry, dict)]
    enabled = sum(1 for item in summaries if not item["disabled"])
    return {
        "source": source,
        "path": str(loc.path),
        "exists": True,
        "total": len(summaries),
        "enabled": enabled,
        "disabled": len(summaries) - enabled,
        "servers": summaries,
    }


@mcp.tool()
def agy_fleet_diff(
    left: LocationId = "cursor",
    right: LocationId = "gemini",
    workspace: str = "",
) -> dict[str, Any]:
    """Diff MCP server sets between two config locations."""
    settings = _settings()
    ws = Path(workspace).resolve() if workspace else None
    left_loc = resolve_location(left, settings, ws)
    right_loc = resolve_location(right, settings, ws)
    left_data = read_json(left_loc.path) if left_loc.exists else {}
    right_data = read_json(right_loc.path) if right_loc.exists else {}
    left_servers = extract_servers_for_location(left_loc.id, left_data) if left_loc.exists else {}
    right_servers = extract_servers_for_location(right_loc.id, right_data) if right_loc.exists else {}
    return {
        "left": {"id": left_loc.id, "path": str(left_loc.path), "exists": left_loc.exists},
        "right": {"id": right_loc.id, "path": str(right_loc.path), "exists": right_loc.exists},
        "diff": diff_servers(left_servers, right_servers),
    }


@mcp.tool()
def agy_fleet_sync(
    source: LocationId = "cursor",
    target: LocationId = "gemini",
    mode: Literal["merge", "replace"] = "merge",
    dry_run: bool = True,
    only_enabled: bool = False,
    include: list[str] | None = None,
    exclude: list[str] | None = None,
    workspace: str = "",
) -> dict[str, Any]:
    """Sync MCP servers from source to target (Cursor → Gemini by default). Set dry_run=false to write."""
    settings = _settings()
    ws = Path(workspace).resolve() if workspace else None
    return sync_configs(
        settings,
        source=source,
        target=target,
        mode=mode,
        dry_run=dry_run,
        include=include,
        exclude=exclude,
        only_enabled=only_enabled,
        workspace=ws,
    )


@mcp.tool()
def agy_fleet_validate(
    source: LocationId = "cursor",
    workspace: str = "",
) -> dict[str, Any]:
    """Validate MCP server commands and transports for a config source."""
    settings = _settings()
    ws = Path(workspace).resolve() if workspace else None
    loc = resolve_location(source, settings, ws)
    if not loc.exists:
        return {"source": source, "path": str(loc.path), "exists": False, "validation": None}
    data = read_json(loc.path)
    servers = extract_servers_for_location(source, data)
    return {
        "source": source,
        "path": str(loc.path),
        "exists": True,
        "validation": validate_servers(servers),
        "agy": agy_binary_status(),
    }


@mcp.tool()
def agy_fleet_registry() -> dict[str, Any]:
    """Read fleet-registry.json catalog (ports, repo paths, categories)."""
    settings = _settings()
    return registry_summary(settings.fleet_registry_path)


@mcp.tool()
def agy_fleet_apply_tool_budget(
    source: LocationId = "gemini",
    max_enabled: int = 50,
    priority: list[str] | None = None,
    dry_run: bool = True,
    workspace: str = "",
) -> dict[str, Any]:
    """Disable servers beyond Antigravity's recommended tool budget (default 50 enabled)."""
    settings = _settings()
    ws = Path(workspace).resolve() if workspace else None
    loc = resolve_location(source, settings, ws)
    if not loc.exists:
        return {"source": source, "path": str(loc.path), "exists": False, "error": "config not found"}

    data = read_json(loc.path)
    servers = extract_servers_for_location(source, data)
    budget = apply_tool_budget(servers, max_enabled=max_enabled, priority=priority)

    write_result = None
    if not dry_run:
        payload = build_config_for_location(loc.id, servers=budget["servers"], original=data)
        backup_path = write_json(loc.path, payload, backup=settings.backup_on_write)
        write_result = {"written": str(loc.path), "backup": str(backup_path) if backup_path else None}

    return {
        "source": source,
        "path": str(loc.path),
        "dry_run": dry_run,
        "max_enabled": max_enabled,
        "kept_enabled": budget["kept_enabled"],
        "newly_disabled": budget["newly_disabled"],
        "write": write_result,
    }
