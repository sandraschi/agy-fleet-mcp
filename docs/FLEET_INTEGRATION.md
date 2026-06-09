# Fleet integration — agy-fleet-mcp

## Role

`agy-fleet-mcp` is the **config plane** for Antigravity CLI MCP consumption. It does not spawn `agy` subprocesses (see PyPI `agy-mcp` for that).

| Package | Direction |
|---------|-----------|
| `agy-mcp` | MCP client → calls `agy` |
| `agy-fleet-mcp` | Fleet configs → Antigravity/Gemini MCP JSON |

## Ports

| Service | Port |
|---------|------|
| HTTP MCP | **10825** |
| Health | `GET /health` |

> **10825** replaces an earlier **10793** assignment that collided with avatar-mcp backend.

## Registry

Registered in `mcp-central-docs/operations/fleet-registry.json`:

```json
{
  "id": "agy-fleet-mcp",
  "port": 10825,
  "category": "Command",
  "status": "beta"
}
```

`agy_fleet_registry` tool reads this catalog from MCP.

## fleet-agent bridge (optional)

```json
"agy-fleet": {
  "url": "http://127.0.0.1:10825/mcp",
  "description": "agy-fleet-mcp — Antigravity MCP config sync/diff/validate",
  "category": "orchestration",
  "key_tools": ["agy_fleet_sync", "agy_fleet_diff", "agy_fleet_validate"]
}
```

## Related fleet repos

| Repo | Relationship |
|------|--------------|
| notebooklm-fleet-mcp | Sync into Cursor via this tool; separate NotebookLM wrapper |
| arxiv-mcp | Typical priority entry in tool budget |
| calibre-mcp | Typical priority entry in tool budget |
| mcp-central-docs | Source of `fleet-registry.json` |

## NotebookLM note

For NotebookLM use **[notebooklm-fleet-mcp](https://github.com/sandraschi/notebooklm-fleet-mcp)** or upstream **notebooklm-mcp-cli** — not agy-fleet-mcp.
