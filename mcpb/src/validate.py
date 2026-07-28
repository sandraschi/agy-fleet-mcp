"""Validate MCP server entries against the local filesystem."""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any


def _command_exists(command: str) -> bool:
    if not command:
        return False
    candidate = Path(command)
    if candidate.is_file():
        return True
    return shutil.which(command) is not None


def validate_server(name: str, entry: dict[str, Any]) -> dict[str, Any]:
    issues: list[str] = []
    command = str(entry.get("command", "")).strip()
    args = entry.get("args", [])
    env = entry.get("env") or {}

    if entry.get("url"):
        return {
            "name": name,
            "ok": True,
            "transport": "url",
            "issues": [],
        }

    if not command:
        issues.append("missing command")
    elif not _command_exists(command):
        issues.append(f"command not found: {command}")

    if args is not None and not isinstance(args, list):
        issues.append("args must be a list")

    if not isinstance(env, dict):
        issues.append("env must be an object")

    for key, value in (env.items() if isinstance(env, dict) else []):
        if isinstance(value, str) and ("${" in value or value.startswith("~")):
            issues.append(f"env '{key}' may need expansion")

    return {
        "name": name,
        "ok": not issues,
        "transport": "stdio",
        "issues": issues,
        "disabled": bool(entry.get("disabled", False)),
    }


def validate_servers(servers: dict[str, Any]) -> dict[str, Any]:
    results = [validate_server(name, entry) for name, entry in sorted(servers.items()) if isinstance(entry, dict)]
    failing = [item for item in results if not item["ok"]]
    disabled = [item for item in results if item.get("disabled")]
    return {
        "total": len(results),
        "ok": len(results) - len(failing),
        "failing": len(failing),
        "disabled": len(disabled),
        "results": results,
    }


def agy_binary_status() -> dict[str, Any]:
    agy = shutil.which("agy")
    agymcp = shutil.which("agymcp")
    return {
        "agy_on_path": agy is not None,
        "agy_path": agy,
        "agymcp_on_path": agymcp is not None,
        "agymcp_path": agymcp,
        "gemini_home": str(Path.home() / ".gemini"),
        "gemini_home_exists": (Path.home() / ".gemini").exists(),
    }
