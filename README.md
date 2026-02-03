# 🌉 Contextify - The Context Bridge for AI Coders

[![Version](https://img.shields.io/badge/version-1.1.0-blue.svg)](https://github.com/yourusername/contextify)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

**Contextify** transforms vague coding requests into detailed, context-aware prompts that get you working code on the first try.

## ✨ What's New in v1.1.0

- 🔐 **Auto-load `.env` files** - No more manual environment variable setup!
- 🎯 **Dry-run mode** (`--dry-run`) - Preview context without API calls
- 🎨 **Progress spinners** - Beautiful visual feedback during processing
- 📊 **Version flag** (`--version`) - Check your Contextify version
- 🚀 **Better UX** - Smoother workflow, clearer messages

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
git clone <your-repo-url>
cd contextify
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

# Use contextify
.\scripts\contextify.bat "add a dark mode toggle"
```

For detailed Windows setup, see [docs/WINDOWS.md](docs/WINDOWS.md)

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

## 📁 Project Structure

```
contextify/
├── README.md                    # Main documentation (you are here)
├── LICENSE                      # MIT License
├── requirements.txt             # Python dependencies
├── contextify.py                # Main CLI application
│
├── docs/                        # Documentation
│   ├── QUICKSTART.md           # 3-step quick start guide
│   ├── EXAMPLES.md             # 10+ real-world usage examples
│   ├── WINDOWS.md              # Windows-specific installation guide
│   └── CONTRIBUTING.md         # Contribution guidelines
│
├── scripts/                     # Installation & launcher scripts
│   ├── install.sh              # Linux/Mac installation
│   ├── install.ps1             # Windows detailed installation
│   ├── setup.ps1               # Windows quick setup
│   └── contextify.bat          # Windows batch launcher
│
├── tests/                       # Test suite
│   └── simple_test.py          # Core logic tests
│
└── examples/                    # Configuration examples
    └── .env.example            # Environment variables template
```

**Get Started:**
- New users: Start with [docs/QUICKSTART.md](docs/QUICKSTART.md)
- Need examples? Check [docs/EXAMPLES.md](docs/EXAMPLES.md)
- Windows user? See [docs/WINDOWS.md](docs/WINDOWS.md)
- Want to contribute? Read [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md)

## Features

### � New in v1.1.0

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

### �🎯 Intelligent Context Selection

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

### Environment Variables

```bash
# Required
export GEMINI_API_KEY='your-api-key'

# Optional: Change default max files
export CONTEXTIFY_MAX_FILES=30
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
- **Gemini 1.5 Flash**: FREE for up to 15 requests/minute
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
- Google Gemini 1.5 Flash (for massive context windows)
- Python 3
- A deep frustration with Copilot not understanding my codebase 😅

---

**Star this repo if Contextify saves you time!** ⭐
