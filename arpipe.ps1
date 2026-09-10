<#
  arpipe.ps1 - run the arpipe CLI without the cd / PYTHONPATH dance.

  Stopgap until P19 makes the package runnable from anywhere. It changes
  nothing about the pipeline: it just cd's into arpipe/, puts the parent on
  PYTHONPATH, and calls the venv python. Same as doing it by hand.

  Usage (from arpipe-0.1.0/):
    .\arpipe.ps1 triage  --root live_store
    .\arpipe.ps1 extract --root live_store --out live_dataset --companies companies.csv
    .\arpipe.ps1 audit   --out live_dataset
    .\arpipe.ps1 -h
#>
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path   # arpipe-0.1.0/
$pkg  = Join-Path $root "arpipe"                          # arpipe-0.1.0/arpipe/
$py   = Join-Path $pkg  ".venv\Scripts\python.exe"

if (-not (Test-Path $py))  { throw "venv python not found: $py" }
if (-not (Test-Path $pkg)) { throw "package dir not found: $pkg" }

$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User") + ";" + $env:Path
$env:PYTHONPATH = $root
Push-Location $pkg
try {
    & $py -m arpipe.cli @args
    exit $LASTEXITCODE
} finally {
    Pop-Location
}
