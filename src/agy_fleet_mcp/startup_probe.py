"""Warn-only startup probe for fleet health checks."""

from __future__ import annotations

import logging
from pathlib import Path

from agy_fleet_mcp.config import Settings
from agy_fleet_mcp.paths import list_locations
from agy_fleet_mcp.validate import agy_binary_status

log = logging.getLogger(__name__)


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
