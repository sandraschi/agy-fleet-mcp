"""Warn-only startup probe and on-demand pipeline liveness for fleet health checks."""

from __future__ import annotations

import logging
from typing import Any

from agy_fleet_mcp import __version__
from agy_fleet_mcp.config import Settings
from agy_fleet_mcp.config_formats import extract_servers_for_location
from agy_fleet_mcp.config_store import read_json
from agy_fleet_mcp.paths import list_locations, resolve_location
from agy_fleet_mcp.validate import agy_binary_status

log = logging.getLogger(__name__)


def pipeline_liveness(settings: Settings) -> dict[str, Any]:
    """On-demand liveness payload for fleet-agent / orchestrator health probes.

    Reports config presence, the agy CLI, the fleet registry, and whether the
    primary Gemini config respects the enabled-server budget. Non-fatal checks
    degrade the status but never raise.
    """
    locations = list_locations(settings)
    existing = [loc.id for loc in locations if loc.exists]
    missing = [loc.id for loc in locations if not loc.exists]
    agy = agy_binary_status()
    registry_exists = settings.fleet_registry_path.exists()

    budget: dict[str, Any] = {"checked": False, "ok": True, "enabled": 0, "max": settings.max_enabled_servers}
    gemini_loc = resolve_location("gemini", settings)
    if gemini_loc.exists:
        try:
            data = read_json(gemini_loc.path)
            servers = extract_servers_for_location("gemini", data)
            enabled = sum(1 for e in servers.values() if isinstance(e, dict) and not e.get("disabled"))
            budget = {
                "checked": True,
                "enabled": enabled,
                "max": settings.max_enabled_servers,
                "ok": enabled <= settings.max_enabled_servers,
            }
        except Exception as exc:  # pragma: no cover - defensive
            budget["error"] = f"gemini config unreadable: {exc}"

    issues: list[str] = []
    if "cursor" not in existing:
        issues.append("cursor config missing")
    if "gemini" not in existing:
        issues.append("gemini config missing")
    if not agy["agy_on_path"]:
        issues.append("agy CLI not on PATH")
    if not registry_exists:
        issues.append("fleet registry missing")
    if budget.get("checked") and not budget["ok"]:
        issues.append(f"enabled servers exceed budget ({budget['enabled']} > {budget['max']})")

    return {
        "status": "degraded" if issues else "ready",
        "service": "agy-fleet-mcp",
        "version": __version__,
        "checks": {
            "agy_on_path": bool(agy["agy_on_path"]),
            "cursor_config": "cursor" in existing,
            "gemini_config": "gemini" in existing,
            "registry": registry_exists,
            "budget": budget,
        },
        "existing_locations": existing,
        "missing_locations": missing,
        "issues": issues,
    }


async def run_startup_probes(settings: Settings) -> dict[str, object]:
    locations = list_locations(settings)
    existing = [loc.id for loc in locations if loc.exists]
    missing = [loc.id for loc in locations if not loc.exists]
    agy = agy_binary_status()

    if missing:
        log.warning("STARTUP PROBE: missing config locations: %s", ", ".join(missing))
    if not agy["agy_on_path"]:
        log.warning("STARTUP PROBE: agy CLI not on PATH — sync still works; agy runtime not detected")

    registry_exists = settings.fleet_registry_path.exists()
    if not registry_exists:
        log.warning("STARTUP PROBE: fleet registry not found at %s", settings.fleet_registry_path)

    return {
        "ok": True,
        "existing_locations": existing,
        "missing_locations": missing,
        "agy": agy,
        "registry_exists": registry_exists,
    }
