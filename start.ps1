Param(
    [switch]$Serve,
    [switch]$Stdio,
    [switch]$Debug
)

Set-Location $PSScriptRoot

if (-not (Test-Path ".\.venv")) {
    & "C:\Users\sandr\.local\bin\uv.exe" sync
}

$args = @("run", "python", "-m", "agy_fleet_mcp")
if ($Serve) { $args += "--serve" }
if ($Stdio) { $args += "--stdio" }
if ($Debug) { $args += "--debug" }
if (-not $Serve -and -not $Stdio) { $args += "--serve" }

& "C:\Users\sandr\.local\bin\uv.exe" @args
