# Changelog

All notable changes to Contextify will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2026-02-04

### Added
- **Auto-load `.env` file**: Automatically loads `GEMINI_API_KEY` from `.env` files in current directory, script directory, or `~/.contextify/.env`
- **`--version` flag**: Show version number with `contextify --version` or `contextify -v`
- **`--dry-run` flag**: Preview gathered context without making API calls (useful for debugging and cost control)
- **Progress spinner**: Animated spinner provides visual feedback during context gathering and prompt generation
- **`python-dotenv` dependency**: Added for better `.env` file support (optional, falls back to manual parsing)

### Changed
- Error message now mentions creating `.env` file as an alternative to environment variables
- API key check now skipped in dry-run mode

### Improved
- Better user experience with visual feedback during processing
- More flexible environment variable management
- Clearer indication of what the tool is doing at each step

## [1.0.0] - 2026-02-03

### Added
- Initial release
- Context-aware prompt generation for AI coding assistants
- Support for multiple focus modes (frontend, backend, database, config, tests)
- Git integration with `--changed` flag
- Customizable output with `--output`, `--max-files`, `--no-clipboard`
- Model selection with `--model-name` and `--temperature` control
- Conditional context with `--no-tree` and `--no-style`
- Detail level control with `-s/--simple` and `-d/--detailed`
- Custom exclusion patterns with `--exclude-patterns`
- Cross-platform installation scripts (Windows, Linux, macOS)
- Comprehensive documentation
