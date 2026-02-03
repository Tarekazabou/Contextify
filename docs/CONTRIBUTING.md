# Contributing to Contextify

## Development Setup

1. Clone the repository
   ```bash
   git clone <your-repo-url>
   cd contextify
   ```

2. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

3. Set API key
   ```bash
   export GEMINI_API_KEY='your-api-key'
   ```

4. Test the application
   ```bash
   python tests/simple_test.py
   ```

## Code Style

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide
- Use type hints for function parameters and returns
- Add docstrings to all functions and classes
- Keep security filtering strict (always err on the side of caution)
- Use meaningful variable and function names

## Project Structure

```
contextify/
├── contextify.py        # Main application - 3 classes
├── requirements.txt     # Python dependencies
├── docs/               # Documentation
├── scripts/            # Installation scripts
├── tests/              # Test files
└── examples/           # Configuration examples
```

## Testing

Before submitting a pull request, run the test suite:

```bash
python tests/simple_test.py
```

Expected output:
```
✅ Files created correctly
✅ Detected: React, Tailwind CSS, TypeScript
✅ .env in gitignore (would be filtered)
🎉 ALL CORE TESTS PASSED!
```

## Key Components

### ContextGatherer Class
- Scans codebase for file structure
- Detects code style (React, Vue, TypeScript, etc.)
- Filters sensitive files automatically
- Integrates with Git

### PromptGenerator Class
- Calls Gemini API
- Creates refined prompts
- Formats context appropriately

### CLI Interface
- Argument parsing with argparse
- Focus modes for specific areas
- Multiple output options
- User-friendly messages

## Security Guidelines

Always prioritize security when modifying:

1. **File Filtering**: Sensitive patterns to ignore:
   - `*.env*`, `*.pem`, `*id_rsa*`, `*.key`, `*.cert`, `*.p12`
   - Pattern files: `*secret*`, `*password*`, `*credentials*`

2. **Default Ignores**: Always ignore:
   - `node_modules`, `.git`, `__pycache__`, `venv`, `env`
   - Build directories: `dist`, `build`, `.next`, `out`, `target`
   - Hidden directories (starting with `.`)

3. **Gitignore Compliance**: Always respect `.gitignore` files

## Pull Request Process

1. **Fork and branch**: Create feature branch from main
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make changes**: Update code, tests, and docs as needed

3. **Test**: Run tests and verify nothing breaks
   ```bash
   python tests/simple_test.py
   python contextify.py "test request" --no-clipboard
   ```

4. **Document**: Update README or docs if adding features

5. **Commit**: Clear, concise commit messages
   ```bash
   git commit -m "Add: feature description"
   ```

6. **Push and PR**: Open pull request with description

## Feature Ideas

- [ ] Improved codebase style detection
- [ ] Additional language support (Go, Rust, etc.)
- [ ] Custom style detection patterns
- [ ] Output format options (Markdown, JSON)
- [ ] Batch processing multiple requests
- [ ] Local model integration (Ollama, etc.)
- [ ] Database schema detection

## Reporting Issues

Found a bug? Open an issue with:
- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Your environment (OS, Python version, etc.)
- Relevant code snippets

## Questions?

- Check existing issues first
- Read the documentation in `docs/`
- Review examples in `docs/EXAMPLES.md`
- Open a discussion for ideas

## License

By contributing, you agree your changes are released under the MIT License (see LICENSE file).

---

**Thank you for contributing to Contextify!** 🚀
