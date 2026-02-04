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
python -m contextify.main %*
"@ | Out-File -Encoding ASCII "$scriptDir\contextify.bat"

Write-Host "contextify.bat created" -ForegroundColor Green

# Step 4: Provider Setup
Write-Host ""
Write-Host "[4/4] Provider setup (interactive wizard)..." -ForegroundColor Yellow

$projectRoot = Split-Path $PSScriptRoot -Parent
$env:PYTHONPATH = $projectRoot
& .\.venv\Scripts\python -m contextify.main onboard

Write-Host ""
Write-Host "SETUP COMPLETE" -ForegroundColor Green
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Run: .\scripts\contextify.bat ""your request here"""
Write-Host "  2. For help: .\scripts\contextify.bat --help"
Write-Host "  3. To reconfigure: .\scripts\contextify.bat onboard"
Write-Host ""
Write-Host "Examples:" -ForegroundColor Cyan
Write-Host "  .\scripts\contextify.bat ""add a dark mode toggle""" -ForegroundColor Cyan
Write-Host "  .\scripts\contextify.bat ""generate unit tests for this function""" -ForegroundColor Cyan
Write-Host "  .\scripts\contextify.bat ""refactor this code to use async/await""" -ForegroundColor Cyan
Write-Host "  .\scripts\contextify.bat ""fix bug"" --changed" -ForegroundColor Cyan
Write-Host "  .\scripts\contextify.bat ""improve performance of algorithm"" --focus backend" -ForegroundColor Cyan