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
& $pythonCmd -m pip install google-generativeai pyperclip pathspec --user

Write-Success "Dependencies installed"

# Script directory
$scriptDir = if ($PSScriptRoot) { $PSScriptRoot } else { (Get-Location).Path }

# Create batch launcher
$batchPath = Join-Path $scriptDir "contextify.bat"

Show-Spinner "Setting up CLI launcher" 600

@"
@echo off
python "%~dp0..\contextify.py" %*
"@ | Out-File -Encoding ASCII $batchPath

Write-Success "contextify.bat created"

# API key
Write-Host ""
$apiKeyInput = Read-Host "Enter GEMINI_API_KEY (leave blank to skip)"
if ($apiKeyInput) {
    $env:GEMINI_API_KEY = $apiKeyInput
    [System.Environment]::SetEnvironmentVariable("GEMINI_API_KEY", $apiKeyInput, "User")
    Write-Success "GEMINI_API_KEY saved"
} else {
    Write-Warn "API key not set"
}

Write-Host ""
Write-Success "Installation complete"

Write-Host ""
Write-Host "Usage:"
Write-Host "  .\scripts\contextify.bat ""add a dark mode toggle"""
Write-Host "  .\scripts\contextify.bat ""fix bug"" --changed"
Write-Host ""
Write-Host "Make sure to restart your terminal to apply environment variable changes." -ForegroundColor Yellow