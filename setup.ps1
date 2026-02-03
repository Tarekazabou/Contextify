# Quick Setup for Contextify on Windows
# Save this as: setup.ps1
# Run: .\setup.ps1

Write-Host @"
╔════════════════════════════════════════════════════════════╗
║                    CONTEXTIFY SETUP                        ║
║          The Context Bridge for AI Coders                  ║
╚════════════════════════════════════════════════════════════╝
"@ -ForegroundColor Cyan

# Step 1: Check Python
Write-Host "`n[1/4] Checking Python..." -ForegroundColor Yellow
$python = $null
if (Get-Command python -ErrorAction SilentlyContinue) {
    $python = "python"
} elseif (Get-Command python3 -ErrorAction SilentlyContinue) {
    $python = "python3"
} else {
    Write-Host "❌ Python not found!" -ForegroundColor Red
    Write-Host "Install from: https://www.python.org/downloads/" -ForegroundColor White
    Write-Host "Check 'Add Python to PATH' during installation!" -ForegroundColor Yellow
    exit 1
}
Write-Host "   ✅ Found: $python" -ForegroundColor Green

# Step 2: Install packages
Write-Host "`n[2/4] Installing packages..." -ForegroundColor Yellow
& $python -m pip install --quiet google-generativeai pyperclip pathspec --user
if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✅ Packages installed" -ForegroundColor Green
} else {
    Write-Host "   ⚠️  Some packages may have failed, but continuing..." -ForegroundColor Yellow
}

# Step 3: Create launcher
Write-Host "`n[3/4] Creating launcher..." -ForegroundColor Yellow
$scriptDir = $PSScriptRoot
if (-not $scriptDir) { $scriptDir = Get-Location }

@"
@echo off
python "%~dp0contextify.py" %*
"@ | Out-File -FilePath "$scriptDir\contextify.bat" -Encoding ASCII

Write-Host "   ✅ Created contextify.bat" -ForegroundColor Green

# Step 4: Check API key
Write-Host "`n[4/4] Checking API key..." -ForegroundColor Yellow
if ($env:GEMINI_API_KEY) {
    Write-Host "   ✅ API key is set!" -ForegroundColor Green
} else {
    Write-Host "   ⚠️  API key not set" -ForegroundColor Yellow
    Write-Host "`n   To set it now, run:" -ForegroundColor White
    Write-Host "   `$env:GEMINI_API_KEY='your-api-key-here'" -ForegroundColor Cyan
    Write-Host "`n   Get your key from: https://makersuite.google.com/app/apikey" -ForegroundColor White
}

# Done!
Write-Host @"

╔════════════════════════════════════════════════════════════╗
║                   ✅ SETUP COMPLETE!                       ║
╚════════════════════════════════════════════════════════════╝

📝 QUICK START:
"@ -ForegroundColor Green

Write-Host "1. Set your API key (if not already set):" -ForegroundColor White
Write-Host "   `$env:GEMINI_API_KEY='your-key-here'" -ForegroundColor Cyan

Write-Host "`n2. Use Contextify:" -ForegroundColor White
Write-Host "   .\contextify.bat 'add a dark mode toggle'" -ForegroundColor Cyan
Write-Host "   .\contextify.bat 'create user card' --focus frontend" -ForegroundColor Cyan
Write-Host "   .\contextify.bat 'fix bug' --changed" -ForegroundColor Cyan

Write-Host "`n💡 PRO TIP - Create an alias:" -ForegroundColor Yellow
Write-Host @"
   function ctx { .\contextify.bat `$args }
   
   Then use: ctx 'your request'
"@ -ForegroundColor Gray

Write-Host "`n🔗 More help: .\contextify.bat --help" -ForegroundColor White
Write-Host ""
