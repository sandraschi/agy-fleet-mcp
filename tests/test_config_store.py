from agy_fleet_mcp.config_store import extract_servers, normalize_servers, wrap_servers


def test_extract_and_wrap_servers():
    data = {"mcpServers": {"alpha": {"command": "uv", "args": ["run", "alpha"]}}}
    servers = extract_servers(data)
    assert "alpha" in servers
    wrapped = wrap_servers(servers)
    assert wrapped["mcpServers"]["alpha"]["command"] == "uv"


def test_normalize_servers_sets_disabled_default():
    servers = normalize_servers({"beta": {"command": "node"}})
    assert servers["beta"]["disabled"] is False
