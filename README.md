# 🌉 Contextify - The Context Bridge for AI Coders

[![Version](https://img.shields.io/badge/version-1.2.0-blue.svg)](https://github.com/Tarekazabou/Contextify)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

**Contextify** transforms vague coding requests into detailed, context-aware prompts that get you working code on the first try.

## ✨ What's New in v1.2.0

- 🔍 **Project Analysis** (`--analyze`) - Static analysis of project structure, architecture, and workflow
- 🤖 **AI-Enhanced Analysis** (`--analyze --ai`) - AI-powered architectural insights and recommendations
- 🔐 **GitHub Copilot Support** - Fixed two-stage authentication with proper IDE headers
- 💾 **Multi-Provider Support** - GitHub Copilot, Google Gemini, OpenAI, Anthropic, Local Proxy
- 🎨 **Smart Provider Detection** - Automatically selects the right AI provider based on configuration

## The Problem

GitHub Copilot and ChatGPT are powerful, but they often lack the "big picture" of your specific codebase. You end up with:
- Generic code that doesn't match your style
- Wrong component imports
- Broken TypeScript interfaces
- Code that ignores your design system

## The Solution

Contextify uses **Gemini's massive context window** (1M+ tokens) to:

1. 🔍 **Scan your entire codebase** - file structure, dependencies, code patterns
2. 🎨 **Detect your coding style** - React vs Vue, Tailwind vs CSS, arrow functions vs regular
3. 🛡️ **Filter sensitive files** - automatically ignores `.env`, `.pem`, and follows `.gitignore`
4. 🤖 **Generate a perfect prompt** - detailed instructions that your AI coder can execute perfectly

## Installation

### Quick Start (Recommended)

**1. Clone the repository:**
```bash
git clone https://github.com/Tarekazabou/Contextify.git
cd Contextify
```

**2. Create a `.env` file in the project root:**
```bash
echo "GEMINI_API_KEY=your-api-key-here" > .env
```
Get your free API key from: https://aistudio.google.com/app/apikey

**3. Run the installation script:**

### Linux/Mac
```bash
chmod +x scripts/install.sh
./scripts/install.sh
```

### Windows
```powershell
.\scripts\setup.ps1
```

**That's it!** The `.env` file will be automatically loaded.

### Use Contextify (Windows example)
```powershell
.\scripts\contextify.bat "add a dark mode toggle"
```

For detailed Windows setup, see [docs/WINDOWS.md](docs/WINDOWS.md)

## Quick Start

```bash
# Basic usage - generates prompt and copies to clipboard
contextify "add a dark mode toggle"

# Focus on specific part of codebase
contextify "create a user profile card" --focus frontend

# Analyze your project structure
contextify --analyze

# Get AI-powered architectural analysis
contextify --analyze --ai

# Only look at changed files (great for bug fixes)
contextify "fix the login bug" --changed

# Save to file instead of clipboard
contextify "refactor authentication" --output prompt.md

# Target a specific file and function
contextify "update totals" --target src/utils/calc.ts --scope-function calculateTotal

# Minimal context (dependencies only) for a specific target
contextify "fix bug in checkout" --target src/Checkout.tsx --tree-shake --skeleton-context

# Add recent git activity as a clue
contextify "fix the build error" --git-aware
```

## 📁 Project Structure

```
contextify/
├── contextify/          (source code)
│   ├── __init__.py
│   ├── contextify.py
│   ├── auth.py
│   ├── config.py
│   ├── onboarding.py
│   └── providers.py
├── docs/               (documentation)
├── scripts/            (setup/deployment scripts)
├── tests/              (test files)
├── examples/           (example usage)
├── .env.example
├── .gitignore
├── LICENSE
├── README.md
├── CHANGELOG.md
├── requirements.txt
└── QUICK_REFERENCE.md
```

**Get Started:**
- New users: Start with [docs/QUICKSTART.md](docs/QUICKSTART.md)
- Need examples? Check [docs/EXAMPLES.md](docs/EXAMPLES.md)
- Windows user? See [docs/WINDOWS.md](docs/WINDOWS.md)
- Want to contribute? Read [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md)
- All flags explained: See [docs/FLAGS.md](docs/FLAGS.md)

## Features

### ✨ New in v1.1.0

**Auto-load `.env` files:**
```bash
# Just create a .env file with your API key
echo "GEMINI_API_KEY=your-key" > .env

# Contextify automatically loads it!
contextify "your request"
```

**Dry-run mode for debugging:**
```bash
contextify "add dark mode" --dry-run
# Shows exactly what context will be sent (no API call, no cost)
```

**Check your version:**
```bash
contextify --version
# Output: contextify.py 1.1.0
```

### 🎯 Intelligent Context Selection

Use `--focus` to scan only relevant parts of your codebase:

- `--focus frontend` - Only scans `/src`, `/components`, `/pages`, etc.
- `--focus backend` - Only scans `/server`, `/api`, `/routes`, etc.
- `--focus database` - Only scans `/prisma`, `/migrations`, SQL files
- `--focus config` - Only scans config files
- `--focus tests` - Only scans test files

**Example:**
```bash
contextify "add pagination to the products API" --focus backend
```

### 🔄 Git Integration

Use `--changed` to only analyze files you're currently working on (based on `git diff`):

```bash
contextify "fix the bug causing the crash" --changed
```

### 🎯 Targeted Context (New Flags)

Use these to tightly scope context for precision fixes:

- `--target <path>`: Fully include one primary file
- `--tree-shake`: Only include direct dependencies of `--target`
- `--skeleton-context`: Strip implementations from non-target files
- `--scope-function <name>`: Add a “do not change outside this function” constraint

**Examples:**
```bash
contextify "update totals" --target src/utils/calc.ts --scope-function calculateTotal
contextify "fix bug in checkout" --target src/Checkout.tsx --tree-shake --skeleton-context
```

### 🧭 Git-Aware Hints

Injects recently modified git files as an intent clue:

```bash
contextify "fix the build error" --git-aware
```

### 📊 Project Analysis Features

**NEW in v1.2.0**: Analyze your project structure without generating a prompt.

#### Static Analysis (`--analyze`)

Get a detailed technical breakdown of your project:

```bash
contextify --analyze
```

Generates a report including:
- **Architecture Overview** - Project structure and organization
- **Technology Stack** - Detected languages, frameworks, libraries
- **Entry Points** - Main application files identified
- **Dependencies** - Import/dependency analysis
- **Code Statistics** - File counts, LOC estimates
- **Configuration** - Config files detected
- **Dataflow** - Inferred application flow

Perfect for:
- Onboarding new team members
- Understanding existing codebases
- Technical documentation
- Architecture reviews

#### AI-Enhanced Analysis (`--analyze --ai`)

Get AI-powered insights about your architecture:

```bash
contextify --analyze --ai
```

Uses your configured AI provider (GitHub Copilot, Google Gemini, etc.) to generate:
- **Detailed Architecture Overview** - Complete system design explanation
- **Project Purpose & Scope** - What the project does and why
- **Technology Stack Assessment** - Why these technologies were chosen
- **Code Organization Analysis** - Directory structure and design patterns
- **Data Flow Explanation** - How data moves through the system
- **Key Components** - Important files and their responsibilities
- **Development Workflow** - How to work with the codebase
- **Dependencies & Integrations** - External systems and libraries used
- **Potential Issues** - Areas needing attention
- **Recommendations** - Suggested improvements

Example output:
```
# Project Analysis Report

## 1. Architecture Overview
This is a full-stack TypeScript/Node.js application using Next.js for the frontend...

## 2. Project Purpose & Scope
The application is an e-commerce platform designed to handle product listings, shopping carts,
and payment processing...

[... 8 more sections ...]
```

Perfect for:
- AI-assisted architecture reviews
- Deep codebase understanding
- Team documentation
- Planning refactoring efforts

### 🔒 Hard Lock Constraints

Enforces strict tech-stack constraints from config files:

```bash
contextify "refactor auth" --hard-lock
```

Disable negative constraints if needed:

```bash
contextify "refactor auth" --no-negative-context
```

### 🎨 Automatic Style Detection

Contextify automatically detects and includes:
- **Language**: TypeScript, JavaScript, Python, etc.
- **Framework**: React, Next.js, Vue, Angular
- **Styling**: Tailwind CSS, styled-components
- **Validation**: Zod, Yup
- **Testing**: Jest, Vitest
- **Patterns**: Arrow functions, naming conventions

### 🛡️ Security & Privacy

Contextify automatically ignores sensitive files:
- Environment files (`.env*`)
- Private keys (`*.pem`, `*id_rsa*`)
- Certificates (`*.cert`, `*.p12`)
- Any files matching patterns in `.gitignore`
- Common ignore patterns (`node_modules`, `.git`, etc.)

### 📋 Output Modes

**Clipboard Mode (Default):**
```bash
contextify "add search functionality"
# Automatically copies to clipboard - just Cmd+V into your editor!
```

**File Mode:**
```bash
contextify "create admin dashboard" --output dashboard-prompt.md
# Saves prompt to a file for documentation or later use
```

**Print Mode:**
```bash
contextify "refactor database layer" --no-clipboard
# Prints to terminal instead of clipboard
```

## Real-World Example

### Before Contextify

**You type:** "Create a user profile card"

**Copilot gives you:**
```jsx
// Generic card that doesn't match your app
function UserCard() {
  return (
    <div className="card">
      <h2>User Name</h2>
      <p>user@email.com</p>
    </div>
  );
}
```

❌ Wrong styling  
❌ No TypeScript types  
❌ Doesn't use your components  
❌ 20 minutes of manual fixes

### After Contextify

**You run:**
```bash
contextify "create a user profile card" --focus frontend
```

**Contextify generates:**
```
Act as a Senior React Developer. Create a UserProfileCard.tsx component.

Context:
- Language: TypeScript
- Framework: React with Next.js
- Styling: Tailwind CSS
- Component Pattern: Functional components with arrow functions

Use the existing components and types:
- User interface from @/types/user.ts
- Card component from @/components/ui/card.tsx
- Avatar component from @/components/Avatar.tsx
- Button component from @/components/ui/button.tsx

Requirements:
1. Display user's name, email, and role
2. Show avatar using the Avatar component
3. Include an "Edit Profile" button (variant='outline')
4. Use Tailwind classes matching our design system
5. Ensure strict TypeScript type safety
6. Follow existing code patterns (arrow functions, named exports)

Reference Code:

### types/user.ts
```typescript
export interface User {
  id: string;
  name: string;
  email: string;
  role: 'admin' | 'user';
  avatarUrl?: string;
}
```

[... includes relevant files ...]
```

**Copilot/ChatGPT now gives you:**
```tsx
// Perfect, production-ready code that matches your codebase exactly! ✨
```

## Advanced Usage

### Custom File Limits

Control how many files to include (default: 30):

```bash
contextify "major refactor" --max-files 50
```

### Multiple Focuses

For complex tasks, run multiple focused scans:

```bash
# First, get frontend context
contextify "add user dashboard" --focus frontend --output frontend-prompt.md

# Then, get backend context
contextify "add user dashboard API" --focus backend --output backend-prompt.md
```

### Integration with AI Coders

**GitHub Copilot:**
```bash
contextify "add feature" 
# Paste into a new file as a comment, then let Copilot generate
```

**ChatGPT/Claude:**
```bash
contextify "add feature" --output prompt.txt
# Upload prompt.txt or paste directly
```

**Cursor:**
```bash
contextify "add feature"
# Paste into Cursor's chat
```

## Configuration

### AI Provider Setup

Contextify supports multiple AI providers. Set up your preferred provider:

#### Google Gemini (Recommended - Free Tier Available)

1. Get your API key: https://aistudio.google.com/app/apikey
2. Add to `.env`:
```bash
GEMINI_API_KEY=your-api-key
```

#### GitHub Copilot

1. Requires active GitHub Copilot subscription
2. Add to `.env`:
```bash
GITHUB_TOKEN=ghp_xxxxxxxxxxxx
```

The tool will automatically handle two-stage authentication:
- Exchanges your GitHub token for a Copilot API token
- Manages token caching and refresh
- Includes proper IDE headers for compatibility

#### OpenAI (GPT-4)

```bash
OPENAI_API_KEY=sk-xxxxxxxxxx
```

#### Anthropic Claude

```bash
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxx
```

#### Local Proxy / Self-Hosted

```bash
LOCAL_PROXY_URL=http://localhost:8000
```

**Provider Priority:**
If multiple providers are configured, Contextify uses this order:
1. GitHub Copilot (if GITHUB_TOKEN is set)
2. Google Gemini (if GEMINI_API_KEY is set)
3. OpenAI (if OPENAI_API_KEY is set)
4. Anthropic (if ANTHROPIC_API_KEY is set)
5. Local Proxy (if LOCAL_PROXY_URL is set)

Use the `--model` flag to explicitly choose a provider:
```bash
contextify "your request" --model gemini-2.5-flash
contextify "your request" --model gpt-4
contextify "your request" --model claude-opus
```

### Environment Variables

```bash
# AI Configuration
export GEMINI_API_KEY='your-api-key'           # Google Gemini
export GITHUB_TOKEN='ghp_xxxxxxxxxxxx'         # GitHub Copilot
export OPENAI_API_KEY='sk-xxxxxxxxxx'          # OpenAI GPT
export ANTHROPIC_API_KEY='sk-ant-xxxxxxxxxx'   # Anthropic Claude

# Contextify Options
export CONTEXTIFY_MAX_FILES=30         # Max files to include in context
export CONTEXTIFY_NO_CLIPBOARD=false   # Disable clipboard integration
```

### Custom Ignore Patterns

Add patterns to your `.gitignore` and Contextify will respect them:

```
# .gitignore
*.log
temp/
experimental/
```

## How It Works

1. **Context Gathering** - Scans your file structure, respecting `.gitignore` and filtering sensitive files
2. **Style Analysis** - Detects your tech stack, frameworks, and coding patterns
3. **File Selection** - Intelligently picks the most relevant files (configs, changed files, key components)
4. **Prompt Generation** - Sends context to Gemini with a specialized prompt engineering system
5. **Output** - Copies the refined, detailed prompt to your clipboard

## Comparison with Similar Tools

| Feature | Contextify | Aider | GitHub Copilot Workspace |
|---------|-----------|-------|-------------------------|
| Large context window | ✅ (1M+ tokens) | ❌ | ✅ |
| Automatic style detection | ✅ | ❌ | ✅ |
| Focus modes | ✅ | ❌ | ❌ |
| Git integration | ✅ | ✅ | ✅ |
| Works with any AI coder | ✅ | ❌ | ❌ |
| Clipboard integration | ✅ | ❌ | N/A |
| Privacy filtering | ✅ | ⚠️ | ⚠️ |
| Free tier | ✅ | ✅ | ❌ |

## API Costs

Gemini pricing is very generous:
- **Gemini 2.5 Flash**: FREE for up to 15 requests/minute
- Even large codebases (~100K tokens) cost pennies

A typical request: $0.00 - $0.02

## Troubleshooting

### "Command not found: contextify"

Make sure `~/.local/bin` is in your PATH:
```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### "GEMINI_API_KEY not set"

Get your API key from https://makersuite.google.com/app/apikey and:
```bash
export GEMINI_API_KEY='your-key'
# Make it permanent:
echo 'export GEMINI_API_KEY="your-key"' >> ~/.bashrc
```

### "Clipboard not working"

The tool will print to terminal instead. Or install clipboard support:
```bash
# Linux
sudo apt-get install xclip

# macOS (usually works by default)
pip3 install pyperclip --break-system-packages
```

### "Too many files"

Reduce the file limit:
```bash
contextify "your request" --max-files 15
```

Or use focus mode:
```bash
contextify "your request" --focus frontend
```

## Roadmap

- [ ] Support for more languages (Rust, Go, Java)
- [ ] Direct execution mode (agent that applies changes)
- [ ] Multiple LLM providers (Claude, GPT-4)
- [ ] VS Code extension
- [ ] Custom style guides
- [ ] Team presets
- [ ] Diff preview before applying changes

## Contributing

Contributions are welcome! This is a rapidly evolving tool and we'd love your help making it better.

## License

MIT License - See LICENSE file for details

## Credits

Built with ❤️ for developers tired of generic AI-generated code.

Powered by:
- Google Gemini 2.5 Flash (for massive context windows)
- Python 3
- A deep frustration with Copilot not understanding my codebase 😅

---

**Star this repo if Contextify saves you time!** ⭐
