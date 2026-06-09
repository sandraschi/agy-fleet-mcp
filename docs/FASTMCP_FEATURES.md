# FastMCP features — agy-fleet-mcp

## Server identity

```python
mcp = FastMCP("agy-fleet-mcp", instructions="...")
```

Instructions emphasize config sync and agy-mcp distinction.

## Transports

| Mode | Command |
|------|---------|
| stdio (default) | `python -m agy_fleet_mcp --stdio` |
| HTTP | `python -m agy_fleet_mcp --serve` |

HTTP app (`app.py`) mounts `mcp.http_app(path="/mcp")` with startup probes.

## Skills provider

```python
SkillsDirectoryProvider(roots=[skills/])
```

Exposes **`skill://agy-fleet`**.

## Tool patterns

- Sync tools default `dry_run=True`
- Location IDs as `Literal` enums for schema clarity
- Structured dict responses (never raw JSON strings)

## No dashboard

Unlike notebooklm-fleet-mcp or arxiv-mcp, this repo is **MCP-only** — no `web_sota/`. HTTP surface is `/health` + `/mcp` only.

## MCPB

`manifest.json` v0.2 — stdio via `uv run python -m agy_fleet_mcp --stdio`.

Pack: `just mcpb-pack`.
