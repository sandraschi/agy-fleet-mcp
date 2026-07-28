import json

from agy_fleet_mcp.config_store import extract_servers, normalize_servers, read_json, wrap_servers


def test_extract_and_wrap_servers():
    data = {"mcpServers": {"alpha": {"command": "uv", "args": ["run", "alpha"]}}}
    servers = extract_servers(data)
    assert "alpha" in servers
    wrapped = wrap_servers(servers)
    assert wrapped["mcpServers"]["alpha"]["command"] == "uv"


def test_normalize_servers_sets_disabled_default():
    servers = normalize_servers({"beta": {"command": "node"}})
    assert servers["beta"]["disabled"] is False


def test_read_json_strips_utf8_bom(tmp_path):
    path = tmp_path / "mcp.json"
    payload = {"mcpServers": {"demo": {"command": "uv"}}}
    path.write_bytes(b"\xef\xbb\xbf" + json.dumps(payload).encode("utf-8"))
    assert read_json(path) == payload
