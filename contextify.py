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
from pathlib import Path
from typing import List, Dict, Set, Optional
import pyperclip

try:
    import google.generativeai as genai
except ImportError:
    print("Error: google-generativeai package not found.")
    print("Install it with: pip install google-generativeai")
    sys.exit(1)


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
    
    def __init__(self, root_path: str = '.'):
        self.root = Path(root_path).resolve()
        self.gitignore_spec = self._load_gitignore()
        
    def _load_gitignore(self) -> Optional[pathspec.PathSpec]:
        """Load .gitignore patterns."""
        gitignore_path = self.root / '.gitignore'
        if gitignore_path.exists():
            with open(gitignore_path, 'r') as f:
                patterns = f.read().splitlines()
                # Add sensitive patterns
                patterns.extend(self.SENSITIVE_PATTERNS)
                return pathspec.PathSpec.from_lines('gitwildmatch', patterns)
        return pathspec.PathSpec.from_lines('gitwildmatch', self.SENSITIVE_PATTERNS)
    
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

    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash-latest')
    
    def generate_prompt(self, user_request: str, context: Dict) -> str:
        """Generate refined prompt using Gemini."""
        
        # Build context message
        context_parts = [
            "# Codebase Context\n",
            f"## Project Structure\n{context['file_tree']}\n",
        ]
        
        if context['style']:
            style_desc = []
            for key, value in context['style'].items():
                if value:
                    if isinstance(value, list):
                        style_desc.append(f"- {key.title()}: {', '.join(value)}")
                    else:
                        style_desc.append(f"- {key.title()}: {value}")
            
            if style_desc:
                context_parts.append("## Detected Code Style\n" + "\n".join(style_desc) + "\n")
        
        if context['files']:
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
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error generating prompt: {e}\n\nContext gathered:\n{full_context}"


def main():
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

Focus options: frontend, backend, database, config, tests
        """
    )
    
    parser.add_argument('request', help='Your coding request (e.g., "add dark mode")')
    parser.add_argument('--focus', choices=['frontend', 'backend', 'database', 'config', 'tests'],
                       help='Focus on specific part of codebase')
    parser.add_argument('--changed', action='store_true',
                       help='Only include files changed in git')
    parser.add_argument('--output', '-o', help='Save to file instead of clipboard')
    parser.add_argument('--max-files', type=int, default=30,
                       help='Maximum number of files to include (default: 30)')
    parser.add_argument('--no-clipboard', action='store_true',
                       help='Do not copy to clipboard')
    
    args = parser.parse_args()
    
    # Check for API key
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        print("❌ Error: GEMINI_API_KEY environment variable not set")
        print("\nGet your API key from: https://makersuite.google.com/app/apikey")
        print("Then set it with: export GEMINI_API_KEY='your-key-here'")
        sys.exit(1)
    
    print("🔍 Gathering context...")
    
    # Gather context
    gatherer = ContextGatherer()
    
    context = {
        'file_tree': gatherer.gather_file_tree(args.focus, args.changed),
        'style': gatherer.analyze_codebase_style(),
        'files': gatherer.get_important_files(args.focus, args.changed, args.max_files)
    }
    
    print(f"✅ Found {len(context['files'])} relevant files")
    print(f"🎨 Detected: {context['style'].get('language', 'unknown')} with {context['style'].get('framework', 'no framework')}")
    
    print("\n🤖 Generating refined prompt with Gemini...")
    
    # Generate prompt
    generator = PromptGenerator(api_key)
    refined_prompt = generator.generate_prompt(args.request, context)
    
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
