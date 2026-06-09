import json
from pathlib import Path

from agy_fleet_mcp.config import Settings
from agy_fleet_mcp.sync import diff_servers, sync_configs


def test_diff_servers_detects_changes():
    left = {"a": {"command": "uv", "disabled": False}}
    right = {"a": {"command": "uv", "disabled": True}, "b": {"command": "node", "disabled": False}}
    diff = diff_servers(left, right)
    assert diff["added_in_right"] == ["b"]
    assert diff["changed"] == ["a"]


def test_sync_merge_dry_run(tmp_path: Path):
    source = tmp_path / "source.json"
    target = tmp_path / "target.json"
    source.write_text(
        json.dumps({"mcpServers": {"one": {"command": "uv", "args": ["run", "one"]}}}),
        encoding="utf-8",
    )
    target.write_text(json.dumps({"mcpServers": {}}), encoding="utf-8")

    settings = Settings(
        cursor_mcp_path=source,
        gemini_mcp_path=target,
        backup_on_write=False,
    )
    result = sync_configs(settings, source="cursor", target="gemini", dry_run=True)
    assert result["selected_count"] == 1
    assert result["result_count"] == 1
    assert '"mcpServers"' in target.read_text(encoding="utf-8")
