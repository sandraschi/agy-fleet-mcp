"""Sync MCP server definitions between fleet config locations."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Literal

from agy_fleet_mcp.config_store import (
    extract_servers,
    normalize_servers,
    read_json,
    server_summary,
    wrap_servers,
    write_json,
)
from agy_fleet_mcp.paths import resolve_location
from agy_fleet_mcp.config import Settings

SyncMode = Literal["merge", "replace"]


def _filter_servers(
    servers: dict[str, dict[str, Any]],
    *,
    include: list[str] | None,
    exclude: list[str],
    only_enabled: bool,
) -> dict[str, dict[str, Any]]:
    selected: dict[str, dict[str, Any]] = {}
    include_set = set(include or [])
    for name, entry in servers.items():
        if include and name not in include_set:
            continue
        if name in exclude:
            continue
        if only_enabled and entry.get("disabled"):
            continue
        selected[name] = entry
    return selected


def diff_servers(
    left: dict[str, dict[str, Any]],
    right: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    left_names = set(left)
    right_names = set(right)
    added = sorted(right_names - left_names)
    removed = sorted(left_names - right_names)
    changed: list[str] = []
    for name in sorted(left_names & right_names):
        if left[name] != right[name]:
            changed.append(name)
    return {
        "added_in_right": added,
        "removed_from_right": removed,
        "changed": changed,
        "left_count": len(left),
        "right_count": len(right),
    }


def sync_configs(
    settings: Settings,
    *,
    source: str,
    target: str,
    mode: SyncMode = "merge",
    dry_run: bool = True,
    include: list[str] | None = None,
    exclude: list[str] | None = None,
    only_enabled: bool = False,
    workspace: Path | None = None,
) -> dict[str, Any]:
    source_loc = resolve_location(source, settings, workspace)
    target_loc = resolve_location(target, settings, workspace)

    if source_loc.kind != "mcp_json" or target_loc.kind != "mcp_json":
        raise ValueError("Sync requires MCP JSON sources and targets (not registry)")

    if not source_loc.exists:
        raise FileNotFoundError(f"Source config not found: {source_loc.path}")

    source_servers = normalize_servers(extract_servers(read_json(source_loc.path)))
    target_servers = normalize_servers(extract_servers(read_json(target_loc.path))) if target_loc.exists else {}

    incoming = _filter_servers(
        source_servers,
        include=include,
        exclude=exclude or [],
        only_enabled=only_enabled,
    )

    if mode == "merge":
        merged = dict(target_servers)
        merged.update(incoming)
        result_servers = merged
    elif mode == "replace":
        result_servers = incoming
    else:
        raise ValueError(f"Unsupported sync mode: {mode}")

    diff = diff_servers(target_servers, result_servers)
    preview = [server_summary(name, entry) for name, entry in sorted(result_servers.items())]

    write_result: dict[str, Any] | None = None
    if not dry_run:
        backup_path = write_json(target_loc.path, wrap_servers(result_servers), backup=settings.backup_on_write)
        write_result = {"written": str(target_loc.path), "backup": str(backup_path) if backup_path else None}

    return {
        "dry_run": dry_run,
        "source": {"id": source_loc.id, "path": str(source_loc.path)},
        "target": {"id": target_loc.id, "path": str(target_loc.path)},
        "mode": mode,
        "selected_count": len(incoming),
        "result_count": len(result_servers),
        "diff": diff,
        "servers": preview,
        "write": write_result,
    }


def apply_tool_budget(
    servers: dict[str, dict[str, Any]],
    *,
    max_enabled: int,
    priority: list[str] | None = None,
) -> dict[str, Any]:
    """Disable servers beyond max_enabled, keeping priority names enabled first."""
    priority = priority or []
    priority_set = set(priority)
    enabled_names = [name for name, entry in servers.items() if not entry.get("disabled")]
    ordered = [name for name in priority if name in servers]
    ordered.extend(name for name in sorted(enabled_names) if name not in priority_set)
    keep = set(ordered[:max_enabled])

    adjusted = {}
    disabled_now: list[str] = []
    for name, entry in servers.items():
        copy = dict(entry)
        if not entry.get("disabled") and name not in keep:
            copy["disabled"] = True
            disabled_now.append(name)
        adjusted[name] = copy

    return {
        "max_enabled": max_enabled,
        "kept_enabled": sorted(keep),
        "newly_disabled": disabled_now,
        "servers": adjusted,
    }
