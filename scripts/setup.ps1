# Quick Setup for Contextify on Windows
# Run with: .\setup.ps1

# Dot-source animation functions
. "$PSScriptRoot\contextify-animation.ps1"

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "           CONTEXTIFY QUICK SETUP            " -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan

# Step 1: Python
Write-Host ""
Write-Host "[1/4] Checking Python..." -ForegroundColor Yellow

$python = $null
foreach ($cmd in @("python", "python3")) {
    if (Get-Command $cmd -ErrorAction SilentlyContinue) {
        $python = $cmd
        break
    }
}

if (-not $python) {
    Write-Host "Python not found" -ForegroundColor Red
    exit 1
}

Write-Host "Found Python: $python" -ForegroundColor Green

Show-Spinner "Creating virtual environment" 1000
& $python -m venv .venv

Show-Spinner "Installing dependencies" 1500
& .\.venv\Scripts\pip install -r "$PSScriptRoot\..\requirements.txt"

Show-Spinner "Setting up CLI launcher" 600

# Step 2: Packages
Write-Host ""
Write-Host "[2/4] Installing packages..." -ForegroundColor Yellow
Write-Host "Packages installed (venv)" -ForegroundColor Green

# Step 3: Launcher
Write-Host ""
Write-Host "[3/4] Creating launcher..." -ForegroundColor Yellow

$scriptDir = if ($PSScriptRoot) { $PSScriptRoot } else { (Get-Location).Path }

@"
@echo off
python "%~dp0..\contextify.py" %*
"@ | Out-File -Encoding ASCII "$scriptDir\contextify.bat"

Write-Host "contextify.bat created" -ForegroundColor Green

# Step 4: API key
Write-Host ""
Write-Host "[4/4] API key..." -ForegroundColor Yellow

if (-not $env:GEMINI_API_KEY) {
    $key = Read-Host "Enter GEMINI_API_KEY (optional)"
    if ($key) {
        $env:GEMINI_API_KEY = $key
        [System.Environment]::SetEnvironmentVariable("GEMINI_API_KEY", $key, "User")
        Write-Host "API key saved" -ForegroundColor Green
    }
} else {
    Write-Host "API key already set" -ForegroundColor Green
}

Write-Host ""
Write-Host "SETUP COMPLETE" -ForegroundColor Green
Write-Host "Run: .\scripts\contextify.bat --help"
Write-Host ""
Write-Host "Examples:" -ForegroundColor Cyan
Write-Host "  .\scripts\contextify.bat ""explain this code""" -ForegroundColor Cyan
Write-Host "  .\scripts\contextify.bat ""generate unit tests for this       function""" -ForegroundColor Cyan
Write-Host "  .\scripts\contextify.bat ""refactor this code to use async/await""" -ForegroundColor Cyan
Write-Host "  .\scripts\contextify.bat ""improve performance of this algorithm""" -ForegroundColor Cyan
Write-Host "  .\scripts\contextify.bat ""write documentation for this module""" -ForegroundColor Cyan
Write-Host "  .\scripts\contextify.bat ""summarize the changes made in this commit""" -ForegroundColor Cyan
Write-Host "  .\scripts\contextify.bat ""generate a README.md for this project""" -ForegroundColor Cyan
Write-Host "  .\scripts\contextify.bat ""generate code to interact with this API""" -ForegroundColor Cyan
Write-Host "  .\scripts\contextify.bat ""find bugs in this code""" -ForegroundColor Cyan