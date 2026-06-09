"""Read and write MCP JSON config files."""

from __future__ import annotations

import json
import shutil
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    text = path.read_text(encoding="utf-8")
    if not text.strip():
        return {}
    data = json.loads(text)
    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON object in {path}")
    return data


def write_json(path: Path, data: dict[str, Any], *, backup: bool = True) -> Path | None:
    path.parent.mkdir(parents=True, exist_ok=True)
    backup_path: Path | None = None
    if backup and path.exists():
        stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
        backup_path = path.with_suffix(path.suffix + f".bak.{stamp}")
        shutil.copy2(path, backup_path)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return backup_path


def extract_servers(data: dict[str, Any]) -> dict[str, Any]:
    servers = data.get("mcpServers")
    if servers is None:
        return {}
    if not isinstance(servers, dict):
        raise ValueError("mcpServers must be an object")
    return servers


def wrap_servers(servers: dict[str, Any]) -> dict[str, Any]:
    return {"mcpServers": servers}


def normalize_server_entry(name: str, entry: Any) -> dict[str, Any]:
    if not isinstance(entry, dict):
        raise ValueError(f"Server '{name}' must be an object")
    normalized = dict(entry)
    if "disabled" not in normalized:
        normalized["disabled"] = False
    return normalized


def normalize_servers(servers: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {name: normalize_server_entry(name, entry) for name, entry in servers.items()}


def server_summary(name: str, entry: dict[str, Any]) -> dict[str, Any]:
    command = entry.get("command", "")
    args = entry.get("args", [])
    env_keys = sorted((entry.get("env") or {}).keys())
    return {
        "name": name,
        "command": command,
        "args": args if isinstance(args, list) else [],
        "disabled": bool(entry.get("disabled", False)),
        "env_keys": env_keys,
        "has_url": "url" in entry,
    }
