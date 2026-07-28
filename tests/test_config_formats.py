from agy_fleet_mcp.config_formats import build_config_for_location


def test_build_mcp_config_preserves_claude_preferences():
    original = {
        "mcpServers": {"old": {"command": "uv", "args": ["run", "old"]}},
        "preferences": {"coworkWebSearchEnabled": True},
        "coworkUserFilesPath": "C:\\Users\\sandr\\Claude",
    }
    servers = {
        "memops": {"command": "uv", "args": ["run", "memops"], "disabled": False},
        "winops": {"command": "py", "args": ["-m", "winops"], "disabled": True},
    }

    payload = build_config_for_location("claude", servers=servers, original=original)

    assert payload["preferences"] == original["preferences"]
    assert payload["coworkUserFilesPath"] == original["coworkUserFilesPath"]
    assert set(payload["mcpServers"]) == {"memops", "winops"}
    assert "disabled" not in payload["mcpServers"]["memops"]
    assert "disabled" not in payload["mcpServers"]["winops"]


def test_build_mcp_config_preserves_cursor_extras():
    original = {"mcpServers": {}, "someCursorKey": 1}
    servers = {"git-github": {"command": "py", "disabled": False}}

    payload = build_config_for_location("cursor", servers=servers, original=original)

    assert payload["someCursorKey"] == 1
    assert payload["mcpServers"]["git-github"]["disabled"] is False
