# 🌉 Contextify - The Context Bridge for AI Coders

**Contextify** transforms vague coding requests into detailed, context-aware prompts that get you working code on the first try.

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

```bash
# Navigate to project directory
cd contextify

# Run the installation script
chmod +x scripts/install.sh
./scripts/install.sh

# Set your Gemini API key (get one from https://makersuite.google.com/app/apikey)
export GEMINI_API_KEY='your-api-key-here'

# Add to your shell config to make it permanent
echo 'export GEMINI_API_KEY="your-api-key-here"' >> ~/.bashrc
```

## Quick Start

```bash
# Basic usage - generates prompt and copies to clipboard
contextify "add a dark mode toggle"

# Focus on specific part of codebase
contextify "create a user profile card" --focus frontend

# Only look at changed files (great for bug fixes)
contextify "fix the login bug" --changed

# Save to file instead of clipboard
contextify "refactor authentication" --output prompt.md
```

## Features

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

### 🎯 Targeted Context (New Flags)

Scope context tightly for precision fixes:

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

### 🔒 Hard Lock Constraints

Enforces strict tech-stack constraints from config files:

```bash
contextify "refactor auth" --hard-lock
```

Disable negative constraints if needed:

```bash
contextify "refactor auth" --no-negative-context
```

## Architecture

### Key Components

1. **ContextGatherer** - Scans codebase intelligently
   - File tree generation
   - Style analysis
   - Sensitive file filtering
   - Git integration

2. **PromptGenerator** - Creates refined prompts
   - Gemini API integration
   - Context-aware prompt engineering
   - Style matching

3. **CLI Interface** - User-friendly command-line tool
   - Focus modes
   - Output options
   - Flexible configuration

## Requirements

- Python 3.8+
- Dependencies (installed by install.sh):
  - `google-generativeai>=0.3.0` - Gemini API client
  - `pyperclip>=1.8.0` - Clipboard integration
  - `pathspec>=0.11.0` - .gitignore parsing

## Project Structure

```
Contextify/
├── contextify.py              # Main CLI application (rooted in repo)
├── scripts/                   # Installation & launcher scripts
│   ├── install.sh             # Linux/Mac installation
│   ├── install.ps1            # Windows installation
│   └── contextify.bat         # Windows launcher
├── docs/                      # Documentation (you're here)
│   ├── README.md
│   ├── QUICKSTART.md
│   ├── EXAMPLES.md
│   └── FLAGS.md               # CLI flags reference
├── tests/                     # Test suite
│   └── simple_test.py
├── requirements.txt           # Python dependencies
└── LICENSE                    # MIT License
```

## Troubleshooting

### "GEMINI_API_KEY not set" error

Get your free API key from https://makersuite.google.com/app/apikey and set it:

```bash
export GEMINI_API_KEY='your-api-key-here'
```

### "pyperclip not available" error

Install pyperclip:
```bash
pip install pyperclip
```

Or use `--output` flag to save to file instead:
```bash
contextify "your request" --output prompt.md
```

### "No matching files" when using --focus

Make sure your directory names match the focus patterns. Use `--no-clipboard` to see what's being scanned:

```bash
contextify "your request" --focus frontend --no-clipboard
```

## Comparison with Alternatives

| Feature | Contextify | ChatGPT | Copilot | Cursor |
|---------|-----------|---------|---------|---------|
| Context-aware | ✅ Yes | ❌ No | ⚠️ Limited | ⚠️ Limited |
| Style detection | ✅ Yes | ❌ No | ❌ No | ⚠️ Limited |
| Git integration | ✅ Yes | ❌ No | ❌ No | ❌ No |
| Clipboard ready | ✅ Yes | ❌ No | ❌ No | ❌ No |
| Free | ✅ Yes* | ❌ No | ⚠️ Limited | ✅ Yes |

*Free Gemini API tier available

## License

MIT - Use freely in personal and commercial projects
