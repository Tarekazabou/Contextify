#!/usr/bin/env python3
"""
Contextify - The Context Bridge for AI Coding Assistants
Generates detailed, context-aware prompts for GitHub Copilot and other AI coders.
"""

import os
import sys
import json
import subprocess
import argparse
import pathspec
import threading
import time
from pathlib import Path
from typing import List, Dict, Set, Optional
import pyperclip

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

try:
    import google.generativeai as genai
except ImportError:
    print("Error: google-generativeai package not found.")
    print("Install it with: pip install google-generativeai")
    sys.exit(1)

# Version
__version__ = "1.1.0"


def load_environment():
    """Load .env file from current directory, script directory, or home directory."""
    if load_dotenv is None:
        # python-dotenv not installed, try manual loading
        env_paths = [
            Path('.') / '.env',
            Path(__file__).parent / '.env',
            Path.home() / '.contextify' / '.env',
        ]
        
        for env_path in env_paths:
            if env_path.exists():
                try:
                    with open(env_path, 'r') as f:
                        for line in f:
                            line = line.strip()
                            if line and not line.startswith('#') and '=' in line:
                                key, value = line.split('=', 1)
                                key = key.strip()
                                value = value.strip().strip('"').strip("'")
                                if key and value and key not in os.environ:
                                    os.environ[key] = value
                    return True
                except Exception:
                    pass
        return False
    else:
        # Use python-dotenv
        env_paths = [
            Path('.') / '.env',
            Path(__file__).parent / '.env',
            Path.home() / '.contextify' / '.env',
        ]
        
        for env_path in env_paths:
            if env_path.exists():
                load_dotenv(env_path)
                return True
        return False


class Spinner:
    """Simple CLI spinner for better UX."""
    
    def __init__(self, message="Processing"):
        self.message = message
        self.running = False
        self.thread = None
    
    def start(self):
        """Start the spinner animation."""
        self.running = True
        self.thread = threading.Thread(target=self._spin, daemon=True)
        self.thread.start()
    
    def _spin(self):
        """Internal method to animate spinner."""
        chars = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
        i = 0
        while self.running:
            sys.stdout.write(f"\r{chars[i % len(chars)]} {self.message}...")
            sys.stdout.flush()
            time.sleep(0.1)
            i += 1
    
    def stop(self, final_message=None):
        """Stop the spinner."""
        self.running = False
        if self.thread:
            self.thread.join()
        sys.stdout.write("\r" + " " * (len(self.message) + 10) + "\r")
        sys.stdout.flush()
        if final_message:
            print(final_message)


class ContextGatherer:
    """Intelligently gathers codebase context."""
    
    SENSITIVE_PATTERNS = [
        '*.env*', '*.pem', '*id_rsa*', '*.key', '*.cert', 
        '*secret*', '*password*', '*credentials*', '*.p12'
    ]
    
    FOCUS_MAPPINGS = {
        'frontend': ['src', 'components', 'pages', 'app', 'public', 'styles'],
        'backend': ['server', 'api', 'routes', 'controllers', 'services', 'models'],
        'database': ['prisma', 'migrations', 'schema', 'db', 'sql'],
        'config': ['config', 'webpack', 'vite', 'tsconfig', 'package.json'],
        'tests': ['test', 'tests', '__tests__', 'spec', 'e2e']
    }
    
    CODE_EXTENSIONS = {
        '.js', '.jsx', '.ts', '.tsx', '.py', '.java', '.cpp', '.c', '.h',
        '.cs', '.go', '.rs', '.rb', '.php', '.swift', '.kt', '.scala',
        '.html', '.css', '.scss', '.sass', '.less', '.vue', '.svelte'
    }
    
    CONFIG_FILES = {
        'package.json', 'tsconfig.json', 'vite.config.js', 'vite.config.ts',
        'next.config.js', 'tailwind.config.js', 'webpack.config.js',
        'Cargo.toml', 'go.mod', 'requirements.txt', 'Gemfile', 'pom.xml'
    }
    
    def __init__(self, root_path: str = '.', exclude_cli_patterns: Optional[List[str]] = None):
        self.root = Path(root_path).resolve()
        self.exclude_cli_patterns = exclude_cli_patterns or []
        self.gitignore_spec = self._load_gitignore()
        
    def _load_gitignore(self) -> Optional[pathspec.PathSpec]:
        """Load .gitignore patterns."""
        gitignore_path = self.root / '.gitignore'
        if gitignore_path.exists():
            with open(gitignore_path, 'r') as f:
                patterns = f.read().splitlines()
                # Add sensitive patterns
                patterns.extend(self.SENSITIVE_PATTERNS)
                if self.exclude_cli_patterns:
                    patterns.extend(self.exclude_cli_patterns)
                return pathspec.PathSpec.from_lines('gitwildmatch', patterns)
        patterns = list(self.SENSITIVE_PATTERNS)
        if self.exclude_cli_patterns:
            patterns.extend(self.exclude_cli_patterns)
        return pathspec.PathSpec.from_lines('gitwildmatch', patterns)
    
    def _should_ignore(self, path: Path) -> bool:
        """Check if file should be ignored."""
        relative = path.relative_to(self.root)
        
        # Always ignore common dirs
        ignore_dirs = {'node_modules', '.git', '__pycache__', 'venv', 'env', 
                      'dist', 'build', '.next', 'out', 'target'}
        
        for part in relative.parts:
            if part in ignore_dirs or part.startswith('.'):
                return True
        
        # Check gitignore
        if self.gitignore_spec and self.gitignore_spec.match_file(str(relative)):
            return True
            
        return False
    
    def get_changed_files(self) -> Set[Path]:
        """Get files changed in git (uncommitted)."""
        try:
            result = subprocess.run(
                ['git', 'diff', '--name-only', 'HEAD'],
                cwd=self.root,
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                files = result.stdout.strip().split('\n')
                return {self.root / f for f in files if f}
        except:
            pass
        return set()
    
    def gather_file_tree(self, focus: Optional[str] = None, 
                        changed_only: bool = False) -> str:
        """Generate a visual file tree."""
        lines = [f"📁 {self.root.name}/"]
        
        focus_dirs = self.FOCUS_MAPPINGS.get(focus, []) if focus else []
        changed_files = self.get_changed_files() if changed_only else set()
        
        def walk_dir(path: Path, prefix: str = "", depth: int = 0):
            if depth > 4:  # Limit depth
                return
                
            try:
                items = sorted(path.iterdir(), key=lambda x: (not x.is_dir(), x.name))
            except PermissionError:
                return
            
            for i, item in enumerate(items):
                if self._should_ignore(item):
                    continue
                
                # Skip if focusing and not in focus dirs
                if focus_dirs:
                    rel = item.relative_to(self.root)
                    if not any(str(rel).startswith(d) for d in focus_dirs):
                        continue
                
                # Skip if changed_only and not changed
                if changed_only and changed_files and item not in changed_files:
                    continue
                
                is_last = i == len(items) - 1
                current = "└── " if is_last else "├── "
                extension = "    " if is_last else "│   "
                
                marker = "📁" if item.is_dir() else "📄"
                lines.append(f"{prefix}{current}{marker} {item.name}")
                
                if item.is_dir():
                    walk_dir(item, prefix + extension, depth + 1)
        
        walk_dir(self.root)
        return "\n".join(lines)
    
    def analyze_codebase_style(self) -> Dict[str, any]:
        """Analyze codebase to determine coding style."""
        style = {
            'language': 'unknown',
            'framework': None,
            'styling': None,
            'validation': None,
            'testing': None,
            'patterns': []
        }
        
        # Check package.json for JS/TS projects
        package_json = self.root / 'package.json'
        if package_json.exists():
            try:
                with open(package_json) as f:
                    data = json.load(f)
                    deps = {**data.get('dependencies', {}), 
                           **data.get('devDependencies', {})}
                    
                    style['language'] = 'typescript' if 'typescript' in deps else 'javascript'
                    
                    if 'react' in deps:
                        style['framework'] = 'React'
                    elif 'vue' in deps:
                        style['framework'] = 'Vue'
                    elif 'next' in deps:
                        style['framework'] = 'Next.js'
                    elif '@angular/core' in deps:
                        style['framework'] = 'Angular'
                    
                    if 'tailwindcss' in deps:
                        style['styling'] = 'Tailwind CSS'
                    elif 'styled-components' in deps:
                        style['styling'] = 'styled-components'
                    
                    if 'zod' in deps:
                        style['validation'] = 'Zod'
                    elif 'yup' in deps:
                        style['validation'] = 'Yup'
                    
                    if 'jest' in deps or 'vitest' in deps:
                        style['testing'] = 'jest' if 'jest' in deps else 'vitest'
            except:
                pass
        
        # Check for Python
        if (self.root / 'requirements.txt').exists() or (self.root / 'pyproject.toml').exists():
            style['language'] = 'python'
        
        # Detect patterns by scanning a few files
        sample_files = []
        for ext in ['.ts', '.tsx', '.js', '.jsx']:
            sample_files.extend(list(self.root.rglob(f'*{ext}'))[:5])
        
        arrow_functions = 0
        function_keywords = 0
        
        for file in sample_files[:10]:
            if self._should_ignore(file):
                continue
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    arrow_functions += content.count('=>')
                    function_keywords += content.count('function ')
            except:
                continue
        
        if arrow_functions > function_keywords * 2:
            style['patterns'].append('Prefers arrow functions')
        
        return style
    
    def get_important_files(self, focus: Optional[str] = None, 
                           changed_only: bool = False,
                           max_files: int = 30) -> List[Dict[str, str]]:
        """Get important file contents."""
        files_data = []
        changed_files = self.get_changed_files() if changed_only else set()
        focus_dirs = self.FOCUS_MAPPINGS.get(focus, []) if focus else []
        
        # Priority 1: Config files
        for config in self.CONFIG_FILES:
            config_path = self.root / config
            if config_path.exists():
                files_data.append(self._read_file(config_path))
        
        # Priority 2: Changed files
        if changed_only and changed_files:
            for file in list(changed_files)[:max_files]:
                if file.suffix in self.CODE_EXTENSIONS:
                    files_data.append(self._read_file(file))
        
        # Priority 3: Important code files
        if len(files_data) < max_files:
            for ext in self.CODE_EXTENSIONS:
                for file in self.root.rglob(f'*{ext}'):
                    if len(files_data) >= max_files:
                        break
                    
                    if self._should_ignore(file):
                        continue
                    
                    if focus_dirs:
                        rel = file.relative_to(self.root)
                        if not any(str(rel).startswith(d) for d in focus_dirs):
                            continue
                    
                    # Prioritize smaller, important-looking files
                    if file.stat().st_size < 50000:  # < 50KB
                        files_data.append(self._read_file(file))
        
        return files_data[:max_files]
    
    def _read_file(self, path: Path) -> Dict[str, str]:
        """Read file content safely."""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
                relative = path.relative_to(self.root)
                return {
                    'path': str(relative),
                    'content': content
                }
        except Exception as e:
            return {
                'path': str(path.relative_to(self.root)),
                'content': f'[Error reading file: {e}]'
            }


class PromptGenerator:
    """Generates refined prompts using Gemini."""
    
    SYSTEM_PROMPT = """You are an expert Prompt Engineer for AI Coding Assistants (GitHub Copilot, Cursor, etc.).

Your goal is to take a vague user request and the provided codebase context, and write a highly detailed, 
perfect prompt that the user can paste into their AI coding assistant to get working code on the first try.

IMPORTANT: Do not write the code yourself; write the prompt FOR the code.

The prompt you generate should:
1. Act as instructions for an AI coder (e.g., "Act as a Senior React Developer...")
2. Include all relevant context from the codebase
3. Reference specific files, interfaces, and components
4. Match the existing code style and patterns
5. Be specific about requirements and constraints
6. Include any relevant code snippets inline for reference

Format your response as a complete, copy-paste ready prompt."""

    def __init__(self, api_key: str, model_name: str = 'gemini-2.5-flash', temperature: float = 0.7):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
        self.temperature = temperature
    
    def generate_prompt(self, user_request: str, context: Dict, include_file_contents: bool = True) -> str:
        """Generate refined prompt using Gemini."""
        
        # Build context message
        context_parts = [
            "# Codebase Context\n",
        ]

        if not context.get('no_tree'):
            context_parts.append(f"## Project Structure\n{context['file_tree']}\n")
        
        if context.get('style') and not context.get('no_style'):
            style_desc = []
            for key, value in context['style'].items():
                if value:
                    if isinstance(value, list):
                        style_desc.append(f"- {key.title()}: {', '.join(value)}")
                    else:
                        style_desc.append(f"- {key.title()}: {value}")
            
            if style_desc:
                context_parts.append("## Detected Code Style\n" + "\n".join(style_desc) + "\n")
        
        if include_file_contents and context['files']:
            context_parts.append(f"\n## Relevant Files ({len(context['files'])} files)\n")
            for file_data in context['files']:
                context_parts.append(f"\n### {file_data['path']}\n```\n{file_data['content']}\n```\n")
        
        full_context = "\n".join(context_parts)
        
        # Generate prompt
        prompt = f"""{self.SYSTEM_PROMPT}

User Request: "{user_request}"

{full_context}

Now generate a detailed prompt for an AI coding assistant that will help them implement this request perfectly."""

        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(temperature=self.temperature)
            )
            return response.text
        except Exception as e:
            return f"Error generating prompt: {e}\n\nContext gathered:\n{full_context}"


def main():
    # Load environment variables from .env files
    load_environment()
    
    parser = argparse.ArgumentParser(
        description='Contextify - Generate context-aware prompts for AI coding assistants',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  contextify "add a dark mode toggle"
  contextify "create a user profile card" --focus frontend
  contextify "add database migration for posts" --focus database
  contextify "fix the bug" --changed
  contextify "refactor auth" --output prompt.md
  contextify "my request" --model-name gemini-2.5-flash
  contextify "my request" --temperature 0.3
  contextify "my request" --no-tree
  contextify "my request" --no-style
  contextify "my request" --exclude-patterns "test_*.py" "temp_dir/"
  contextify "my request" --simple
  contextify "my request" --detailed
  contextify "my request" --dry-run

Focus options: frontend, backend, database, config, tests
Detail options: -s/--simple (no code), -d/--detailed (with code, default)
        """
    )
    
    parser.add_argument('request', help='Your coding request (e.g., "add dark mode")')
    parser.add_argument('--version', '-v', action='version', version=f'%(prog)s {__version__}')
    parser.add_argument('--focus', choices=['frontend', 'backend', 'database', 'config', 'tests'],
                       help='Focus on specific part of codebase')
    parser.add_argument('--changed', action='store_true',
                       help='Only include files changed in git')
    parser.add_argument('--output', '-o', help='Save to file instead of clipboard')
    parser.add_argument('--max-files', type=int, default=30,
                       help='Maximum number of files to include (default: 30)')
    parser.add_argument('--no-clipboard', action='store_true',
                       help='Do not copy to clipboard')
    parser.add_argument('--model-name', type=str, default='gemini-2.5-flash',
                       help="Specify the generative AI model to use (default: 'gemini-2.5-flash')")
    parser.add_argument('--temperature', type=float, default=0.7, metavar='[0.0-1.0]',
                       help='Controls randomness in generation; lower values make output more deterministic (default: 0.7)')
    parser.add_argument('--no-tree', action='store_true',
                       help='Do not include the file tree in the generated prompt')
    parser.add_argument('--no-style', action='store_true',
                       help='Do not include the detected code style in the generated prompt')
    parser.add_argument('--exclude-patterns', type=str, nargs='*', default=[],
                       help='Glob patterns for files/directories to explicitly exclude from context gathering (e.g., "temp/*", "docs/")')
    
    # Add mutually exclusive group for detail level
    detail_group = parser.add_mutually_exclusive_group()
    detail_group.add_argument('-s', '--simple', action='store_true',
                              help='Generate simple paragraph prompt without code details')
    detail_group.add_argument('-d', '--detailed', action='store_true',
                              help='Generate detailed prompt with code suggestions (default)')
    parser.add_argument('--dry-run', action='store_true',
                       help='Preview gathered context without calling AI (useful for debugging)')
    
    args = parser.parse_args()

    if not 0.0 <= args.temperature <= 1.0:
        parser.error("--temperature must be between 0.0 and 1.0")
    
    # Check for API key
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key and not args.dry_run:
        print("❌ Error: GEMINI_API_KEY environment variable not set")
        print("\nGet your API key from: https://makersuite.google.com/app/apikey")
        print("Then set it with: export GEMINI_API_KEY='your-key-here'")
        print("\nOr create a .env file with: GEMINI_API_KEY=your-key-here")
        sys.exit(1)
    
    spinner = Spinner("Gathering context")
    spinner.start()
    
    # Gather context
    gatherer = ContextGatherer(exclude_cli_patterns=args.exclude_patterns)
    
    # Determine include_file_contents: simple mode excludes them, detailed (default) includes them
    include_file_contents = not args.simple  # True by default, False only if --simple is used
    
    context = {
        'file_tree': gatherer.gather_file_tree(args.focus, args.changed) if not args.no_tree else "File tree omitted by --no-tree flag.",
        'style': gatherer.analyze_codebase_style() if not args.no_style else {},
        'files': gatherer.get_important_files(args.focus, args.changed, args.max_files),
        'no_tree': args.no_tree,
        'no_style': args.no_style
    }
    
    spinner.stop()
    
    detail_level = "simple (no code)" if args.simple else "detailed (with code)"
    print(f"✅ Found {len(context['files'])} relevant files")
    if not args.no_style:
        print(f"🎨 Detected: {context['style'].get('language', 'unknown')} with {context['style'].get('framework', 'no framework')}")
    
    # Handle dry-run mode
    if args.dry_run:
        print("\n" + "="*60)
        print("🔍 DRY RUN - Context Preview")
        print("="*60)
        
        if not args.no_tree:
            print(f"\n📁 File Tree:\n{context['file_tree']}")
        
        if not args.no_style and context['style']:
            print(f"\n🎨 Code Style:")
            for key, value in context['style'].items():
                if value:
                    if isinstance(value, list):
                        print(f"   - {key.title()}: {', '.join(value)}")
                    else:
                        print(f"   - {key.title()}: {value}")
        
        print(f"\n📄 Files to include ({len(context['files'])}):")
        for i, f in enumerate(context['files'][:10], 1):
            print(f"   {i}. {f['path']}")
        if len(context['files']) > 10:
            print(f"   ... and {len(context['files']) - 10} more")
        
        print(f"\n⚙️  Settings:")
        print(f"   - Detail level: {detail_level}")
        print(f"   - Focus: {args.focus or 'all'}")
        print(f"   - Model: {args.model_name}")
        print(f"   - Temperature: {args.temperature}")
        print("="*60)
        sys.exit(0)
    
    spinner2 = Spinner(f"Generating refined prompt with Gemini ({args.model_name}, temperature={args.temperature}, {detail_level})")
    spinner2.start()
    
    # Generate prompt
    generator = PromptGenerator(api_key, model_name=args.model_name, temperature=args.temperature)
    refined_prompt = generator.generate_prompt(args.request, context, include_file_contents=include_file_contents)
    
    spinner2.stop()
    
    # Output
    if args.output:
        output_path = Path(args.output)
        with open(output_path, 'w') as f:
            f.write(refined_prompt)
        print(f"✅ Prompt saved to: {output_path}")
    
    if not args.no_clipboard:
        try:
            pyperclip.copy(refined_prompt)
            print("📋 Prompt copied to clipboard!")
        except:
            print("⚠️  Could not copy to clipboard (pyperclip not available)")
            if not args.output:
                print("\n" + "="*80)
                print(refined_prompt)
                print("="*80)
    
    if not args.output and args.no_clipboard:
        print("\n" + "="*80)
        print(refined_prompt)
        print("="*80)
    
    print("\n✨ Done! Paste the prompt into your AI coding assistant.")


if __name__ == '__main__':
    main()
