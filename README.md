# agy-fleet-mcp

<p align="center">
  <a href="https://github.com/astral-sh/uv"><img src="https://img.shields.io/badge/uv-ready-7c5cfc?style=flat-square" alt="uv"></a>
  <a href="https://github.com/astral-sh/ruff"><img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json" alt="Ruff"></a>
  <a href="https://python.org"><img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python"></a>
  <a href="https://github.com/PrefectHQ/fastmcp"><img src="https://img.shields.io/badge/FastMCP-3.2-7c5cfc?style=flat-square" alt="FastMCP"></a>
</p>

Fleet MCP **config bridge** for **Antigravity CLI** (`agy`) — sync Cursor fleet into Gemini/Antigravity JSON, diff configs, validate commands, and cap the ~50-tool budget.

**Not** [agy-mcp](https://pypi.org/project/agy-mcp/) on PyPI — opposite direction.

**v0.1.0** · FastMCP 3.2 · [CHANGELOG](CHANGELOG.md)

---

## Contents

- [Features](#features)
- [Quick start](#quick-start)
- [What you can do](#what-you-can-do)
- [Port](#port)
- [Documentation](#documentation)
- [Requirements](#requirements)
- [License](#license)

---

## Features

- **Config sync** — Cursor → Gemini / Antigravity / project-local JSON
- **Diff & validate** — preview drift; check commands and `agy` on PATH
- **Tool budget** — disable servers beyond Antigravity's ~50 enabled limit
- **Fleet registry** — read `fleet-registry.json` catalog from MCP
- **Dual transport** — stdio (Cursor) or HTTP MCP on **10825**
- **Safe writes** — `dry_run=true` default; JSON backup on write

---

## Quick start

```powershell
git clone https://github.com/sandraschi/agy-fleet-mcp
cd agy-fleet-mcp
uv sync --extra dev
.\install-mcp.ps1 cursor
```

Stdio:

```powershell
uv run python -m agy_fleet_mcp --stdio
```

HTTP:

```powershell
.\start.ps1 -Serve
```

All install paths: **[INSTALL.md](INSTALL.md)**

---

## What you can do

**Preview sync**

> Diff my Cursor MCP config against Gemini and show what would change.

**Push fleet to Antigravity**

> Merge Cursor servers into `~/.gemini/config/mcp_config.json` (dry-run first).

**Respect tool limits**

> Cap Gemini to 50 enabled servers, prioritizing calibre-mcp and arxiv-mcp.

---

## Port

| Service | Port |
|---------|------|
| HTTP MCP + `/health` | **10825** |

Stdio has no port. (10793 avoided — avatar-mcp backend.)

---

## Documentation

| Doc | Topic |
|-----|-------|
| [INSTALL.md](INSTALL.md) | Options A–D (MCPB, source, Cursor) |
| [PRD.md](PRD.md) | Product requirements |
| [CHANGELOG.md](CHANGELOG.md) | Version history |
| [llms-full.txt](llms-full.txt) | Agent reference |
| [docs/README.md](docs/README.md) | Staged doc index |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Config plane design |
| [docs/TOOLS.md](docs/TOOLS.md) | MCP tool reference |
| [docs/FLEET_INTEGRATION.md](docs/FLEET_INTEGRATION.md) | fleet-agent, registry |
| [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) | Ports, sync safety |

MCD: [mcp-central-docs/projects/agy-fleet-mcp](https://github.com/sandraschi/mcp-central-docs/tree/main/projects/agy-fleet-mcp)

---

## Requirements

- **uv** — Python deps
- **Cursor MCP config** — `~/.cursor/mcp.json` as typical source
- **agy** (optional) — validation only

---

## Related

- [agy-mcp](https://pypi.org/project/agy-mcp/) — agy → MCP tools (opposite)
- [notebooklm-fleet-mcp](https://github.com/sandraschi/notebooklm-fleet-mcp) — NotebookLM fleet wrapper
- [mcp-central-docs](https://github.com/sandraschi/mcp-central-docs) — fleet registry

---

## License

MIT — see [LICENSE](LICENSE)
