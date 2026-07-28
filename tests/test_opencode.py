import json
from pathlib import Path

from agy_fleet_mcp.config import Settings
from agy_fleet_mcp.config_formats import (
    build_config_for_location,
    extract_servers_for_location,
)
from agy_fleet_mcp.paths import resolve_location
from agy_fleet_mcp.sync import sync_configs


def test_resolve_opencode_location():
    settings = Settings()
    loc = resolve_location("opencode", settings)
    assert loc.id == "opencode"
    assert loc.path.name == "opencode.json"
    assert loc.kind == "opencode_json"


def test_opencode_roundtrip_preserves_instructions():
    original = {
        "instructions": ["fleet rules"],
        "mcp": {
            "memops": {
                "type": "local",
                "command": ["uv.exe", "run", "memops"],
                "environment": {"PYTHONUNBUFFERED": "1"},
                "enabled": True,
                "timeout": 120000,
            }
        },
    }
    servers = extract_servers_for_location("opencode", original)
    assert servers["memops"]["command"] == "uv.exe"
    assert servers["memops"]["args"] == ["run", "memops"]
    assert servers["memops"]["disabled"] is False

    rebuilt = build_config_for_location("opencode", servers=servers, original=original)
    assert rebuilt["instructions"] == ["fleet rules"]
    assert rebuilt["mcp"]["memops"]["enabled"] is True
    assert rebuilt["mcp"]["memops"]["timeout"] == 120000


def test_sync_cursor_to_opencode_merge(tmp_path: Path):
    source = tmp_path / "cursor.json"
    target = tmp_path / "opencode.json"
    source.write_text(
        json.dumps({"mcpServers": {"git-github": {"command": "uv", "args": ["run", "git"]}}}),
        encoding="utf-8",
    )
    target.write_text(
        json.dumps(
            {
                "instructions": ["keep me"],
                "mcp": {
                    "memops": {
                        "type": "local",
                        "command": ["uv", "run", "memops"],
                        "environment": {},
                        "enabled": True,
                        "timeout": 300000,
                    }
                },
            }
        ),
        encoding="utf-8",
    )

    settings = Settings(
        cursor_mcp_path=source,
        opencode_config_path=target,
        backup_on_write=False,
    )
    preview = sync_configs(settings, source="cursor", target="opencode", dry_run=True)
    assert preview["selected_count"] == 1
    assert preview["result_count"] == 2

    sync_configs(settings, source="cursor", target="opencode", dry_run=False)
    written = json.loads(target.read_text(encoding="utf-8"))
    assert written["instructions"] == ["keep me"]
    assert "git-github" in written["mcp"]
    assert "memops" in written["mcp"]


def test_opencode_disabled_maps_to_enabled_false():
    data = {
        "mcp": {
            "slow": {
                "type": "local",
                "command": ["uv", "run", "slow"],
                "environment": {},
                "enabled": False,
                "timeout": 1,
            }
        }
    }
    servers = extract_servers_for_location("opencode", data)
    assert servers["slow"]["disabled"] is True
    rebuilt = build_config_for_location("opencode", servers=servers, original=data)
    assert rebuilt["mcp"]["slow"]["enabled"] is False
