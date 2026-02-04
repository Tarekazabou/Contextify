# Contextify CLI Flags Reference

This page explains every available flag in `contextify` and how to use them together.

## Prompt Generation Flags

### Output & Destination
- `--output <path>`: Save the generated prompt to a file instead of clipboard.
- `--no-clipboard`: Print the prompt to stdout; useful for terminals without clipboard support.

### Context Scope Controls
- `--focus <area>`: Limit scanning to a part of the codebase. Common values: `frontend`, `backend`, `database`, `config`, `tests`.
- `--changed`: Only include files detected by `git diff` for the current working tree.
- `--target <path>`: Fully include one primary file for deep context.
- `--tree-shake`: When used with `--target`, include only direct dependencies of the target file.
- `--skeleton-context`: Strip implementations from non-target files to keep context lightweight (works best with `--target`).
- `--no-tree`: Disable directory tree output in the generated prompt.
- `--exclude-patterns <patterns>`: Comma-separated glob patterns to skip (in addition to `.gitignore` and built-in ignores).

### Prompt Quality & Safety
- `--hard-lock`: Enforce constraints from config files (e.g., required libraries, frameworks).
- `--no-negative-context`: Disable negative constraints that normally prevent off-stack suggestions.
- `--no-style`: Skip automatic style detection (language/framework/pattern inference).
- `--git-aware`: Add hints based on recent git activity to influence intent.
- `--max-files <n>`: Cap the number of files included (default: 30).
- `--temperature <float>`: Adjust LLM creativity (higher = more diverse output).
- `--model <id>`: Override the default model when generating prompts. Examples:
  - `gpt-4`, `gpt-4o`
  - `gemini-2.5-flash`, `gemini-2.0-flash`
  - `claude-opus`, `claude-sonnet`

## Project Analysis Flags

### Static Analysis
- `--analyze`: Generate a static analysis report of your project structure without using AI. Shows:
  - Project structure and organization
  - Detected languages and frameworks
  - Entry points
  - Dependency analysis
  - Code statistics
  - Inferred architecture

**Example:**
```bash
contextify --analyze
# Output: Detailed technical report of your codebase
```

### AI-Enhanced Analysis
- `--analyze --ai`: Generate AI-powered architectural insights using your configured provider. Provides:
  - Detailed architecture overview
  - Project purpose and scope
  - Technology stack assessment
  - Code organization analysis
  - Data flow explanation
  - Key components and responsibilities
  - Development workflow guide
  - Dependencies and integrations
  - Potential issues and problems
  - Recommendations for improvement

**Example:**
```bash
contextify --analyze --ai
# Output: 10-section AI analysis with architectural insights
```

- `--ai`: (Used with `--analyze`) Enables AI enhancement for analysis. Requires a configured AI provider.

## General Flags

### Preview & Diagnostics
- `--dry-run`: Show what would be sent without calling the API; helpful for debugging context selection.
- `--version`: Print the Contextify version and exit.
- `--help`: Show help documentation for available commands and flags.

## Usage Patterns

### Basic Prompt Generation
```bash
# Simple request with default settings
contextify "add a search box"

# Save to file instead of clipboard
contextify "add a search box" --output search-prompt.md

# Print to terminal
contextify "add a search box" --no-clipboard
```

### Focused Context
```bash
# Frontend-specific work
contextify "add search box" --focus frontend

# Backend-specific work
contextify "create user API" --focus backend

# Database migrations
contextify "add user roles" --focus database
```

### Targeted Precision Fixes
```bash
# Deep dive into one file
contextify "fix null error" --target src/utils/calc.ts

# Same file, minimal context
contextify "fix null error" --target src/utils/calc.ts --tree-shake --skeleton-context

# Fix specific function without touching elsewhere
contextify "update calculation logic" --target src/utils/calc.ts --scope-function calculateTotal
```

### Git-Aware Development
```bash
# Only include changed files
contextify "resolve login crash" --changed

# Add recent git history as hints
contextify "fix deployment issue" --git-aware

# Combine changed + git-aware
contextify "fix bug" --changed --git-aware

# Preview before committing tokens
contextify "fix bug" --changed --dry-run
```

### Project Analysis
```bash
# Understand project structure
contextify --analyze

# Get AI insights about architecture
contextify --analyze --ai

# Save analysis to file
contextify --analyze --output analysis.md

# Get AI analysis without clipboard
contextify --analyze --ai --no-clipboard
```

### Advanced Usage
```bash
# Fine-tune model temperature (0.0-1.0, higher = more creative)
contextify "add feature" --temperature 0.3

# Use specific model
contextify "add feature" --model gpt-4

# Increase context files
contextify "major refactor" --max-files 100

# Exclude specific patterns
contextify "add feature" --exclude-patterns "*.test.ts,*.spec.ts"

# Hard-lock tech stack constraints
contextify "refactor" --hard-lock

# Disable style detection
contextify "add feature" --no-style
```

## Command Combinations

### Development Workflow
1. **Understand the codebase:**
   ```bash
   contextify --analyze --ai
   ```

2. **Work on a specific feature:**
   ```bash
   contextify "add user dashboard" --focus frontend
   ```

3. **Fix a bug in changed files:**
   ```bash
   contextify "fix login bug" --changed --git-aware
   ```

4. **Targeted file modification:**
   ```bash
   contextify "optimize performance" --target src/api/users.ts --tree-shake
   ```

### Team Collaboration
```bash
# Generate documentation
contextify --analyze --ai --output architecture.md

# Create onboarding guide
contextify --analyze --output structure.md
```
