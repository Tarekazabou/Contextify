# Contextify Installation Script for Windows PowerShell
# Run with: .\install.ps1

$ErrorActionPreference = "Stop"

# Dot-source animation functions
. "$PSScriptRoot\contextify-animation.ps1"

function Write-Info($msg)    { Write-Host "[INFO] $msg" -ForegroundColor Cyan }
function Write-Success($msg) { Write-Host "[OK]   $msg" -ForegroundColor Green }
function Write-Warn($msg)    { Write-Host "[WARN] $msg" -ForegroundColor Yellow }
function Write-ErrorMsg($msg){ Write-Host "[ERR]  $msg" -ForegroundColor Red }

Write-Host ""
Write-Host "Installing Contextify - The Context Bridge for AI Coders" -ForegroundColor Cyan
Write-Host ""

# Detect Python
$pythonCmd = $null
foreach ($cmd in @("python", "python3")) {
    if (Get-Command $cmd -ErrorAction SilentlyContinue) {
        $pythonCmd = $cmd
        break
    }
}

if (-not $pythonCmd) {
    Write-ErrorMsg "Python 3 not found."
    Write-Warn "Install from https://www.python.org/downloads/"
    exit 1
}

$pyVersion = & $pythonCmd -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
Write-Success "Python found: $pythonCmd (v$pyVersion)"

# Install dependencies
Write-Info "Installing Python dependencies..."
Show-Spinner "Installing dependencies" 1500
& $pythonCmd -m pip install --upgrade pip --user
& $pythonCmd -m pip install google-generativeai pyperclip pathspec python-dotenv requests keyring colorama --user

Write-Success "Dependencies installed"

# Script directory
$scriptDir = if ($PSScriptRoot) { $PSScriptRoot } else { (Get-Location).Path }

# Create batch launcher
$batchPath = Join-Path $scriptDir "contextify.bat"

Show-Spinner "Setting up CLI launcher" 600

@"
@echo off
python -m contextify.main %*
"@ | Out-File -Encoding ASCII $batchPath

Write-Success "contextify.bat created"

# Interactive provider setup
Write-Host ""
Write-Info "Setting up AI provider (interactive wizard)..."
Write-Host ""

$scriptDir = if ($PSScriptRoot) { $PSScriptRoot } else { (Get-Location).Path }
$projectRoot = Split-Path $scriptDir -Parent

# Add project root to PYTHONPATH for module discovery
$env:PYTHONPATH = $projectRoot
& $pythonCmd -m contextify.main onboard

Write-Host ""
Write-Success "Installation complete"

Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Run: .\scripts\contextify.bat ""your request here"""
Write-Host "  2. For more options: .\scripts\contextify.bat --help"
Write-Host "  3. To reconfigure provider: .\scripts\contextify.bat onboard"
Write-Host ""
Write-Host "Examples:" -ForegroundColor Cyan
Write-Host "  .\scripts\contextify.bat ""add a dark mode toggle"""
Write-Host "  .\scripts\contextify.bat ""fix bug"" --changed"
Write-Host "  .\scripts\contextify.bat ""refactor auth"" --focus backend"
Write-Host ""