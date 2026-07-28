# agy-fleet-mcp (MCPB Bundle)

FastMCP 3.2 fleet bridge — sync and manage MCP servers for Antigravity CLI (agy) and Gemini config

## Usage

Add to \claude_desktop_config.json\:
\\\json
{
  "mcpServers": {
    "agy-fleet-mcp": {
      "command": "uv",
      "args": ["run", "--directory", "\D:\Dev\repos", "python", "-m", "agy_fleet_mcp"],
      "env": { "PYTHONPATH": "\D:\Dev\repos/src" }
    }
  }
}
\\\

## Tools

- **health**: health
- **agy_fleet_help**: agy_fleet_help
- **agy_fleet_list_locations**: agy_fleet_list_locations
- **agy_fleet_list_servers**: agy_fleet_list_servers
- **agy_fleet_diff**: agy_fleet_diff
- **agy_fleet_sync**: agy_fleet_sync
- **agy_fleet_validate**: agy_fleet_validate
- **agy_fleet_registry**: agy_fleet_registry
- **agy_fleet_apply_tool_budget**: agy_fleet_apply_tool_budget
- **_settings_cursor**: _settings(cursor)
- **_settings_gemini**: _settings(gemini)
- **_settings_antigravity_cli**: _settings(antigravity_cli)
- **_settings_antigravity_ide**: _settings(antigravity_ide)
- **_settings_project**: _settings(project)

## Requirements

- Python 3.12+
- uv
