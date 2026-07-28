# MCP tools — agy-fleet-mcp

## agy_fleet_help

Package overview and agy-mcp distinction. No parameters.

## agy_fleet_list_locations

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `workspace` | str | `""` | Project root for `project` location |

Returns all known paths with `exists` flags.

## agy_fleet_list_servers

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `source` | enum | `cursor` | Config source ID (`cursor`, `gemini`, `antigravity_cli`, `antigravity_ide`, `project`, `opencode`) |
| `workspace` | str | `""` | Project root |

Returns `servers` summaries: name, command, disabled, transport hints.

## agy_fleet_diff

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `left` | enum | `cursor` | Left config |
| `right` | enum | `gemini` | Right config |
| `workspace` | str | `""` | Project root |

Returns `diff`: added, removed, changed server names.

## agy_fleet_sync

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `source` | enum | `cursor` | Copy from |
| `target` | enum | `gemini` | Copy to |
| `mode` | `merge` \| `replace` | `merge` | Merge strategy |
| `dry_run` | bool | `true` | Preview only |
| `only_enabled` | bool | `false` | Skip disabled source servers |
| `include` | list[str] | null | Whitelist server names |
| `exclude` | list[str] | null | Blacklist server names |
| `workspace` | str | `""` | Project root |

**Safety:** always call with `dry_run=true` first.

## agy_fleet_validate

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `source` | enum | `cursor` | Config to validate |
| `workspace` | str | `""` | Project root |

Returns per-server validation + `agy` binary status.

## agy_fleet_registry

No parameters. Reads `FLEET_REGISTRY_PATH` and returns summary (ids, ports, categories).

## agy_fleet_apply_tool_budget

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `source` | enum | `gemini` | Config to modify |
| `max_enabled` | int | `50` | Max enabled servers |
| `priority` | list[str] | null | Keep these enabled first |
| `dry_run` | bool | `true` | Preview only |
| `workspace` | str | `""` | Project root |

Sets `disabled: true` on servers beyond budget.

## Source / target IDs

`cursor` · `gemini` · `antigravity_cli` · `antigravity_ide` · `project`
