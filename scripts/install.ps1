# Contextify Installation Script for Windows PowerShell
# Run this with: .\install.ps1

Write-Host "🚀 Installing Contextify - The Context Bridge for AI Coders" -ForegroundColor Cyan
Write-Host ""

# Check for Python
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    if (-not (Get-Command python3 -ErrorAction SilentlyContinue)) {
        Write-Host "❌ Python 3 is required but not installed." -ForegroundColor Red
        Write-Host "Please install Python 3 from https://www.python.org/downloads/" -ForegroundColor Yellow
        Write-Host "Make sure to check 'Add Python to PATH' during installation!" -ForegroundColor Yellow
        exit 1
    }
    $pythonCmd = "python3"
} else {
    $pythonCmd = "python"
}

Write-Host "✅ Python found: $pythonCmd" -ForegroundColor Green

# Install dependencies
Write-Host ""
Write-Host "📦 Installing Python dependencies..." -ForegroundColor Cyan
& $pythonCmd -m pip install google-generativeai pyperclip pathspec --user

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to install dependencies" -ForegroundColor Red
    exit 1
}

# Get the current directory (scripts directory)
$scriptDir = $PSScriptRoot
if (-not $scriptDir) { $scriptDir = Get-Location }

# Create a batch file wrapper for easy execution
$batchContent = @"
@echo off
python "$scriptDir\..\contextify.py" %*
"@

$batchPath = "$scriptDir\contextify.bat"
Set-Content -Path $batchPath -Value $batchContent

Write-Host ""
Write-Host "✅ Installation complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📝 Next steps:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Get your Gemini API key from: https://makersuite.google.com/app/apikey" -ForegroundColor White
Write-Host ""
Write-Host "2. Set the environment variable (choose ONE option):" -ForegroundColor White
Write-Host ""
Write-Host "   Option A - Set for current session:" -ForegroundColor Yellow
Write-Host "   `$env:GEMINI_API_KEY='your-api-key-here'" -ForegroundColor Gray
Write-Host ""
Write-Host "   Option B - Set permanently (run PowerShell as Administrator):" -ForegroundColor Yellow
Write-Host "   [System.Environment]::SetEnvironmentVariable('GEMINI_API_KEY', 'your-api-key-here', 'User')" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Add to PATH (optional, for system-wide access):" -ForegroundColor White
Write-Host "   a. Open System Properties > Environment Variables" -ForegroundColor Gray
Write-Host "   b. Edit 'Path' under User Variables" -ForegroundColor Gray
Write-Host "   c. Add: $scriptDir\.." -ForegroundColor Gray
Write-Host ""
Write-Host "🎉 Usage:" -ForegroundColor Cyan
Write-Host ""
Write-Host "   From this directory:" -ForegroundColor White
Write-Host "   .\scripts\contextify.bat 'add a dark mode toggle'" -ForegroundColor Gray
Write-Host "   .\scripts\contextify.bat 'create a user profile card' --focus frontend" -ForegroundColor Gray
Write-Host "   .\scripts\contextify.bat 'fix the bug' --changed" -ForegroundColor Gray
Write-Host ""
Write-Host "For help: .\scripts\contextify.bat --help" -ForegroundColor White
Write-Host ""
Write-Host "💡 Quick API Key Setup:" -ForegroundColor Cyan
Write-Host "   `$env:GEMINI_API_KEY='your-key'; .\scripts\contextify.bat 'your request'" -ForegroundColor Gray
