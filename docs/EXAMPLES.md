# Contextify Examples

## Example 1: Adding Dark Mode to a React App

```bash
contextify "add a dark mode toggle to the navbar" --focus frontend
```

**What Contextify does:**
1. Scans your React components
2. Detects you're using Tailwind CSS
3. Finds your existing theme configuration
4. Generates a detailed prompt that references your actual Navbar component

**Generated prompt includes:**
- Your existing Navbar.tsx structure
- Your Tailwind theme colors
- Your state management pattern (Context API, Zustand, etc.)
- Specific instructions to match your coding style

## Example 2: Adding API Endpoint

```bash
contextify "create a POST endpoint for creating user posts" --focus backend
```

**What Contextify does:**
1. Scans your API routes
2. Detects Express/Fastify/Next.js API routes
3. Finds your database schema and models
4. Finds existing validation patterns

**Generated prompt includes:**
- Your routing patterns
- Database model structures
- Validation schemas
- Authentication middleware usage

## Example 3: Bug Fix with Git Integration

```bash
# After making some changes and encountering a bug
contextify "fix the TypeError when submitting the form" --changed
```

**What Contextify does:**
1. Only looks at files you've modified (git diff)
2. Focuses context on the relevant area
3. Includes error patterns from your code

**Perfect for:**
- Quick bug fixes
- Debugging specific features
- Iterative development

## Example 4: Database Migration

```bash
contextify "add a migration for user profile photos" --focus database
```

**What Contextify does:**
1. Scans your Prisma schema / SQL migrations
2. Detects your migration pattern
3. Includes existing table structures
4. Provides template based on your patterns

## Example 5: Creating a New Feature (Multi-step)

For complex features, use Contextify multiple times:

```bash
# Step 1: Plan the feature with full context
contextify "create a commenting system for blog posts" --output step1-plan.md

# Step 2: Build the database layer
contextify "add database models for comments" --focus database --output step2-db.md

# Step 3: Build the API
contextify "create API endpoints for comments" --focus backend --output step3-api.md

# Step 4: Build the UI
contextify "create comment components" --focus frontend --output step4-ui.md
```

## Example 6: Refactoring

```bash
contextify "refactor the authentication to use JWT instead of sessions" --focus backend --max-files 40
```

**Tips for refactoring:**
- Use higher `--max-files` to get more context
- Focus on the specific area
- Consider using `--output` to save the prompt for reference

## Example 7: Style Consistency

```bash
contextify "make all components use our design system consistently"
```

**Contextify automatically detects:**
- Your design system location
- Component patterns
- Styling approach
- Naming conventions

## Example 8: Testing

```bash
contextify "write tests for the user authentication flow" --focus tests
```

**What Contextify provides:**
- Your testing framework (Jest, Vitest, etc.)
- Existing test patterns
- Mock patterns
- Assertion styles

## Example 9: Configuration Update

```bash
contextify "add tailwind configuration for custom colors" --focus config
```

**Focuses on:**
- Configuration files only
- Package.json dependencies
- Build tools
- Environment setup

## Example 10: Working with Large Codebases

For huge projects, break it down:

```bash
# Focus on just the area you need
contextify "update the checkout flow" --focus frontend --max-files 20

# Or use git to limit scope
contextify "fix issues from the last commit" --changed
```

## Pro Tips

### 1. Use Focus Modes Aggressively
```bash
# Instead of scanning everything
contextify "add feature"

# Be specific
contextify "add feature" --focus frontend
```

### 2. Combine with Git Workflow
```bash
# Start a feature branch
git checkout -b feature/new-thing

# Make some changes
# ... edit files ...

# Generate prompt for next steps
contextify "complete the user dashboard" --changed
```

### 3. Save Important Prompts
```bash
# For documentation
contextify "major feature" --output docs/feature-prompt.md

# For team sharing
contextify "new API design" --output team-review.md
```

### 4. Iterate Quickly
```bash
# First attempt
contextify "add search"

# Paste into Copilot, get code
# Test it, find issues

# Refine
contextify "fix the search to include fuzzy matching" --changed
```

### 5. Use with Different AI Tools

**With GitHub Copilot:**
```bash
contextify "feature" 
# Paste as a comment in a new file
# Let Copilot generate
```

**With ChatGPT:**
```bash
contextify "feature" --output prompt.txt
# Upload to ChatGPT or paste in chat
```

**With Cursor:**
```bash
contextify "feature"
# Paste into Cursor's AI chat
# Apply changes directly
```

## Common Patterns

### New Component
```bash
contextify "create a [ComponentName] component" --focus frontend
```

### New API Route
```bash
contextify "create [method] endpoint for [resource]" --focus backend
```

### Database Change
```bash
contextify "add [schema change]" --focus database
```

### Bug Fix
```bash
contextify "fix [specific issue]" --changed
```

### Refactor
```bash
contextify "refactor [area] to use [pattern]" --focus [area] --max-files 40
```

### Test Addition
```bash
contextify "add tests for [feature]" --focus tests
```

## Workflow Integration

### Pre-commit Hook
```bash
# In .git/hooks/pre-commit
#!/bin/bash
if [ -n "$(git diff --cached --name-only)" ]; then
    echo "💡 Tip: Run 'contextify \"commit message\" --changed' for AI assistance"
fi
```

### VS Code Task
```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Contextify Current Feature",
      "type": "shell",
      "command": "contextify",
      "args": ["${input:feature}", "--changed"],
      "problemMatcher": []
    }
  ],
  "inputs": [
    {
      "id": "feature",
      "type": "promptString",
      "description": "What are you working on?"
    }
  ]
}
```

### Alias for Speed
```bash
# Add to ~/.bashrc or ~/.zshrc
alias ctx="contextify"
alias ctxf="contextify --focus frontend"
alias ctxb="contextify --focus backend"
alias ctxc="contextify --changed"

# Usage
ctx "add feature"
ctxf "create component"
ctxc "fix bug"
```
