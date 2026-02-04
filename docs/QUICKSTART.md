# Contextify - Quick Start Guide

## What is Contextify?

Contextify is a CLI tool that bridges the gap between your vague coding ideas and precise AI-generated code. It scans your entire codebase, understands your architecture, and generates highly detailed prompts that work perfectly with GitHub Copilot, ChatGPT, Claude, or any AI coding assistant.

## The Problem It Solves

When you ask Copilot to "create a user card", you get generic code that:
- ❌ Doesn't match your styling system
- ❌ Breaks your TypeScript interfaces
- ❌ Ignores your existing components
- ❌ Requires 20+ minutes of manual fixes

## The Solution

Contextify uses AI providers with massive context windows to:
1. Scan your ENTIRE codebase
2. Detect your tech stack and coding patterns
3. Generate a perfect, detailed prompt
4. Copy it to your clipboard for instant use

## Installation (3 Steps)

### Step 1: Install the Tool

Navigate to your Contextify directory and run the appropriate script:

**Windows (PowerShell):**
```powershell
.\scripts\setup.ps1
```

**Linux/macOS:**
```bash
chmod +x scripts/install.sh
./scripts/install.sh
```

### Step 2: Set Up Your AI Provider

Choose your preferred setup method:

**Interactive Setup (Recommended):**
```bash
contextify onboard
```

This guides you through selecting a provider, authenticating, and choosing your model.

**Quick Setup with Environment Variable:**
```bash
export GEMINI_API_KEY='your-api-key-here'          # Linux/macOS
set GEMINI_API_KEY=your-api-key-here               # Windows Command Prompt
$env:GEMINI_API_KEY='your-api-key-here'            # Windows PowerShell
```

Get your free API key: https://aistudio.google.com/app/apikey

### Step 3: Test It

In any code project directory:

```bash
contextify "add a dark mode toggle"
```

The prompt is now in your clipboard. Paste it into GitHub Copilot, ChatGPT, Claude, or any AI tool!

## Basic Usage

### Simple Request

```bash
contextify "your request here"
```

### Focus on Specific Area

```bash
contextify "create user profile card" --focus frontend
contextify "add posts endpoint" --focus backend
contextify "add user table" --focus database
```

### Only Changed Files (Great for Bug Fixes)

```bash
contextify "fix the login bug" --changed
```

### Save to File

```bash
contextify "major refactor" --output prompt.md
```

### Target a Specific File or Function

```bash
contextify "update totals" --target src/utils/calc.ts --scope-function calculateTotal
```

### Minimal Context for a Target

```bash
contextify "fix bug in checkout" --target src/Checkout.tsx --tree-shake --skeleton-context
```

### Add Git-Aware Hints

```bash
contextify "fix the build error" --git-aware
```

## Real Examples

### Example 1: Adding a Component

```bash
cd ~/my-react-app
contextify "create a UserCard component that shows name, email, and avatar" --focus frontend
```

**What you get:**
- Detailed prompt that references YOUR components
- Uses YOUR design system (Tailwind, styled-components, etc.)
- Matches YOUR TypeScript interfaces
- Follows YOUR coding patterns

### Example 2: API Development

```bash
cd ~/my-backend
contextify "create a POST endpoint for blog posts with validation" --focus backend
```

**What you get:**
- Uses YOUR routing pattern (Express, Fastify, Next.js)
- Matches YOUR database schema
- Includes YOUR validation library (Zod, Yup)
- Follows YOUR auth middleware

### Example 3: Bug Fixing

```bash
# After making some changes and encountering a bug:
contextify "fix the TypeError in the form submission" --changed
```

**What you get:**
- Only looks at files you modified
- Focused, relevant context
- Faster and more accurate

## Pro Tips

### 1. Use Aliases

```bash
# Add to ~/.bashrc or ~/.zshrc
alias ctx="contextify"
alias ctxf="contextify --focus frontend"
alias ctxb="contextify --focus backend"

# Usage:
ctx "add feature"
ctxf "create component"
```

### 2. Combine with Git Workflow

```bash
git checkout -b feature/new-dashboard
# ... make some changes ...
contextify "complete the dashboard" --changed
```

### 3. Multi-Step Complex Features

```bash
# Break down big features:
contextify "add commenting system" --focus database --output step1-db.md
contextify "add comment API" --focus backend --output step2-api.md
contextify "add comment UI" --focus frontend --output step3-ui.md
```

## Focus Modes Explained

| Focus | What It Scans |
|-------|---------------|
| `frontend` | `/src`, `/components`, `/pages`, `/app`, `/styles` |
| `backend` | `/server`, `/api`, `/routes`, `/controllers`, `/services` |
| `database` | `/prisma`, `/migrations`, `/schema`, `/db`, SQL files |
| `config` | Config files, `package.json`, build tools |
| `tests` | `/test`, `/tests`, `__tests__`, `.spec` files |

## Common Workflows

### Creating New Features

```bash
contextify "add user authentication" --focus backend
# Paste into your AI assistant, implement
# Test it
contextify "add login form" --focus frontend
# Paste into your AI assistant, implement
```

### Refactoring

```bash
contextify "refactor auth to use JWT" --focus backend --max-files 40
```

### Writing Tests

```bash
contextify "write tests for user service" --focus tests
```

### Styling Updates

```bash
contextify "update all buttons to use our new design system" --focus frontend
```

## Using with Different AI Tools

### GitHub Copilot in VS Code

1. Run: `contextify "your request"`
2. Create a new file in VS Code
3. Paste the prompt as a comment
4. Let Copilot generate the code

### ChatGPT / Claude

1. Run: `contextify "your request" --output prompt.txt`
2. Upload or paste `prompt.txt` into the chat
3. Get perfectly contextualized code

### Cursor

1. Run: `contextify "your request"`
2. Open Cursor's AI chat (Cmd+L)
3. Paste and let Cursor generate

## Troubleshooting

### "Command not found: contextify"

**Windows PowerShell:**
```powershell
. $PROFILE  # Reload your profile
```

**Linux/macOS:**
```bash
source ~/.bashrc      # for bash
source ~/.zshrc       # for zsh
```

### "API Key not found"

Set up your provider using either method:

**Interactive setup:**
```bash
contextify onboard
```

**Environment variable:**
```bash
export GEMINI_API_KEY='your-key-here'
```

### Getting rate limited?

```bash
# Reduce number of files:
contextify "request" --max-files 15

# Or use focus mode:
contextify "request" --focus frontend
```

## What Makes Contextify Special?

✅ **Understands YOUR codebase** - Not generic patterns
✅ **Massive context** - Millions of tokens via multiple AI providers
✅ **Smart filtering** - Ignores secrets, node_modules automatically
✅ **Style matching** - Detects your frameworks and patterns
✅ **Git integration** - Focus on changed files
✅ **Works with any AI** - Copilot, ChatGPT, Claude, Cursor
✅ **Secure credentials** - Uses OS keyring for safe storage

## Supported Providers

- **Google Gemini** - Fast, generous free tier
- **GitHub Copilot** - Via device flow authentication
- **OpenAI** - GPT-4 and GPT-3.5 Turbo
- **Anthropic Claude** - Claude 3 models
- **Local Proxy** - Connect to local AI servers

## Need Help?

```bash
# View all options:
contextify --help

# View all flags:
contextify prompt --help

# Check examples:
cat docs/EXAMPLES.md

# Read full documentation:
cat docs/README.md
```

## Next Steps

1. ✅ Install the tool (`./scripts/setup.ps1` or `./scripts/install.sh`)
2. ✅ Set up provider (`contextify onboard` or set API key)
3. ✅ Try it: `contextify "your first request"`
4. 📚 Read [docs/EXAMPLES.md](EXAMPLES.md) for more use cases
5. 🚀 Start generating amazing code!

**Happy coding! Let Contextify bridge the gap between your ideas and perfect code.** 🚀



## Basic Usage

### Simple Request

```bash
contextify "your request here"
```

### Focus on Specific Area

```bash
contextify "create user profile card" --focus frontend
contextify "add posts endpoint" --focus backend
contextify "add user table" --focus database
```

### Only Changed Files (Great for Bug Fixes)

```bash
contextify "fix the login bug" --changed
```

### Save to File

```bash
contextify "major refactor" --output prompt.md
```

### Target a Specific File or Function

```bash
contextify "update totals" --target src/utils/calc.ts --scope-function calculateTotal
```

### Minimal Context for a Target

```bash
contextify "fix bug in checkout" --target src/Checkout.tsx --tree-shake --skeleton-context
```

### Add Git-Aware Hints

```bash
contextify "fix the build error" --git-aware
```

## Real Examples

### Example 1: Adding a Component

```bash
cd ~/my-react-app
contextify "create a UserCard component that shows name, email, and avatar" --focus frontend
```

**What you get:**
- Detailed prompt that references YOUR components
- Uses YOUR design system (Tailwind, styled-components, etc.)
- Matches YOUR TypeScript interfaces
- Follows YOUR coding patterns

### Example 2: API Development

```bash
cd ~/my-backend
contextify "create a POST endpoint for blog posts with validation" --focus backend
```

**What you get:**
- Uses YOUR routing pattern (Express, Fastify, Next.js)
- Matches YOUR database schema
- Includes YOUR validation library (Zod, Yup)
- Follows YOUR auth middleware

### Example 3: Bug Fixing

```bash
# After making some changes and encountering a bug:
contextify "fix the TypeError in the form submission" --changed
```

**What you get:**
- Only looks at files you modified
- Focused, relevant context
- Faster and more accurate

## Pro Tips

### 1. Use Aliases

```bash
# Add to ~/.bashrc or ~/.zshrc
alias ctx="contextify"
alias ctxf="contextify --focus frontend"
alias ctxb="contextify --focus backend"

# Usage:
ctx "add feature"
ctxf "create component"
```

### 2. Combine with Git Workflow

```bash
git checkout -b feature/new-dashboard
# ... make some changes ...
contextify "complete the dashboard" --changed
```

### 3. Multi-Step Complex Features

```bash
# Break down big features:
contextify "add commenting system" --focus database --output step1-db.md
contextify "add comment API" --focus backend --output step2-api.md
contextify "add comment UI" --focus frontend --output step3-ui.md
```

## Focus Modes Explained

| Focus | What It Scans |
|-------|---------------|
| `frontend` | `/src`, `/components`, `/pages`, `/app`, `/styles` |
| `backend` | `/server`, `/api`, `/routes`, `/controllers`, `/services` |
| `database` | `/prisma`, `/migrations`, `/schema`, `/db`, SQL files |
| `config` | Config files, `package.json`, build tools |
| `tests` | `/test`, `/tests`, `__tests__`, `.spec` files |

## Common Workflows

### Creating New Features

```bash
contextify "add user authentication" --focus backend
# Paste into your AI assistant, implement
# Test it
contextify "add login form" --focus frontend
# Paste into your AI assistant, implement
```

### Refactoring

```bash
contextify "refactor auth to use JWT" --focus backend --max-files 40
```

### Writing Tests

```bash
contextify "write tests for user service" --focus tests
```

### Styling Updates

```bash
contextify "update all buttons to use our new design system" --focus frontend
```

## Using with Different AI Tools

### GitHub Copilot in VS Code

1. Run: `contextify "your request"`
2. Create a new file in VS Code
3. Paste the prompt as a comment
4. Let Copilot generate the code

### ChatGPT / Claude

1. Run: `contextify "your request" --output prompt.txt`
2. Upload or paste `prompt.txt` into the chat
3. Get perfectly contextualized code

### Cursor

1. Run: `contextify "your request"`
2. Open Cursor's AI chat (Cmd+L)
3. Paste and let Cursor generate

## Troubleshooting

### "Command not found: contextify"

**Windows PowerShell:**
```powershell
. $PROFILE  # Reload your profile
```

**Linux/macOS:**
```bash
source ~/.bashrc      # for bash
source ~/.zshrc       # for zsh
```

### "API Key not found"

Set up your provider using either method:

**Interactive setup:**
```bash
contextify onboard
```

**Environment variable:**
```bash
export GEMINI_API_KEY='your-key-here'
```

### Getting rate limited?

```bash
# Reduce number of files:
contextify "request" --max-files 15

# Or use focus mode:
contextify "request" --focus frontend
```

## What Makes Contextify Special?

✅ **Understands YOUR codebase** - Not generic patterns
✅ **Massive context** - Millions of tokens via multiple AI providers
✅ **Smart filtering** - Ignores secrets, node_modules automatically
✅ **Style matching** - Detects your frameworks and patterns
✅ **Git integration** - Focus on changed files
✅ **Works with any AI** - Copilot, ChatGPT, Claude, Cursor
✅ **Secure credentials** - Uses OS keyring for safe storage

## Supported Providers

- **Google Gemini** - Fast, generous free tier
- **GitHub Copilot** - Via device flow authentication
- **OpenAI** - GPT-4 and GPT-3.5 Turbo
- **Anthropic Claude** - Claude 3 models
- **Local Proxy** - Connect to local AI servers

## Need Help?

```bash
# View all options:
contextify --help

# View all flags:
contextify prompt --help

# Check examples:
cat docs/EXAMPLES.md

# Read full documentation:
cat docs/README.md
```

## Next Steps

1. ✅ Install the tool (`./scripts/setup.ps1` or `./scripts/install.sh`)
2. ✅ Set up provider (`contextify onboard` or set API key)
3. ✅ Try it: `contextify "your first request"`
4. 📚 Read [docs/EXAMPLES.md](EXAMPLES.md) for more use cases
5. 🚀 Start generating amazing code!

**Happy coding! Let Contextify bridge the gap between your ideas and perfect code.** 🚀
