from agy_fleet_mcp.config import Settings
from agy_fleet_mcp.paths import resolve_location


def test_resolve_cursor_location():
    settings = Settings()
    loc = resolve_location("cursor", settings)
    assert loc.id == "cursor"
    assert loc.path.name == "mcp.json"
