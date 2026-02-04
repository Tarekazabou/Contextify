# GitHub Copilot Integration

Contextify now supports **GitHub Copilot** as an alternative to Google Gemini for prompt refinement. This guide explains how to set up and use the GitHub Copilot provider.

## Overview

Two ways to use Contextify with GitHub Copilot:

1. **Device Flow Authentication** (Recommended) - Interactive browser-based login
2. **Pre-configured Token** - Set a GitHub token in `.env` or environment variables

## Setup: Device Flow (Interactive)

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Run with --use-github Flag

On your first run, Contextify will initiate an interactive authentication:

```bash
contextify "your request here" --use-github
```

**What happens:**
1. You'll see a GitHub URL and device code
2. Open the URL in your browser
3. Enter the provided device code
4. Authorize the application
5. Return to your terminal
6. Contextify exchanges the device code for an access token
7. The token is used to call GitHub Copilot's API

### Example Output:
```
[GitHub Copilot Authentication]
============================================================

1. Open: https://github.com/login/device
2. Enter code: ABC1-2345
3. Authorize the application

Waiting for authorization (expires in 900s)...
============================================================

✓ Successfully authenticated with GitHub!
```

## Setup: Pre-configured Token

If you prefer not to do interactive auth each time, you can pre-configure a token.

### Option 1: Environment Variable

```bash
export GITHUB_TOKEN='your-github-token-here'
contextify "your request" --use-github
```

### Option 2: .env File

Create or edit `.env` in your project root or Contextify directory:

```env
GEMINI_API_KEY=your-gemini-key-here  # Still used by default
GITHUB_TOKEN=your-github-token-here  # Used with --use-github flag
```

Then run:
```bash
contextify "your request" --use-github
```

## Getting a GitHub Token

You can use any of these token types:

### Personal Access Token (Easiest)
1. Go to https://github.com/settings/tokens
2. Click "Generate new token" → "Generate new token (classic)"
3. Give it a name (e.g., "Contextify")
4. Select scope: `user:email` (minimal required)
5. Click "Generate token"
6. Copy the token and save it

### GitHub App Token
For programmatic access, create a GitHub App and use an installation token.

## CLI Usage Examples

### Use Gemini (Default)
```bash
contextify "add dark mode feature" --model-name gemini-2.5-flash
```

### Use GitHub Copilot (Device Flow)
```bash
contextify "add dark mode feature" --use-github
```

### Use GitHub Copilot (Pre-configured Token)
```bash
export GITHUB_TOKEN='ghp_...'
contextify "add dark mode feature" --use-github
```

### Combine with Other Flags
```bash
# Focus on frontend with GitHub Copilot
contextify "create auth component" --focus frontend --use-github

# Use skeleton context with GitHub Copilot
contextify "fix the bug" --target src/Bug.tsx --skeleton-context --use-github

# Save output instead of clipboard
contextify "refactor auth" --use-github --output prompt.md
```

## Switching Providers

### Gemini (Default)
```bash
contextify "your request"
# OR explicitly:
contextify "your request"  # No --use-github flag
```

### GitHub Copilot
```bash
contextify "your request" --use-github
```

### Fallback Behavior

The tool tries providers in this order:
1. **If `--use-github` is set:** Use GitHub Copilot (authenticate if needed)
2. **Otherwise:** Use Gemini (default)

If Gemini API key is missing and `--use-github` is not set, you'll get an error.

## Troubleshooting

### "GITHUB_TOKEN environment variable not set"

**Solution:** Run the command with `--use-github` to trigger interactive auth:
```bash
contextify "your request" --use-github
```

Or set the token first:
```bash
export GITHUB_TOKEN='your-token'
contextify "your request" --use-github
```

### "Failed to initialize GitHub Copilot provider"

**Possible causes:**
- Network error during authentication
- GitHub API is temporarily down
- Invalid token if pre-configured

**Solutions:**
1. Check your internet connection
2. Try again with `--use-github` to re-authenticate
3. If using a saved token, regenerate it on GitHub Settings

### "Authentication timeout"

**Solution:** The device code expired. Just run the command again:
```bash
contextify "your request" --use-github
```

Device codes expire after 15 minutes of inactivity.

### GitHub Copilot vs Gemini Performance

Both providers work well, but have different characteristics:

**GitHub Copilot:**
- ✓ Optimized for coding tasks
- ✓ Better understanding of GitHub contexts
- ✓ Uses your GitHub Copilot subscription

**Gemini:**
- ✓ General-purpose, fast
- ✓ Free tier available
- ✓ Good for non-coding contexts

Try both and see which works better for your workflows!

## Advanced: Custom Configuration

If you want to set up a **local Copilot Proxy** (VS Code extension), that's a more complex setup. For now, stick with the device flow auth or pre-configured token method above.

## Security Notes

- **Device codes** expire after 15 minutes and are single-use
- **Access tokens** are stored in your shell environment or `.env` file
- **Never commit** `.env` files with tokens to git
- Add to `.gitignore`:
  ```
  .env
  .env.local
  .env.*.local
  ```

## See Also

- [QUICKSTART.md](./QUICKSTART.md) - Basic usage guide
- [Contextify main docs](./README.md)
