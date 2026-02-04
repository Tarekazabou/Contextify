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

Contextify uses Gemini's 1M+ token context window to:
1. Scan your ENTIRE codebase
2. Detect your tech stack and coding patterns
3. Generate a perfect, detailed prompt
4. Copy it to your clipboard for instant use

## Installation (3 steps)

### Step 1: Install the tool
```bash
chmod +x install.sh
./install.sh
```

### Step 2: Get Gemini API Key
1. Visit: https://makersuite.google.com/app/apikey
2. Create a free API key
3. Set it as environment variable:
```bash
export GEMINI_API_KEY='your-api-key-here'

# Make it permanent (add to ~/.bashrc or ~/.zshrc):
echo 'export GEMINI_API_KEY="your-api-key-here"' >> ~/.bashrc
source ~/.bashrc
```

### Step 3: Test it
```bash
# In any code project directory:
contextify "add a dark mode toggle"
```

The prompt is now in your clipboard - paste it into GitHub Copilot, ChatGPT, or Cursor!

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
# Add to ~/.bashrc
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
# Paste into Copilot, implement
# Test it
contextify "add login form" --focus frontend  
# Paste into Copilot, implement
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

### GitHub Copilot
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
```bash
# Make sure ~/.local/bin is in your PATH:
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### "GEMINI_API_KEY not set"
```bash
export GEMINI_API_KEY='your-key-here'
# Make permanent:
echo 'export GEMINI_API_KEY="your-key"' >> ~/.bashrc
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
✅ **Massive context** - 1M+ tokens via Gemini  
✅ **Smart filtering** - Ignores secrets, node_modules automatically  
✅ **Style matching** - Detects your frameworks and patterns  
✅ **Git integration** - Focus on changed files  
✅ **Works with any AI** - Copilot, ChatGPT, Claude, Cursor  
✅ **Free tier** - Gemini Flash is generous and fast  

## Cost

Gemini 1.5 Flash pricing:
- FREE: Up to 15 requests/minute
- Typical request: $0.00 - $0.02
- Even huge codebases: < $0.05 per request

## Need Help?

```bash
# View all options:
contextify --help

# Check examples:
cat docs/EXAMPLES.md

# Read full documentation:
cat docs/README.md
```

## Next Steps

1. ✅ Install the tool (`./install.sh`)
2. ✅ Set API key (`export GEMINI_API_KEY='...'`)
3. ✅ Try it: `contextify "your first request"`
4. 📚 Read `docs/EXAMPLES.md` for more use cases
5. ⭐ Star the repo if it saves you time!

---

**Happy coding! Let Contextify bridge the gap between your ideas and perfect code.** 🚀
