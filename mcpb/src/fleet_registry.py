"""Load fleet-registry.json catalog."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from agy_fleet_mcp.config_store import read_json


def load_registry(path: Path) -> list[dict[str, Any]]:
    data = read_json(path)
    fleet = data.get("fleet", [])
    if not isinstance(fleet, list):
        raise ValueError("fleet-registry.json must contain a 'fleet' array")
    return [entry for entry in fleet if isinstance(entry, dict)]


def registry_summary(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"exists": False, "path": str(path), "count": 0, "servers": []}
    entries = load_registry(path)
    servers = [
        {
            "id": entry.get("id"),
            "name": entry.get("name"),
            "port": entry.get("port"),
            "repo_path": entry.get("repo_path"),
            "category": entry.get("category"),
            "status": entry.get("status"),
        }
        for entry in entries
    ]
    return {"exists": True, "path": str(path), "count": len(servers), "servers": servers}
