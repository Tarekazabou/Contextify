# Contextify Setup Guide

This guide walks you through installing and configuring Contextify on your system.

## Prerequisites

- **Python 3.9 or later** installed on your system
- **An AI provider account** with an API key (see [Configuration](#configuration) section)
- **Git** (optional, but recommended for using the `--changed` flag)

## Quick Start Installation

### Windows

```powershell
# Navigate to the Contextify directory
cd "C:\Path\To\Contextify"

# Run the setup script
.\scripts\setup.ps1

# Verify installation
contextify --help
```

### Linux/macOS

```bash
# Navigate to the Contextify directory
cd /path/to/contextify

# Make script executable and run
chmod +x scripts/install.sh
./scripts/install.sh

# Verify installation
contextify --help
```

## Configuration

Contextify requires an AI provider API key. You have two setup options:

### Option 1: Interactive Setup (Recommended)

The interactive onboarding wizard guides you through provider selection, authentication, and model configuration:

```bash
contextify onboard
```

This will:
1. Let you choose an AI provider (GitHub Copilot, Google Gemini, OpenAI, Anthropic, or Local Proxy)
2. Authenticate securely with your chosen provider
3. Select your default AI model
4. Save credentials securely to your system

**Security**: Credentials are stored using your OS's secure credential storage:
- **Windows**: Credential Manager (encrypted by Windows)
- **macOS**: Keychain (encrypted by macOS)
- **Linux**: libsecret (encrypted by your system)

### Option 2: Environment Variables (Quick Setup)

For quick testing or automation, set environment variables:

**Google Gemini:**
```bash
export GEMINI_API_KEY='your-api-key-here'         # Linux/macOS
set GEMINI_API_KEY=your-api-key-here              # Windows (Command Prompt)
$env:GEMINI_API_KEY='your-api-key-here'           # Windows (PowerShell)
```

**GitHub Copilot:**
```bash
export GITHUB_TOKEN='your-github-token'           # Linux/macOS
set GITHUB_TOKEN=your-github-token                # Windows (Command Prompt)
$env:GITHUB_TOKEN='your-github-token'             # Windows (PowerShell)
```

## Credential Storage Details

### How Credentials Are Stored

Contextify uses a **secure-by-default** approach:

1. **Primary**: OS keyring storage (encrypted)
   - Credentials stored in your system's secure storage
   - Requires no additional setup
   - Recommended for production use

2. **Fallback**: Encrypted file storage
   - Used if keyring is unavailable
   - Credentials stored in configuration directory
   - Still encrypted, but less secure than OS keyring

3. **Environment Variables** (optional)
   - Used if no keyring/file credentials exist
   - Useful for automation and CI/CD
   - Less secure than keyring storage

### Configuration Directories

Contextify uses **XDG Base Directory** specification for storing configuration and credentials:

| OS | Configuration Path | Credentials Path |
|---|---|---|
| **Linux** | `~/.config/contextify/` | OS Keyring / File |
| **macOS** | `~/Library/Application Support/contextify/` | OS Keychain / File |
| **Windows** | `%APPDATA%\contextify\` | Credential Manager / File |

Configuration and credentials are created automatically during `contextify onboard`.

### Secure Credential Practices

- ✅ Use `contextify onboard` for interactive setup
- ✅ Let credentials be stored in OS keyring automatically
- ✅ Never commit API keys to git
- ✅ Don't share your `.env` files
- ❌ Avoid storing credentials in plain text files
- ❌ Don't commit credentials to version control

## Installation Methods

### Method 1: PowerShell Script (Windows - Recommended)

The `setup.ps1` script handles everything:

```powershell
.\scripts\setup.ps1
```

**What it does:**
1. Creates a Python virtual environment
2. Installs all dependencies from `requirements.txt`
3. Creates a batch file for easy command access
4. Adds Contextify to your system PATH

**After setup:**
```powershell
# You can now use contextify from any terminal
contextify --help
```

### Method 2: Bash Script (Linux/macOS)

The `install.sh` script handles the complete setup:

```bash
chmod +x scripts/install.sh
./scripts/install.sh
```

**What it does:**
1. Creates a Python virtual environment
2. Installs all dependencies from `requirements.txt`
3. Creates executable symlink in `/usr/local/bin/`
4. Updates your shell configuration

### Method 3: Manual Installation (All Platforms)

```bash
# 1. Create virtual environment (recommended)
python -m venv venv

# 2. Activate virtual environment
# Linux/macOS:
source venv/bin/activate
# Windows (PowerShell):
venv\Scripts\Activate.ps1
# Windows (Command Prompt):
venv\Scripts\activate.bat

# 3. Install dependencies
pip install -r requirements.txt

# 4. Install Contextify in development mode
pip install -e .

# 5. Verify
contextify --help
```

## Dependencies

Contextify requires the following Python packages (automatically installed):

| Package | Version | Purpose |
|---------|---------|---------|
| google-generativeai | >=0.3.0 | Google Gemini API |
| pyperclip | >=1.8.0 | Clipboard support |
| pathspec | >=0.11.0 | .gitignore pattern matching |
| python-dotenv | >=1.0.0 | .env file loading |
| requests | >=2.28.0 | HTTP requests |
| keyring | >=24.0.0 | Secure credential storage |
| colorama | >=0.4.6 | Terminal colors |

## Verification

Verify your installation with:

```bash
# Check version
contextify --version

# Show help
contextify --help

# Test context gathering (no API call)
contextify "test request" --dry-run
```

## Troubleshooting

### "command not found: contextify" (Windows PowerShell)

The `setup.ps1` script adds Contextify to your PATH. Restart PowerShell or reload your profile:

```powershell
. $PROFILE
```

### "command not found: contextify" (Linux/macOS)

Reload your shell configuration:

```bash
source ~/.bashrc          # for bash
source ~/.zshrc           # for zsh
```

### "GEMINI_API_KEY not found" or "GITHUB_TOKEN not found"

You need to set up a provider. Either:
1. Run `contextify onboard` for interactive setup, or
2. Set the environment variable manually

**Get API keys:**
- Google Gemini: https://aistudio.google.com/app/apikey
- GitHub Copilot: Requires GitHub authentication via `contextify onboard`

### "keyring" import error

The `keyring` package isn't installed. Re-run installation:

```bash
pip install -r requirements.txt
```

Or install keyring directly:

```bash
pip install keyring>=24.0.0
```

**Note**: On Linux, you may need to install `libsecret` first:

```bash
# Debian/Ubuntu
sudo apt-get install libsecret-1-0 libsecret-1-dev

# Fedora
sudo dnf install libsecret libsecret-devel

# Arch
sudo pacman -S libsecret
```

### "Permission denied" on Linux/macOS

Make the install script executable:

```bash
chmod +x scripts/install.sh
./scripts/install.sh
```

### "Module not found" after installation

Your virtual environment may not be activated. Try:

```bash
# Activate virtual environment
source venv/bin/activate    # Linux/macOS
venv\Scripts\activate.bat   # Windows (Command Prompt)
venv\Scripts\Activate.ps1   # Windows (PowerShell)

# Then try again
contextify --help
```

## Next Steps

1. **Set up your provider**: Run `contextify onboard`
2. **Try it out**: `contextify "add a button component"`
3. **Learn the flags**: See [docs/FLAGS.md](FLAGS.md)
4. **See examples**: Check [docs/EXAMPLES.md](EXAMPLES.md)
5. **Read quick start**: Visit [docs/QUICKSTART.md](QUICKSTART.md)

Happy coding! 🚀
