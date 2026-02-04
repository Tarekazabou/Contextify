# Contextify CLI Flags Reference

This page explains every available flag in `contextify.py` and how to use them together.

## Output & destination
- `--output <path>`: Save the generated prompt to a file instead of clipboard.
- `--no-clipboard`: Print the prompt to stdout; useful for terminals without clipboard support.

## Context scope controls
- `--focus <area>`: Limit scanning to a part of the codebase. Common values: `frontend`, `backend`, `database`, `config`, `tests`.
- `--changed`: Only include files detected by `git diff` for the current working tree.
- `--target <path>`: Fully include one primary file for deep context.
- `--tree-shake`: When used with `--target`, include only direct dependencies of the target file.
- `--skeleton-context`: Strip implementations from non-target files to keep context lightweight (works best with `--target`).
- `--no-tree`: Disable directory tree output in the generated prompt.
- `--exclude-patterns <patterns>`: Comma-separated glob patterns to skip (in addition to `.gitignore` and built-in ignores).

## Prompt quality & safety
- `--hard-lock`: Enforce constraints from config files (e.g., required libraries, frameworks).
- `--no-negative-context`: Disable negative constraints that normally prevent off-stack suggestions.
- `--no-style`: Skip automatic style detection (language/framework/pattern inference).
- `--git-aware`: Add hints based on recent git activity to influence intent.
- `--max-files <n>`: Cap the number of files included (default: 30).
- `--temperature <float>`: Adjust LLM creativity (higher = more diverse output).
- `--model-name <id>`: Override the default Gemini model when generating prompts.

## Preview & diagnostics
- `--dry-run`: Show what would be sent without calling the API; helpful for debugging context selection.
- `--version`: Print the Contextify version and exit.

## Function-level precision
- `--scope-function <name>`: Add a “do not change outside this function” constraint for the targeted file.

## Usage patterns
- Focused frontend work:
  ```bash
  contextify "add search box" --focus frontend
  ```
- Targeted fix with minimal context:
  ```bash
  contextify "fix null error" --target src/utils/calc.ts --tree-shake --skeleton-context
  ```
- Git-aware bugfixing:
  ```bash
  contextify "resolve login crash" --changed --git-aware
  ```
- Preview before spending tokens:
  ```bash
  contextify "refactor checkout" --dry-run --focus backend
  ```
