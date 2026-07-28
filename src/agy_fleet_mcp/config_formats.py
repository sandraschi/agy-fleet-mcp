"""MCP config format adapters (mcpServers vs OpenCode mcp.*)."""

from __future__ import annotations

from typing import Any

MCP_SERVERS_FORMAT = "mcp_servers"
OPENCODE_FORMAT = "opencode"

LOCATION_FORMATS: dict[str, str] = {
    "cursor": MCP_SERVERS_FORMAT,
    "gemini": MCP_SERVERS_FORMAT,
    "antigravity_cli": MCP_SERVERS_FORMAT,
    "antigravity_ide": MCP_SERVERS_FORMAT,
    "project": MCP_SERVERS_FORMAT,
    "claude": MCP_SERVERS_FORMAT,
    "opencode": OPENCODE_FORMAT,
}


def location_format(location_id: str) -> str:
    fmt = LOCATION_FORMATS.get(location_id)
    if fmt is None:
        raise ValueError(f"Unknown location '{location_id}'")
    return fmt


def _opencode_entry_to_canonical(entry: dict[str, Any]) -> dict[str, Any]:
    command_parts = entry.get("command", [])
    if not isinstance(command_parts, list) or not command_parts:
        command = ""
        args: list[Any] = []
    else:
        command = str(command_parts[0])
        args = [str(part) for part in command_parts[1:]]

    env = entry.get("environment") or entry.get("env") or {}
    if not isinstance(env, dict):
        env = {}

    disabled = False
    if entry.get("disabled") is True:
        disabled = True
    if entry.get("enabled") is False:
        disabled = True

    canonical: dict[str, Any] = {
        "command": command,
        "args": args,
        "env": dict(env),
        "disabled": disabled,
    }
    if entry.get("type"):
        canonical["_opencode_type"] = entry["type"]
    if "timeout" in entry:
        canonical["_opencode_timeout"] = entry["timeout"]
    return canonical


def _canonical_to_opencode_entry(name: str, entry: dict[str, Any], existing: dict[str, Any] | None) -> dict[str, Any]:
    base = dict(existing or {})
    command = str(entry.get("command", "")).strip()
    args = entry.get("args") or []
    if not isinstance(args, list):
        args = []

    oc: dict[str, Any] = {
        "type": entry.get("_opencode_type") or base.get("type") or "local",
        "command": ([command, *list(args)]) if command else list(base.get("command") or []),
        "environment": dict(entry.get("env") or {}),
        "enabled": not bool(entry.get("disabled", False)),
        "timeout": entry.get("_opencode_timeout") or base.get("timeout") or 300000,
    }
    return oc


def extract_servers_for_location(location_id: str, data: dict[str, Any]) -> dict[str, Any]:
    fmt = location_format(location_id)
    if fmt == MCP_SERVERS_FORMAT:
        servers = data.get("mcpServers")
        if servers is None:
            return {}
        if not isinstance(servers, dict):
            raise ValueError("mcpServers must be an object")
        return servers

    mcp = data.get("mcp")
    if mcp is None:
        return {}
    if not isinstance(mcp, dict):
        raise ValueError("mcp must be an object")
    return {name: _opencode_entry_to_canonical(entry) for name, entry in mcp.items() if isinstance(entry, dict)}


def _servers_for_write(location_id: str, servers: dict[str, Any]) -> dict[str, Any]:
    """Claude Desktop does not understand agy-fleet's per-server disabled flag."""
    if location_id != "claude":
        return servers
    cleaned: dict[str, Any] = {}
    for name, entry in servers.items():
        if not isinstance(entry, dict):
            continue
        cleaned[name] = {k: v for k, v in entry.items() if k != "disabled"}
    return cleaned


def build_config_for_location(
    location_id: str,
    *,
    servers: dict[str, Any],
    original: dict[str, Any] | None = None,
) -> dict[str, Any]:
    fmt = location_format(location_id)
    if fmt == MCP_SERVERS_FORMAT:
        base = dict(original or {})
        base["mcpServers"] = _servers_for_write(location_id, servers)
        return base

    base = dict(original or {})
    existing_mcp = base.get("mcp") if isinstance(base.get("mcp"), dict) else {}
    opencode_mcp: dict[str, Any] = {}
    for name, entry in servers.items():
        if not isinstance(entry, dict):
            continue
        prior = existing_mcp.get(name) if isinstance(existing_mcp.get(name), dict) else None
        opencode_mcp[name] = _canonical_to_opencode_entry(name, entry, prior)
    base["mcp"] = opencode_mcp
    return base
