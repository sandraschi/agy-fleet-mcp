# Install this MCP server into a client config.
# Usage: .\install-mcp.ps1 claude|cursor|windsurf|zed|antigravity|gemini|lmstudio|code|print
param([string]$Client = "print")

$RepoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$ManifestPath = Join-Path $RepoRoot "manifest.json"

if (-not (Test-Path $ManifestPath)) {
    Write-Host "ERROR: manifest.json not found at $ManifestPath" -ForegroundColor Red
    exit 1
}

$mf = Get-Content $ManifestPath -Raw | ConvertFrom-Json
$Name = $mf.name
$Cmd = $mf.server.mcp_config.command
$Args = $mf.server.mcp_config.args

$Entry = @{
    command = "C:\Users\sandr\.local\bin\uv.exe"
    args = @("--directory", $RepoRoot) + $Args
}

if ($mf.server.mcp_config.env.PSObject.Properties.Name) {
    $envTable = @{}
    $mf.server.mcp_config.env.PSObject.Properties | ForEach-Object {
        $envTable[$_.Name] = $_.Value
    }
    $Entry["env"] = $envTable
}

$Block = @{ mcpServers = @{ $Name = $Entry } }
$Json = $Block | ConvertTo-Json -Depth 4

$Paths = @{
    claude      = @{ Path = "$env:APPDATA\Claude\claude_desktop_config.json"; Key = "mcpServers" }
    cursor      = @{ Path = "$env:USERPROFILE\.cursor\mcp.json"; Key = "mcpServers" }
    windsurf    = @{ Path = "$env:USERPROFILE\.codeium\windsurf\mcp_config.json"; Key = "mcpServers" }
    zed         = @{ Path = "$env:APPDATA\Zed\settings.json"; Key = "mcpServers" }
    antigravity = @{ Path = "$env:USERPROFILE\.gemini\antigravity\mcp_config.json"; Key = "mcpServers" }
    gemini      = @{ Path = "$env:USERPROFILE\.gemini\config\mcp_config.json"; Key = "mcpServers" }
    lmstudio    = @{ Path = "$env:USERPROFILE\.lmstudio\mcp.json"; Key = "mcpServers" }
    code        = @{ Path = "$RepoRoot\.vscode\settings.json"; Key = "mcp" }
}

switch -Wildcard ($Client) {
    "print" {
        Write-Host $Json -ForegroundColor Cyan
        Write-Host "`nCopy this into your MCP client config." -ForegroundColor Gray
    }
    default {
        $c = $Paths[$Client]
        if (-not $c) {
            Write-Host "Unknown client '$Client'. Use: claude, cursor, windsurf, zed, antigravity, gemini, lmstudio, code, print" -ForegroundColor Red
            exit 1
        }
        $cfgDir = Split-Path -Parent $c.Path
        if (-not (Test-Path $cfgDir)) { New-Item -ItemType Directory -Path $cfgDir -Force | Out-Null }
        $existing = @{}
        if (Test-Path $c.Path) { $existing = Get-Content $c.Path -Raw | ConvertFrom-Json -AsHashtable }
        $key = $c.Key
        if (-not $existing.ContainsKey($key)) { $existing[$key] = @{} }
        $existing[$key][$Name] = $Entry
        $existing | ConvertTo-Json -Depth 10 | Set-Content $c.Path
        Write-Host "Installed $Name into $($c.Path)" -ForegroundColor Green
    }
}
