# agy-fleet-mcp — User Guide

## Quick Start

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/sandraschi/agy-fleet-mcp.git
   cd agy-fleet-mcp
   ```

2. **Install dependencies with uv:**
   ```bash
   uv sync
   ```
   This will create a virtual environment and install all required packages including FastMCP, pydantic, and any tool-specific dependencies. The `uv.lock` file ensures deterministic builds across machines.

3. **Configure environment variables:**
   Copy `.env.example` to `.env` and set the appropriate paths. The default paths work for most installations:
   ```
   AGY_FLEET_CURSOR_PATH=C:\Users\sandr\.cursor\mcp.json
   AGY_FLEET_GEMINI_PATH=C:\Users\sandr\.gemini\config\mcp_config.json
   AGY_FLEET_BACKUP_ON_WRITE=true
   AGY_FLEET_LOG_LEVEL=INFO
   ```

4. **Run stdio mode (default for Claude Desktop and Cursor):**
   ```bash
   uv run run_server.py
   ```
   The server will start in stdio mode, listening for MCP JSON-RPC messages on stdin/stdout. This is the default transport for Claude Desktop integration. The server prints startup information to stderr, which Claude Desktop captures for logging purposes.

5. **Add to Claude Desktop mcpServers config:**
   ```json
   {
     "mcpServers": {
       "agy-fleet-mcp": {
         "command": "uv",
         "args": ["run", "--directory", "C:\\Dev\\repos\\agy-fleet-mcp", "run_server.py"],
         "env": {
           "AGY_FLEET_BACKUP_ON_WRITE": "true"
         }
       }
     }
   }
   ```

6. **Verify the server is working:**
   Call `agy_fleet_help()` to get an overview of the server's purpose and `agy_fleet_list_locations()` to see which config files exist on your system. If both return successfully with structured JSON, the server is properly connected.

### First Steps

1. **Discover available config locations:** Start by calling `agy_fleet_list_locations()` to see which config files are present on your system. The response will show you which tools (Cursor, Gemini, Antigravity CLI, Antigravity IDE) have existing MCP configurations.

2. **List servers in each location:** Call `agy_fleet_list_servers(source="cursor")` and `agy_fleet_list_servers(source="gemini")` to see what MCP servers each tool currently has configured.

3. **Diff two configurations:** Call `agy_fleet_diff(left="cursor", right="gemini")` to see the differences between Cursor and Gemini configurations. This is the most important diagnostic step.

4. **Validate a config:** Call `agy_fleet_validate(source="cursor")` to check for misconfigured servers. Validation checks that commands resolve and paths exist.

5. **Sync with dry-run:** Call `agy_fleet_sync(dry_run=True)` to see what would change when syncing from Cursor to Gemini.

6. **Apply the sync:** Call `agy_fleet_sync(dry_run=False)` to write the changes.

7. **Apply tool budget:** Call `agy_fleet_apply_tool_budget(source="gemini", dry_run=True)` to preview budget enforcement, then `dry_run=False` to apply.

## Tutorials

### Tutorial 1: Compare Cursor and Gemini MCP Configs

This is the most common workflow — ensuring Cursor and Gemini agree on which fleet MCP servers are available. Config drift happens when servers are added to one tool but not propagated to the other.

```python
# Step 1: Check what each tool has
cursor_info = agy_fleet_list_servers(source="cursor")
gemini_info = agy_fleet_list_servers(source="gemini")
print(f"Cursor: {cursor_info.get('enabled', 0)}/{cursor_info.get('total', 0)} servers enabled")
print(f"Gemini: {gemini_info.get('enabled', 0)}/{gemini_info.get('total', 0)} servers enabled")

# Step 2: Compute diff
diff = agy_fleet_diff(left="cursor", right="gemini")
only_in_cursor = diff['diff'].get('only_left', [])
only_in_gemini = diff['diff'].get('only_right', [])
changed = diff['diff'].get('changed', {})
print(f"Only in Cursor: {len(only_in_cursor)}")
print(f"Only in Gemini: {len(only_in_gemini)}")
print(f"Changed between them: {len(changed)}")

# Step 3: Show details
for server in only_in_cursor:
    print(f"  CURSOR ONLY: {server}")
for server in only_in_gemini:
    print(f"  GEMINI ONLY: {server}")
for server, changes in changed.items():
    for field, values in changes.items():
        print(f"  {server}.{field}: {values.get('old')} -> {values.get('new')}")
```

### Tutorial 2: Sync Cursor to Gemini (Merge Mode)

After verifying with the diff, sync from Cursor to Gemini. Merge mode adds missing servers and updates changed entries but does not remove anything. This is the safest sync mode for day-to-day use.

```python
# Step 1: Always dry-run first
preview = agy_fleet_sync(
    source="cursor",
    target="gemini",
    mode="merge",
    dry_run=True
)
print(f"Would add {preview.get('added', 0)} new servers")
print(f"Would update {preview.get('updated', 0)} existing servers")
print(f"Would remove {preview.get('removed', 0)} servers (should be 0 in merge mode)")
for addition in preview.get('additions', []):
    print(f"  + {addition['name']}: {addition.get('command', '')} {addition.get('args', [])}")

# Step 2: Only proceed if dry run looks correct
if preview.get('added', 0) > 0 or preview.get('updated', 0) > 0:
    result = agy_fleet_sync(
        source="cursor",
        target="gemini",
        mode="merge",
        dry_run=False
    )
    print(f"Sync complete: +{result['added']} added, ~{result['updated']} updated")
    print(f"Backup created at: {result.get('backup', 'N/A')}")
else:
    print("No changes needed")
```

### Tutorial 3: Sync with Include/Exclude Filtering

Only sync specific servers by pattern, or exclude noisy ones. This is useful when you want to propagate only certain categories of MCP servers — for example, only research tools, or exclude test servers.

```python
# Include only specific server patterns
research_sync = agy_fleet_sync(
    source="cursor",
    target="gemini",
    mode="merge",
    include=["arxiv*", "aiwatcher*", "calibre*", "docs*"],
    dry_run=False
)
print(f"Research servers synced: +{research_sync.get('added', 0)}")

# Exclude unwanted patterns
clean_sync = agy_fleet_sync(
    source="cursor",
    target="gemini",
    mode="merge",
    exclude=["test*", "deprecated*", "legacy*", "dev*"],
    dry_run=False
)

# Only enabled servers (skip disabled ones)
enabled_only = agy_fleet_sync(
    source="cursor",
    target="gemini",
    mode="merge",
    only_enabled=True,
    dry_run=False
)
```

### Tutorial 4: Full Replace of Gemini Config

Replace mode overwrites the entire target configuration with the source. This means servers that exist in the target but not in the source will be REMOVED. Use with extreme caution and always dry-run first.

```python
# Step 1: Understand what will be removed
preview = agy_fleet_sync(
    source="cursor",
    target="gemini",
    mode="replace",
    dry_run=True
)
if preview.get('removed', 0) > 0:
    print(f"WARNING: {preview['removed']} servers would be REMOVED from Gemini!")
    for removal in preview.get('removals', []):
        print(f"  - {removal}")
    print("If you want to keep these, use merge mode instead")

# Step 2: Only proceed if you're absolutely certain
if preview.get('removed', 0) == 0:
    result = agy_fleet_sync(
        source="cursor",
        target="gemini",
        mode="replace",
        dry_run=False
    )
    print(f"Replace complete. Backup: {result.get('backup')}")
```

### Tutorial 5: Validate All Config Sources

Run validation across all config sources to find broken or misconfigured MCP server entries.

```python
for source_id in ["cursor", "gemini", "antigravity_cli"]:
    result = agy_fleet_validate(source=source_id)
    if not result.get('exists'):
        print(f"[{source_id}] Config file not found at {result.get('path', '')}")
        continue

    errors = result['validation'].get('errors', [])
    warnings = result['validation'].get('warnings', [])
    valid = result['validation'].get('valid', 0)
    total = result['validation'].get('total', 0)
    agy_avail = result.get('agy', {}).get('available', False)

    print(f"[{source_id}] {valid}/{total} valid configs, agy={'yes' if agy_avail else 'no'}")
    for w in warnings:
        print(f"  WARN: {w}")
    for e in errors:
        print(f"  ERROR: {e}")
```

### Tutorial 6: Apply Tool Budget for Antigravity

Antigravity CLI has a practical limit on how many MCP servers can be enabled simultaneously. Use the tool budget to stay within this limit.

```python
# Step 1: Preview what would change
budget_preview = agy_fleet_apply_tool_budget(
    source="gemini",
    max_enabled=50,
    dry_run=True
)
print(f"Would keep {budget_preview.get('kept_enabled', 0)} enabled")
print(f"Would disable {budget_preview.get('newly_disabled', 0)} servers")
for server in budget_preview.get('newly_disabled_servers', []):
    print(f"  Would disable: {server}")

# Step 2: Apply with priority list to protect important servers
result = agy_fleet_apply_tool_budget(
    source="gemini",
    max_enabled=50,
    priority=["arxiv-mcp", "aiwatcher-mcp", "arr-mcp", "calibre-mcp", "git*", "docs*"],
    dry_run=False
)
print(f"Disabled {result.get('newly_disabled', 0)} low-priority servers")
print(f"Backup: {result.get('write', {}).get('backup', 'N/A')}")
```

### Tutorial 7: Check Fleet Registry

Get a high-level view of all fleet MCP servers to understand the ecosystem scope.

```python
registry = agy_fleet_registry()
if registry.get('success'):
    print(f"Total servers in fleet: {registry['total']}")
    for cat, count in registry.get('categories', {}).items():
        print(f"  {cat}: {count} servers")
    print(f"First 10 repos: {registry['repos'][:10]}")
```

### Tutorial 8: Per-Project Config Management
Create project-specific MCP configurations that differ from the global config.

```python
# Create a project-specific config by syncing with filters
project_sync = agy_fleet_sync(
    source="cursor",
    target="project",
    mode="merge",
    include=["arxiv*", "calibre*", "git*"],
    workspace="D:\\Dev\\repos\\my-project",
    dry_run=False
)
print(f"Project config created with {project_sync.get('added', 0)} servers")
```

### Tutorial 9: Diagnose Sync Conflicts

When the diff shows many changes and you're unsure which direction to sync.

```python
cursor = agy_fleet_list_servers(source="cursor")
gemini = agy_fleet_list_servers(source="gemini")
diff = agy_fleet_diff(left="cursor", right="gemini")

# Validate both sides
cursor_v = agy_fleet_validate(source="cursor")
gemini_v = agy_fleet_validate(source="gemini")

c_issues = len(cursor_v['validation']['errors'])
g_issues = len(gemini_v['validation']['errors'])
print(f"Cursor issues: {c_issues}, Gemini issues: {g_issues}")

if c_issues <= g_issues:
    print("Recommend syncing FROM cursor TO gemini")
else:
    print("Recommend syncing FROM gemini TO cursor")
```

## Troubleshooting

### "Config file not found"

Returned when the expected config path doesn't exist. Set the appropriate env var:
```
AGY_FLEET_CURSOR_PATH=C:\Actual\Path\mcp.json
```

### "Sync did nothing" / zero changes

Both sides are identical or filters are too restrictive. Check the diff first, then adjust include/exclude patterns.

### Validation errors

- `"Command not found"`: The binary isn't on PATH. Install it or set the full path.
- `"Working directory not found"`: The args contain a path that doesn't exist.
- `"Invalid JSON"`: Manual edit broke the config. Restore from a `.bak` file:
  ```powershell
  Copy-Item "mcp_config.json.20260414_120000.bak" "mcp_config.json"
  ```

## FAQ

**Q: Difference between agy-fleet-mcp and agy-mcp?**
A: agy-fleet-mcp manages MCP config files. agy-mcp (PyPI) wraps the `agy` CLI as MCP tools.

**Q: Does this change my actual configs?**
A: Only with `dry_run=False`. All destructive operations default to dry-run.

**Q: What if a sync corrupts my config?**
A: Backups auto-created before writes. Restore from the `.bak` file.
