# Contextify for Windows - Installation Guide

## 🪟 Quick Installation (PowerShell)

### Method 1: Automatic Setup (Recommended)

1. **Open PowerShell** in the Contextify folder
   - Right-click folder → "Open in Windows Terminal" or "Open PowerShell window here"

2. **Run the setup script**:
   ```powershell
   .\scripts\setup.ps1
   ```

3. **Set your API key** (get free key from https://makersuite.google.com/app/apikey):
   ```powershell
   $env:GEMINI_API_KEY='your-api-key-here'
   ```

4. **Use it!**
   ```powershell
   .\scripts\contextify.bat 'add a dark mode toggle'
   ```

### Method 2: Manual Installation

1. **Install Python** (if not already installed)
   - Download from: https://www.python.org/downloads/
   - ✅ **Important**: Check "Add Python to PATH" during installation!

2. **Install dependencies**:
   ```powershell
   python -m pip install google-generativeai pyperclip pathspec --user
   ```

3. **Set API key**:
   ```powershell
   $env:GEMINI_API_KEY='your-api-key-here'
   ```

4. **Run Contextify**:
   ```powershell
   python contextify.py "your request"
   ```

## 🚀 Usage

### Basic Commands

```powershell
# From the Contextify directory:
.\scripts\contextify.bat 'add a dark mode toggle'
.\scripts\contextify.bat 'create a user profile card' --focus frontend
.\scripts\contextify.bat 'fix the login bug' --changed
.\scripts\contextify.bat 'add API endpoint' --focus backend
```

### With PowerShell Alias (Easier!)

Add this to your PowerShell profile for quick access:

```powershell
# Find your profile location
$PROFILE

# Edit it (creates if doesn't exist)
notepad $PROFILE

# Add this line:
function ctx { & "C:\path\to\contextify\scripts\contextify.bat" $args }

# Save and reload
. $PROFILE

# Now you can use:
ctx 'your request'
```

## 🔑 Setting API Key Permanently

### Option 1: User Environment Variable (Recommended)

```powershell
# Run PowerShell as Administrator, then:
[System.Environment]::SetEnvironmentVariable('GEMINI_API_KEY', 'your-api-key-here', 'User')
```

### Option 2: System Environment Variable (All Users)

1. Press `Win + X` → System
2. Click "Advanced system settings"
3. Click "Environment Variables"
4. Under "User variables" click "New"
5. Variable name: `GEMINI_API_KEY`
6. Variable value: `your-api-key-here`
7. Click OK

### Option 3: PowerShell Profile (Session-based)

```powershell
# Edit your profile
notepad $PROFILE

# Add this line:
$env:GEMINI_API_KEY='your-api-key-here'

# Save and reload
. $PROFILE
```

## 📁 Adding to PATH (Optional)

To use `contextify` from anywhere:

1. Copy the full path to your Contextify folder:
   ```powershell
   Get-Location | Select-Object -ExpandProperty Path
   ```

2. Add to PATH:
   - Press `Win + X` → System
   - Click "Advanced system settings"
   - Click "Environment Variables"
   - Under "User variables", select "Path" → Edit
   - Click "New"
   - Paste the Contextify folder path
   - Click OK on all dialogs

3. **Restart PowerShell/Terminal**

4. Now you can use from anywhere:
   ```powershell
   cd C:\your\project
   contextify 'add feature'
   ```

## 💡 PowerShell Tips

### Create Multiple Aliases

```powershell
# Add to your $PROFILE:
function ctx { & "C:\path\to\contextify\scripts\contextify.bat" $args }
function ctxf { & "C:\path\to\contextify\scripts\contextify.bat" $args --focus frontend }
function ctxb { & "C:\path\to\contextify\scripts\contextify.bat" $args --focus backend }
function ctxc { & "C:\path\to\contextify\scripts\contextify.bat" $args --changed }

# Usage:
ctx 'add feature'
ctxf 'create component'
ctxb 'add API route'
ctxc 'fix bug'
```

### One-liner with API Key

```powershell
$env:GEMINI_API_KEY='your-key'; .\scripts\contextify.bat 'your request'
```

### Save Output to File

```powershell
.\scripts\contextify.bat 'major refactor' --output prompt.md
```

## 🐛 Troubleshooting

### "Python is not recognized..."

**Solution**: Reinstall Python and check "Add Python to PATH"
- Or add manually: `C:\Users\YourName\AppData\Local\Programs\Python\Python3xx`

### "Access Denied" when installing packages

**Solution 1**: Use `--user` flag:
```powershell
python -m pip install google-generativeai pyperclip pathspec --user
```

**Solution 2**: Run PowerShell as Administrator

### "Cannot be loaded because running scripts is disabled"

**Solution**: Enable script execution:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### "GEMINI_API_KEY not set"

**Solution**: Set it in current session:
```powershell
$env:GEMINI_API_KEY='your-key-here'
```

Or set it permanently (see above).

### Clipboard not working

**Solution**: Install pyperclip properly:
```powershell
python -m pip install pyperclip --force-reinstall --user
```

If still not working, use file output:
```powershell
.\scripts\contextify.bat 'request' --output prompt.txt
```

## 📝 Example Workflow

```powershell
# Navigate to your project
cd C:\projects\my-app

# Set API key (if not set globally)
$env:GEMINI_API_KEY='your-key'

# Generate prompt
.\scripts\contextify.bat 'add dark mode to navbar' --focus frontend

# The prompt is now in your clipboard!
# Paste into GitHub Copilot, ChatGPT, or Cursor

# Or save to file
.\scripts\contextify.bat 'add dark mode' --output dark-mode-prompt.md
```

## 🎯 Common Use Cases

### Frontend Development
```powershell
.\scripts\contextify.bat 'create UserCard component' --focus frontend
.\scripts\contextify.bat 'add form validation' --focus frontend
.\scripts\contextify.bat 'style the dashboard' --focus frontend
```

### Backend Development
```powershell
.\scripts\contextify.bat 'add POST /api/users endpoint' --focus backend
.\scripts\contextify.bat 'add authentication middleware' --focus backend
.\scripts\contextify.bat 'implement rate limiting' --focus backend
```

### Bug Fixes
```powershell
# After making changes
.\scripts\contextify.bat 'fix the TypeError in form submission' --changed
```

### Database Work
```powershell
.\scripts\contextify.bat 'add posts table migration' --focus database
.\scripts\contextify.bat 'add user relationships' --focus database
```

## 🔗 Integration with VS Code

### Create a VS Code Task

1. Create `.vscode/tasks.json` in your project:

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Contextify",
      "type": "shell",
      "command": "C:\\path\\to\\contextify\\scripts\\contextify.bat",
      "args": ["${input:request}"],
      "problemMatcher": []
    }
  ],
  "inputs": [
    {
      "id": "request",
      "type": "promptString",
      "description": "What would you like to build?"
    }
  ]
}
```

2. Run with: `Ctrl+Shift+P` → "Tasks: Run Task" → "Contextify"

## 🎓 Next Steps

1. ✅ Run `.\scripts\setup.ps1` to install
2. ✅ Set `$env:GEMINI_API_KEY`
3. ✅ Try: `.\scripts\contextify.bat 'your first request'`
4. 📚 Read `docs/QUICKSTART.md` for more examples
5. 💡 Create aliases in your PowerShell profile
6. ⭐ Star the repo if it helps!

## 📞 Need Help?

```powershell
# View all options
.\scripts\contextify.bat --help

# Check examples
Get-Content docs/EXAMPLES.md

# Read full docs
Get-Content README.md
```

---

**Happy coding on Windows!** 🪟✨
