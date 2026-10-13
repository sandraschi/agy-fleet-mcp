set windows-shell := ["powershell.exe", "-NoProfile", "-Command"]
import 'scripts/just/fleet.just'

default:
    @just --list

lint:
    uv run ruff check src/ tests/

test:
    uv run pytest

serve:
    .\start.ps1 -Serve

stdio:
    uv run python -m agy_fleet_mcp --stdio

install-mcp CLIENT:
    .\install-mcp.ps1 {{CLIENT}}

