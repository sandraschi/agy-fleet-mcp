"""Config path resolution for fleet MCP sources and targets."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from agy_fleet_mcp.config import Settings

SOURCE_IDS = ("cursor", "gemini", "antigravity_cli", "antigravity_ide", "project", "opencode", "claude", "registry")
TARGET_IDS = ("cursor", "gemini", "antigravity_cli", "antigravity_ide", "project", "opencode", "claude")


@dataclass(frozen=True)
class ConfigLocation:
    id: str
    label: str
    path: Path
    exists: bool
    kind: str  # mcp_json | fleet_registry


def _project_mcp_path(workspace: Path | None) -> Path:
    root = workspace or Path.cwd()
    return root / ".antigravitycli" / "mcp_config.json"


def resolve_location(location_id: str, settings: Settings, workspace: Path | None = None) -> ConfigLocation:
    mapping: dict[str, tuple[str, Path, str]] = {
        "cursor": ("Cursor global MCP", settings.cursor_mcp_path, "mcp_json"),
        "gemini": ("Gemini / Antigravity shared MCP", settings.gemini_mcp_path, "mcp_json"),
        "antigravity_cli": ("Antigravity CLI MCP", settings.antigravity_cli_mcp_path, "mcp_json"),
        "antigravity_ide": ("Antigravity IDE MCP", settings.antigravity_ide_mcp_path, "mcp_json"),
        "opencode": ("OpenCode MCP", settings.opencode_config_path, "opencode_json"),
        "project": ("Project-local Antigravity CLI", _project_mcp_path(workspace), "mcp_json"),
        "claude": ("Claude Desktop", settings.claude_mcp_path, "mcp_json"),
        "registry": ("Fleet registry catalog", settings.fleet_registry_path, "fleet_registry"),
    }
    if location_id not in mapping:
        raise ValueError(f"Unknown location '{location_id}'. Expected one of: {', '.join(mapping)}")
    label, path, kind = mapping[location_id]
    return ConfigLocation(id=location_id, label=label, path=path, exists=path.exists(), kind=kind)


def list_locations(settings: Settings, workspace: Path | None = None) -> list[ConfigLocation]:
    return [resolve_location(loc_id, settings, workspace) for loc_id in SOURCE_IDS]
