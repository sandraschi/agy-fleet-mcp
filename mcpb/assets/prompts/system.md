# agy-fleet-mcp — MCP Server Capabilities

## Server Overview

agy-fleet-mcp is a FastMCP 3.2 fleet bridge that synchronizes and manages MCP server configurations across multiple tools: Cursor, Gemini, and the Antigravity CLI (agy). It provides diff, sync, validation, registry lookup, and tool budget management for the fleet's MCP ecosystem.

**Key distinction:** This is the _config plane_ for Antigravity CLI MCP JSON — NOT an `agy` subprocess wrapper (that is PyPI `agy-mcp`). It reads, diffs, validates, and writes MCP server JSON entries across different config locations. The server acts as a central control panel for MCP configuration hygiene: ensuring Cursor, Gemini, and Antigravity all agree on which fleet MCP servers should be available.

**Fleet role:** Every MCP server in the sandraschi fleet (200+ repos) has configuration entries spread across Cursor, Gemini, and Antigravity. When servers are added, removed, or updated, agy-fleet-mcp ensures all config files stay in sync. It also enforces tool budget limits — Antigravity CLI has a cap on the number of enabled MCP servers to maintain performance.

**Architecture:** The server reads and writes MCP configuration JSON files at well-known filesystem locations. Each config location is identified by a logical ID (cursor, gemini, antigravity_cli, antigravity_ide, project) and resolved to a specific filesystem path via the Settings class. All destructive operations default to dry-run mode for safety. The fleet registry provides a catalog of all known MCP servers with their ports, repo paths, and categories.

## Tools

### agy_fleet_help

Provides an overview of agy-fleet-mcp and explains the distinction from agy-mcp (PyPI package). Use this tool first when you are unsure which server to use.

**Parameters:** None.

**Return format:**
```json
{
  "package": "agy-fleet-mcp",
  "purpose": "Sync and manage MCP fleet configs for Antigravity CLI consumption",
  "not_this": "agy-mcp on PyPI wraps agy as MCP tools for Cursor — opposite direction",
  "default_source": "cursor",
  "default_target": "gemini",
  "docs": "See README.md and docs/FLEET_INTEGRATION.md in the repo"
}
```

The response clearly distinguishes this server from the PyPI agy-mcp package. The `default_source` and `default_target` fields indicate the most common sync direction (Cursor to Gemini).

### agy_fleet_list_locations

Lists all known MCP config locations and whether each file exists on disk. This is the starting point for understanding which config sources are available for operations like diff, sync, and validate.

**Parameters:**
- `workspace` (str, optional): An absolute filesystem path to a workspace or project directory. When provided, the `project` location resolves to a `.antigravitycli/mcp_config.json` file within this directory. When empty, the project location uses the configured default path. This parameter enables per-project MCP config management.

**Return format:**
```json
{
  "locations": [
    {
      "id": "cursor",
      "label": "Cursor MCP Config",
      "path": "C:\\Users\\sandr\\.cursor\\mcp.json",
      "exists": true,
      "kind": "config"
    },
    {
      "id": "gemini",
      "label": "Gemini MCP Config",
      "path": "C:\\Users\\sandr\\.gemini\\config\\mcp_config.json",
      "exists": true,
      "kind": "config"
    },
    {
      "id": "antigravity_cli",
      "label": "Antigravity CLI MCP Config",
      "path": "C:\\Users\\sandr\\.antigravitycli\\mcp_config.json",
      "exists": false,
      "kind": "config"
    }
  ]
}
```

**Config location IDs and their defaults:**
- `cursor`: `~/.cursor/mcp.json` — Cursor IDE's MCP server definitions.
- `gemini`: `~/.gemini/config/mcp_config.json` — Google Gemini's MCP configuration.
- `antigravity_cli`: `~/.antigravitycli/mcp_config.json` — Antigravity CLI tool config.
- `antigravity_ide`: `~/.antigravity/mcp_config.json` — Antigravity IDE config (separate from CLI).
- `project`: `.antigravitycli/mcp_config.json` — Per-project config within the workspace directory.

The `kind` field indicates the type of configuration : `"config"` for standard MCP server JSON files. The `exists` boolean tells you whether the file is present on disk before attempting operations.

### agy_fleet_list_servers

Lists all MCP servers defined in a specific config source. Shows each server's command, arguments, disabled status, transport type, and associated environment variable keys (values are redacted for security).

**Parameters:**
- `source` (str, default `"cursor"`): Config source to read servers from. Must be one of: `cursor`, `gemini`, `antigravity_cli`, `antigravity_ide`, `project`.
- `workspace` (str, optional): Workspace or project directory path. Required when `source="project"` to resolve the per-project config file.

**Return format:**
```json
{
  "source": "cursor",
  "path": "C:\\Users\\sandr\\.cursor\\mcp.json",
  "exists": true,
  "total": 45,
  "enabled": 42,
  "disabled": 3,
  "servers": [
    {
      "name": "arxiv-mcp",
      "disabled": false,
      "command": "uv",
      "args": ["run", "--directory", "...", "run_server.py"],
      "transport": "stdio",
      "env_keys": ["ARXIV_MCP_SEMANTIC_SCHOLAR_API_KEY"],
      "label": "arXiv Research MCP"
    }
  ]
}
```

When the config file does not exist, the tool returns `{"exists": false, "servers": []}`. The `transport` field is inferred from the command and args (stdio for uv/node/python subprocess args, http for URL-based configs). The `env_keys` list shows which environment variables are configured for each server without exposing their values. The server `name` is the key used in the MCP config JSON, which is also how the server is identified in diff and sync operations.

### agy_fleet_diff

Computes a structural diff of MCP server sets between two config locations. Shows servers present in source but missing in target (only_left), servers in target but not in source (only_right), and servers whose configuration has changed (changed). The diff is useful for understanding configuration drift between tools.

**Parameters:**
- `left` (str, default `"cursor"`): The left-side config source for the comparison.
- `right` (str, default `"gemini"`): The right-side config source for the comparison.
- `workspace` (str, optional): Workspace path for resolving per-project config references.

**Return format:**
```json
{
  "left": {"id": "cursor", "path": "C:\\...", "exists": true},
  "right": {"id": "gemini", "path": "C:\\...", "exists": true},
  "diff": {
    "only_left": ["server-only-in-cursor-1", "server-only-in-cursor-2"],
    "only_right": ["server-only-in-gemini-1"],
    "changed": {
      "server-in-both": {
        "command": {"old": "node", "new": "uv"},
        "args": {"old": ["server.js"], "new": ["run", "server.py"]}
      }
    },
    "summary": "2 only in left, 1 only in right, 1 changed"
  }
}
```

The `only_left` array lists server names that exist in the left source but not in the right. The `only_right` array lists servers that exist in the right source but not in the left. The `changed` object shows servers that exist in both but have differences in their configuration (command, args, env keys, etc.) with old/new values. When a config file doesn't exist, the corresponding side returns `exists: false` and empty server lists.

### agy_fleet_sync

Syncs MCP servers from a source config location to a target. This is the primary tool for propagating MCP configuration changes. By default it syncs from Cursor to Gemini in merge mode with dry_run=True.

**IMPORTANT SAFETY RULE:** `dry_run` defaults to `True`. You must explicitly set `dry_run=False` to write any changes to disk. Always preview with dry_run first.

**Parameters:**
- `source` (str, default `"cursor"`): Config source to read servers from.
- `target` (str, default `"gemini"`): Config destination to write servers to.
- `mode` (str, default `"merge"`): Sync strategy — `"merge"` adds missing servers and updates changed ones but does NOT remove servers that only exist in the target. `"replace"` overwrites the entire target with the source's server list, removing any servers not in the source. Use replace with extreme caution.
- `dry_run` (bool, default `True`): When True, simulates the sync operation and reports what would change without writing anything to disk. Backups are also only created during actual writes.
- `only_enabled` (bool, default `False`): When True, only enabled servers from the source are included in the sync. Disabled servers are skipped.
- `include` (list[str], optional): Only sync servers whose names match these substring patterns. Patterns are case-insensitive. Example: `["arxiv*", "aiwatcher*"]`.
- `exclude` (list[str], optional): Exclude servers whose names match these substring patterns. Exclusion takes priority over inclusion.
- `workspace` (str, optional): Workspace path for resolving project-scoped config.

**Return format (merge mode):**
```json
{
  "source": "cursor",
  "target": "gemini",
  "mode": "merge",
  "dry_run": true,
  "added": 3,
  "updated": 2,
  "removed": 0,
  "additions": [
    {"name": "new-server", "command": "uv", "args": ["run", "server.py"]}
  ],
  "removals": [],
  "warnings": [],
  "backup": null
}
```

In replace mode with `dry_run=False`, the response also includes a `backup` field pointing to the timestamped backup file that was created before the write. If files exist at both source and target paths but one is empty, a warning is included in the response.

### agy_fleet_validate

Validates MCP server configurations for a given config source. Checks that the JSON structure is valid, that commands resolve on the system PATH, that working directories exist, and that the transport configuration is consistent. Also reports whether the `agy` CLI binary is available and its version.

**Parameters:**
- `source` (str, default `"cursor"`): Config source to validate.
- `workspace` (str, optional): Workspace path for per-project config validation.

**Return format:**
```json
{
  "source": "cursor",
  "path": "C:\\...",
  "exists": true,
  "validation": {
    "errors": [],
    "warnings": [
      "Server 'old-server' has command 'python2' which is not on PATH",
      "Server 'test-server' has working directory that does not exist"
    ],
    "total": 45,
    "valid": 43
  },
  "agy": {
    "available": true,
    "version": "0.1.0",
    "path": "C:\\Users\\sandr\\scoop\\shims\\agy.exe"
  }
}
```

Validation checks: (1) Whether the command binary (e.g., `uv`, `node`, `python`) can be found on the system PATH. (2) Whether referenced working directories exist on the filesystem. (3) Whether the JSON structure conforms to the expected MCP server format. (4) Whether the transport is consistent with the command (stdio commands should have appropriate args). The `agy` block reports whether the agy binary itself is available, which is needed for some integration scenarios.

### agy_fleet_registry

Reads the fleet-registry.json catalog, which maps MCP server names to their ports, repo paths, categories, and metadata. This provides a high-level view of all servers that exist in the sandraschi fleet ecosystem.

**Parameters:** None.

**Return format:**
```json
{
  "success": true,
  "registry_path": "C:\\...\\fleet-registry.json",
  "total": 200,
  "categories": {
    "webapp": 150,
    "infrastructure": 30,
    "agent": 20
  },
  "repos": ["arxiv-mcp", "aiwatcher-mcp", "arr-mcp", "calibre-mcp", "docs-mcp", "..."],
  "servers_by_category": {
    "webapp": [{"name": "arxiv-mcp", "port": 10770, "repo": "arxiv-mcp"}],
    "infrastructure": [...]
  }
}
```

The registry file is loaded from the path specified by `AGY_FLEET_FLEET_REGISTRY_PATH`. If the file does not exist, the tool returns `success: false` with a descriptive error. The response includes category breakdowns for high-level understanding of the fleet composition.

### agy_fleet_apply_tool_budget

Enforces Antigravity's recommended tool budget by disabling servers beyond the `max_enabled` threshold. This is critical for Antigravity CLI, which limits how many MCP servers can be exposed simultaneously to maintain performance and manage context. Servers can be preserved via the `priority` list.

**Parameters:**
- `source` (str, default `"gemini"`): Config source to apply the budget to.
- `max_enabled` (int, default `50`): Maximum number of MCP servers that should remain enabled. Servers beyond this count will be disabled (not deleted).
- `priority` (list[str], optional): Server name substring patterns to keep enabled even if the budget is exceeded. Priority servers are always kept enabled regardless of count.
- `dry_run` (bool, default `True`): When True, reports which servers would be disabled without writing anything.
- `workspace` (str, optional): Workspace path for per-project budget enforcement.

**Return format:**
```json
{
  "source": "gemini",
  "path": "C:\\...",
  "dry_run": true,
  "max_enabled": 50,
  "kept_enabled": 50,
  "newly_disabled": 5,
  "write": null,
  "newly_disabled_servers": [
    "low-priority-server-1",
    "experimental-server"
  ]
}
```

When `dry_run=false`, the tool writes the updated configuration and includes a `write` object with the path that was written and the backup path. The budget algorithm sorts servers by: priority servers first (kept regardless), then by the order they appear in the config. Servers beyond the max_enabled count are set to `disabled: true` in the config JSON.

### _settings_cursor / _settings_gemini / _settings_antigravity_cli / _settings_antigravity_ide / _settings_project

These are internal tools for reading and writing settings specific to each config source. They are prefixed with underscore to indicate they are lower-level operations. Use the primary tools (list_servers, sync, diff) for most operations.

**Parameters:** Varies by tool. Typically accepts operation type and value fields.

**Common use cases:**
- Reading the current config path for a specific tool
- Setting the path override for a specific tool
- Checking whether a specific config file is writable

## Configuration

All configuration is via environment variables with the prefix `AGY_FLEET_`:

| Variable | Default | Purpose |
|----------|---------|---------|
| `AGY_FLEET_CURSOR_PATH` | `~/.cursor/mcp.json` | Override the Cursor MCP config file location |
| `AGY_FLEET_GEMINI_PATH` | `~/.gemini/config/mcp_config.json` | Override the Gemini MCP config file location |
| `AGY_FLEET_ANTIGRAVITY_CLI_PATH` | `~/.antigravitycli/mcp_config.json` | Override the Antigravity CLI config location |
| `AGY_FLEET_ANTIGRAVITY_IDE_PATH` | `~/.antigravity/mcp_config.json` | Override the Antigravity IDE config location |
| `AGY_FLEET_FLEET_REGISTRY_PATH` | `./fleet-registry.json` | Override the fleet registry catalog path |
| `AGY_FLEET_BACKUP_ON_WRITE` | `true` | Create timestamped `.bak` copies before any write |
| `AGY_FLEET_LOG_LEVEL` | `INFO` | Set logging verbosity (DEBUG, INFO, WARNING, ERROR) |

The `AGY_FLEET_BACKUP_ON_WRITE` setting is critical for safety. When enabled (default), every write operation creates a timestamped backup file (e.g., `mcp_config.json.20260414_120000.bak`) at the same location as the original file. These backups can be used to recover from accidental misconfiguration.

## Data Sources

**Config Files (JSON):** Each tool stores MCP server configurations in a standard JSON file with the MCP format:
```json
{
  "mcpServers": {
    "server-name": {
      "command": "uv",
      "args": ["run", "--directory", "/path", "run_server.py"],
      "env": {"KEY": "value"}
    }
  }
}
```

**Fleet Registry (JSON):** The fleet-registry.json file catalogs all MCP servers with metadata:
```json
{
  "repos": {"arxiv-mcp": {"port": 10770, "category": "research", "path": "..."}},
  "categories": {"research": [...], "media": [...]}
}
```

**Server Configuration Schema:** Each server entry is validated against a schema that requires `command` (string), optional `args` (list of strings), optional `env` (object of key-value pairs), and optional `disabled` (boolean). The server summary extracts: name, disabled status, command, args preview, transport type, and environment variable keys (values redacted).

## Error Handling

All tools return structured dicts with consistent error patterns:
- `error` (str): Human-readable error description
- `error_type` (str): Machine-readable error category
- `recovery_options` (list[str], optional): Suggested recovery steps

Common error types: `FileNotFoundError` (config path doesn't exist), `JSONDecodeError` (malformed config file), `PermissionError` (file not writable), `ValueError` (invalid parameter).

When a config file does not exist, tools return `{"exists": false}` rather than raising exceptions, allowing graceful handling by the caller. The sync tool validates that both source and target paths are valid before attempting any operation.

## Security

- Environment variable values are redacted in server summaries — only key names are shown
- Timestamped backups are created before every destructive write operation
- All sync and budget operations default to `dry_run=True` — explicit opt-in required to write
- Config paths are resolved relative to the user's home directory, preventing path traversal
- Project-scoped configs are restricted to the provided workspace directory
- The include/exclude filters in sync prevent accidental overwriting of unrelated configs
