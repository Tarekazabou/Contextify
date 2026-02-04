# Contextify Onboarding Guide

Welcome to Contextify! This guide will help you set up your preferred AI provider.

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Setup Wizard
```bash
contextify onboard
```

### 3. Follow the Interactive Prompts
The wizard will guide you through:
- Choosing your preferred provider (GitHub Copilot, Google Gemini, etc.)
- Authenticating with that provider
- Selecting your default model
- Testing the connection

### 4. Start Using Contextify
```bash
contextify "add a dark mode toggle"
contextify "create auth component" --focus frontend
contextify "fix the bug" --target src/Bug.tsx
```

That's it! No more environment variables or flags needed.

---

## Detailed Walkthrough

### Step 1: Welcome
```
======================================================================
  CONTEXTIFY ONBOARDING WIZARD
======================================================================

Welcome! Let's set up your AI provider and model.

📋 Current Configuration:
   (No config found - starting fresh setup)

📦 Step 1: Select Provider
----------------------------------------------------------------------

Which provider would you like to use?
  > [1] GitHub Copilot
    [2] Google Gemini
    [3] OpenAI
    [4] Anthropic Claude
    [5] Local/Proxy Provider

Enter number (or 'c' to cancel): 
```

### Step 2: GitHub Copilot Authentication (Example)
```
✓ Selected: GitHub Copilot
  Use GitHub Copilot models via device-flow authentication

🔐 Step 2: Authentication
----------------------------------------------------------------------

Running GitHub device-flow authentication...
(You'll need to authorize this in your web browser)

[GitHub Copilot Authentication]
============================================================

1. Open: https://github.com/login/device
2. Enter code: ABC1-2345
3. Authorize the application

Waiting for authorization (expires in 900s)...
============================================================

✓ Successfully authenticated with GitHub!
  Profile saved: github-copilot:default
```

### Step 3: Model Discovery
```
🤖 Step 3: Model Selection
----------------------------------------------------------------------

Discovering available models...
✓ Found 3 available models:

Which model would you like to use as default?
  > [1] GPT-4o (Latest)             (gpt-4o)
    [2] GPT-4 Turbo                 (gpt-4-turbo)
    [3] GPT-3.5 Turbo               (gpt-3.5-turbo)

Enter number (or 'c' to cancel): 1

✓ Selected: github-copilot/gpt-4o
```

### Step 4: Connectivity Test
```
🧪 Step 4: Testing Connectivity
----------------------------------------------------------------------
  ✓ Authentication token is configured
```

### Step 5: Configuration Saved
```
💾 Step 5: Saving Configuration
----------------------------------------------------------------------
✓ Config saved to: /home/user/.config/contextify/config.json
```

### Step 6: Summary
```
======================================================================
  ✓ ONBOARDING COMPLETE!
======================================================================

Default Model: github-copilot/gpt-4o
Config Location: /home/user/.config/contextify/config.json
Auth Location: /home/user/.config/contextify/auth.json

You can now run:
  contextify "your request"

To change settings later:
  contextify onboard
```

---

## Provider-Specific Setup

### GitHub Copilot
- **What you'll need**: GitHub account
- **Authentication**: Browser-based (device flow)
- **Model examples**: gpt-4o, gpt-4-turbo, gpt-3.5-turbo
- **Models available**: Depends on your GitHub Copilot subscription
- **Time to setup**: ~2 minutes (includes browser authorization)

```bash
contextify onboard
# Select "GitHub Copilot"
# Authorize in browser
# Select model
# Done!
```

### Google Gemini
- **What you'll need**: API key (free or paid)
- **Get key**: https://makersuite.google.com/app/apikey
- **Authentication**: Paste API key when prompted
- **Model examples**: gemini-2.0-flash, gemini-1.5-pro, gemini-1.5-flash
- **Context window**: Up to 1 million tokens
- **Time to setup**: ~1 minute

```bash
contextify onboard
# Select "Google Gemini"
# Paste API key when prompted
# Select model
# Done!
```

### OpenAI (Optional)
- **What you'll need**: API key
- **Get key**: https://platform.openai.com/api-keys
- **Authentication**: Paste API key when prompted
- **Model examples**: gpt-4, gpt-4-turbo-preview, gpt-3.5-turbo
- **Note**: Requires OpenAI credits/account
- **Time to setup**: ~1 minute

```bash
contextify onboard
# Select "OpenAI"
# Paste API key when prompted
# Select model
# Done!
```

### Anthropic Claude (Optional)
- **What you'll need**: API key
- **Get key**: https://console.anthropic.com/
- **Authentication**: Paste API key when prompted
- **Model examples**: claude-3-opus, claude-3-sonnet, claude-3-haiku
- **Context window**: Up to 200k tokens
- **Time to setup**: ~1 minute

```bash
contextify onboard
# Select "Anthropic Claude"
# Paste API key when prompted
# Select model
# Done!
```

### Local/Proxy Provider
- **What you'll need**: Running LLM endpoint
- **Examples**: vLLM, LM Studio, Ollama, OpenAI-compatible proxy
- **Authentication**: Optional API key
- **Model examples**: Depends on your local setup
- **Time to setup**: ~2 minutes

```bash
contextify onboard
# Select "Local/Proxy Provider"
# Enter endpoint URL (e.g., http://localhost:8000/v1)
# Optionally provide API key
# Connectivity test runs
# Done!
```

---

## Configuration Files

After onboarding, these files will be created:

### Config File
**Location**: `~/.config/contextify/config.json`  
**Contains**: 
- Default model selection
- Provider settings
- Safe to commit (no secrets)

Example:
```json
{
  "agents": {
    "defaults": {
      "model": {
        "primary": "github-copilot/gpt-4o",
        "fallbacks": []
      }
    }
  },
  "models": {
    "mode": "merge",
    "providers": {
      "github-copilot": {
        "type": "github-copilot"
      }
    }
  }
}
```

### Auth Index
**Location**: `~/.config/contextify/auth.json`  
**Contains**: Auth profile metadata (not secrets!)
- DO NOT commit to git
- Tokens/keys stored in OS keyring automatically

Example:
```json
{
  "profiles": {
    "github-copilot:default": {
      "provider": "github-copilot",
      "type": "device-token",
      "createdAt": "2026-02-04T12:00:00Z",
      "keyringEntry": "contextify-github-copilot-default"
    }
  }
}
```

### Secrets Storage
- **Primary**: OS Keyring (automatic)
  - macOS: Keychain
  - Windows: Credential Manager  
  - Linux: libsecret
  - User never sees token in files

- **Fallback**: Encrypted in auth.json (if keyring unavailable)
  - Automatic fallback
  - Still protected by file permissions

---

## Troubleshooting

### "No module named 'keyring'"
```bash
pip install keyring>=24.0.0
```

### GitHub Copilot Device Code Expired
- Device codes expire after 15 minutes
- Just run `contextify onboard` again
- Wizard will generate a new code

### "Cannot connect to endpoint"
If using local/proxy provider:
- Verify endpoint is running: `curl http://localhost:8000/v1/models`
- Check port number in your setup
- Verify no firewall blocking connection

### "API key not working"
- Double-check the key (copy-paste carefully)
- Verify the key has required permissions
- Try generating a new key from provider dashboard
- Run `contextify onboard` to update

### "Config file permission denied"
Contextify creates config with `rw-------` permissions (secure).  
If you see permission errors:
```bash
chmod 600 ~/.config/contextify/config.json
chmod 600 ~/.config/contextify/auth.json
```

### Switching Providers
Simply run the wizard again:
```bash
contextify onboard
# Select different provider
# Authenticate with new provider
# Select model
# Config updated!
```

---

## Advanced Usage

### Keep Using Environment Variables
The old method still works! If `GEMINI_API_KEY` is set:
```bash
export GEMINI_API_KEY="sk-..."
contextify "request"  # Uses Gemini even if other provider configured
```

### Force a Specific Provider
```bash
contextify "request" --use-github  # Force GitHub Copilot
```

### Dry Run (Preview Context)
```bash
contextify "request" --dry-run  # See gathered context without calling AI
```

### Custom Temperature
```bash
contextify "request" --temperature 0.3  # More deterministic
contextify "request" --temperature 0.9  # More creative
```

### Focus on Specific Codebase Area
```bash
contextify "request" --focus frontend   # Frontend only
contextify "request" --focus backend    # Backend only
contextify "request" --focus database   # Database only
contextify "request" --focus tests      # Tests only
contextify "request" --focus config     # Configuration only
```

---

## FAQ

**Q: Can I use multiple providers?**  
A: The wizard currently sets one default. We're planning multi-provider support for Phase 2. For now, you can re-run the wizard to switch providers.

**Q: Is my API key secure?**  
A: Yes! Keys are stored in your OS keyring by default (encrypted by OS). If keyring unavailable, they're stored in a file with restricted permissions (0o600).

**Q: What if I lose my API key?**  
A: Contextify only stores what you provide. Visit your provider's dashboard to regenerate keys. Then run `contextify onboard` to update.

**Q: Can I use Contextify offline?**  
A: Once onboarded, you can use Contextify with a local LLM. Select "Local/Proxy Provider" during setup and point to your local endpoint.

**Q: How do I uninstall/reset?**  
A: Delete the config directory:
```bash
rm -rf ~/.config/contextify  # Linux/Mac
rmdir %APPDATA%\.contextify  # Windows
```

**Q: Can I share my config with teammates?**  
A: The config.json is safe to share (no secrets). But secrets (auth.json, tokens) should not be shared. Each user should run their own `contextify onboard`.

---

## What's Next?

After onboarding, you can:

1. **Generate context-aware prompts**:
   ```bash
   contextify "add dark mode support"
   contextify "refactor auth system" --focus backend
   ```

2. **Focus on specific areas**:
   ```bash
   contextify "fix bug" --focus frontend
   contextify "optimize queries" --focus database
   ```

3. **Target specific files**:
   ```bash
   contextify "fix this" --target src/Bug.tsx
   contextify "refactor" --target src/utils/auth.ts
   ```

4. **Use advanced options**:
   ```bash
   contextify "request" --temperature 0.5 --max-files 50
   contextify "request" --dry-run  # Preview context first
   ```

---

## Need Help?

- Check `README.md` for full documentation
- See provider-specific guides (GITHUB_INTEGRATION.md, etc.)
- Error messages include helpful hints
- Run `contextify onboard --help` for command options

---

**You're all set! Happy coding! 🚀**
