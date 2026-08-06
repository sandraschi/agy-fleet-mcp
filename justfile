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


# Bootstrap: install dev deps + pre-commit hook
bootstrap:
    uv sync --group dev
    uv run pre-commit install
    Write-Host "Pre-commit hooks installed." -ForegroundColor Green