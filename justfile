set windows-shell := ["powershell.exe", "-NoProfile", "-Command"]

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

# Pack Claude Desktop bundle (creates dist/agy-fleet-mcp-v{version}.mcpb)
mcpb-pack:
    cd '{{justfile_directory()}}'
    $ver = (Get-Content pyproject.toml | Select-String '^version = "(.*)"' | ForEach-Object { $_.Matches.Groups[1].Value })
    $null = New-Item -ItemType Directory -Path dist -Force
    Compress-Archive -Path manifest.json, assets, src, pyproject.toml, README.md, CHANGELOG.md -DestinationPath "dist/agy-fleet-mcp-v$ver.mcpb" -CompressionLevel Optimal -Force
    Write-Host "Created dist/agy-fleet-mcp-v$ver.mcpb" -ForegroundColor Green
