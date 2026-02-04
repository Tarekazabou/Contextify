#!/usr/bin/env python3
"""
Contextify - The Context Bridge for AI Coding Assistants
Generates detailed, context-aware prompts for GitHub Copilot and other AI coders.
"""

import os
import sys
import json
import re
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
        """Get files changed in git (uncommitted vs HEAD)."""
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

    def get_git_activity_files(self) -> Set[Path]:
        """Get recently modified files (staged + unstaged)."""
        files = set()
        try:
            unstaged = subprocess.run(
                ['git', 'diff', '--name-only'],
                cwd=self.root,
                capture_output=True,
                text=True
            )
            if unstaged.returncode == 0:
                files.update({self.root / f for f in unstaged.stdout.strip().split('\n') if f})
        except:
            pass

        try:
            staged = subprocess.run(
                ['git', 'diff', '--name-only', '--cached'],
                cwd=self.root,
                capture_output=True,
                text=True
            )
            if staged.returncode == 0:
                files.update({self.root / f for f in staged.stdout.strip().split('\n') if f})
        except:
            pass

        return files
    
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

    def get_tech_constraints(self) -> List[str]:
        """Derive strict environment constraints from config files."""
        constraints = []

        package_json = self.root / 'package.json'
        if package_json.exists():
            try:
                with open(package_json) as f:
                    data = json.load(f)
                    deps = {**data.get('dependencies', {}), **data.get('devDependencies', {})}

                    def add_dep_constraint(name: str, label: str):
                        if name in deps:
                            constraints.append(f"{label}: {deps[name]}")

                    add_dep_constraint('next', 'Framework (Next.js)')
                    add_dep_constraint('react', 'Library (React)')
                    add_dep_constraint('tailwindcss', 'Styling (Tailwind CSS)')
                    add_dep_constraint('typescript', 'Language (TypeScript)')

                    next_ver = deps.get('next')
                    tailwind_ver = deps.get('tailwindcss')
                    ts_ver = deps.get('typescript')

                    next_major = self._parse_major_version(next_ver)
                    if next_major and next_major < 13:
                        constraints.append("Do NOT use Next 13+ App Router features")

                    tailwind_major = self._parse_major_version(tailwind_ver)
                    if tailwind_major and tailwind_major < 3:
                        constraints.append("Do NOT use Tailwind v3-only features (e.g., arbitrary values)")

                    if ts_ver:
                        constraints.append("Avoid TypeScript features beyond the installed version")
            except:
                pass

        requirements = self.root / 'requirements.txt'
        if requirements.exists():
            try:
                with open(requirements) as f:
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith('#'):
                            continue
                        if 'django' in line.lower():
                            constraints.append(f"Framework (Django): {line}")
                        if 'flask' in line.lower():
                            constraints.append(f"Framework (Flask): {line}")
            except:
                pass

        pyproject = self.root / 'pyproject.toml'
        if pyproject.exists():
            try:
                with open(pyproject) as f:
                    content = f.read()
                match = re.search(r"requires-python\s*=\s*['\"]([^'\"]+)['\"]", content)
                if match:
                    constraints.append(f"Python Version: {match.group(1)}")
            except:
                pass

        return constraints

    def get_negative_constraints(self, target_file: Optional[str], scope_function: Optional[str] = None) -> List[str]:
        """Generate negative constraints based on file patterns and scope."""
        constraints = []

        if target_file:
            path = target_file.replace('\\', '/').lower()
            if any(token in path for token in ['test', 'spec', '__tests__', 'e2e']):
                constraints.append("Test file: Do NOT change the testing library or framework")
            if any(token in path for token in ['legacy', 'deprecated', 'old']):
                constraints.append("Legacy file: Do NOT refactor names or restructure existing code")

        if scope_function:
            constraints.append(f"Scope: ONLY modify the `{scope_function}` function. Leave the rest unchanged")

        return constraints

    def _parse_major_version(self, version: Optional[str]) -> Optional[int]:
        if not version:
            return None
        match = re.search(r"(\d+)", str(version))
        if not match:
            return None
        try:
            return int(match.group(1))
        except:
            return None
    
    def get_important_files(self, focus: Optional[str] = None,
                           changed_only: bool = False,
                           max_files: int = 30,
                           target_file: Optional[str] = None,
                           tree_shake: bool = False,
                           git_aware_files: Optional[Set[Path]] = None,
                           skeleton_context: bool = False) -> List[Dict[str, str]]:
        """Get important file contents with optional tree-shaking and skeletonization."""
        files_data = []
        changed_files = self.get_changed_files() if changed_only else set()
        focus_dirs = self.FOCUS_MAPPINGS.get(focus, []) if focus else []
        git_aware_files = git_aware_files or set()

        selected_files: List[Path] = []
        selected_set: Set[Path] = set()

        def add_file(path: Path):
            if not path or not path.exists():
                return
            if self._should_ignore(path):
                return
            if path in selected_set:
                return
            selected_files.append(path)
            selected_set.add(path)

        # Priority 1: Config files
        for config in self.CONFIG_FILES:
            config_path = self.root / config
            if config_path.exists():
                add_file(config_path)

        # Priority 2: Target file and direct dependencies
        target_path = self._resolve_target_path(target_file) if target_file else None
        if target_path:
            add_file(target_path)
            if tree_shake:
                for dep in self._get_direct_dependencies(target_path):
                    add_file(dep)

        # Priority 3: Git-aware files
        for file in git_aware_files:
            add_file(file)

        if not tree_shake:
            # Priority 4: Changed files
            if changed_only and changed_files:
                for file in list(changed_files)[:max_files]:
                    if file.suffix in self.CODE_EXTENSIONS:
                        add_file(file)

            # Priority 5: Important code files
            if len(selected_files) < max_files:
                for ext in self.CODE_EXTENSIONS:
                    for file in self.root.rglob(f'*{ext}'):
                        if len(selected_files) >= max_files:
                            break

                        if self._should_ignore(file):
                            continue

                        if focus_dirs:
                            rel = file.relative_to(self.root)
                            if not any(str(rel).startswith(d) for d in focus_dirs):
                                continue

                        # Prioritize smaller, important-looking files
                        if file.stat().st_size < 50000:  # < 50KB
                            add_file(file)

        # Build final file list with optional skeletonization
        for file in selected_files[:max_files]:
            is_target = target_path and file.resolve() == target_path.resolve()
            files_data.append(self._read_file(file, skeletonize=(skeleton_context and not is_target)))

        return files_data[:max_files]
    
    def _read_file(self, path: Path, skeletonize: bool = False) -> Dict[str, str]:
        """Read file content safely, optionally skeletonizing implementation details."""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
                relative = path.relative_to(self.root)
                if skeletonize and path.suffix in self.CODE_EXTENSIONS:
                    content = self._skeletonize_content(path, content)
                return {
                    'path': str(relative),
                    'content': content
                }
        except Exception as e:
            return {
                'path': str(path.relative_to(self.root)),
                'content': f'[Error reading file: {e}]'
            }

    def _resolve_target_path(self, target_file: Optional[str]) -> Optional[Path]:
        if not target_file:
            return None
        candidate = Path(target_file)
        if not candidate.is_absolute():
            candidate = (self.root / candidate).resolve()
        if candidate.exists() and candidate.is_file():
            return candidate
        return None

    def _get_direct_dependencies(self, file_path: Path) -> Set[Path]:
        """Get direct import dependencies for a file (tree-shake)."""
        deps: Set[Path] = set()
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except:
            return deps

        suffix = file_path.suffix.lower()
        if suffix in {'.js', '.jsx', '.ts', '.tsx', '.mjs', '.cjs', '.vue', '.svelte'}:
            import_paths = set()
            import_paths.update(re.findall(r"from\s+['\"](.*?)['\"]", content))
            import_paths.update(re.findall(r"require\(['\"](.*?)['\"]\)", content))
            import_paths.update(re.findall(r"import\s+['\"](.*?)['\"]", content))
            for imp in import_paths:
                resolved = self._resolve_relative_import(file_path, imp)
                if resolved:
                    deps.add(resolved)

        if suffix == '.py':
            for imp in re.findall(r"^\s*from\s+([\w\.]+)\s+import\s+", content, re.MULTILINE):
                resolved = self._resolve_python_import(file_path, imp)
                if resolved:
                    deps.add(resolved)
            for imp in re.findall(r"^\s*import\s+([\w\.]+)", content, re.MULTILINE):
                resolved = self._resolve_python_import(file_path, imp)
                if resolved:
                    deps.add(resolved)

        return deps

    def _resolve_relative_import(self, base_file: Path, import_path: str) -> Optional[Path]:
        if not import_path.startswith('.'):
            return None
        base_dir = base_file.parent
        candidate = (base_dir / import_path).resolve()
        extensions = ['.ts', '.tsx', '.js', '.jsx', '.mjs', '.cjs', '.json', '.css', '.scss', '.sass', '.less']

        if candidate.is_file():
            return candidate

        for ext in extensions:
            candidate_with_ext = Path(str(candidate)).with_suffix(ext)
            if candidate_with_ext.exists():
                return candidate_with_ext

        if candidate.is_dir():
            for ext in extensions:
                index_file = candidate / f'index{ext}'
                if index_file.exists():
                    return index_file

        return None

    def _resolve_python_import(self, base_file: Path, module_path: str) -> Optional[Path]:
        if module_path.startswith('.'):
            module_path = module_path.lstrip('.')
        parts = module_path.split('.')
        rel_path = Path(*parts)
        candidate = (self.root / rel_path).resolve()

        if (candidate.with_suffix('.py')).exists():
            return candidate.with_suffix('.py')
        if (candidate / '__init__.py').exists():
            return candidate / '__init__.py'
        return None

    def _skeletonize_content(self, path: Path, content: str) -> str:
        suffix = path.suffix.lower()
        if suffix == '.py':
            return self._skeletonize_python(content)
        if suffix in {'.js', '.jsx', '.ts', '.tsx', '.mjs', '.cjs', '.vue', '.svelte'}:
            return self._skeletonize_js_ts(content)
        return content

    def _skeletonize_python(self, content: str) -> str:
        lines = content.splitlines()
        output = []
        for line in lines:
            stripped = line.strip()
            if stripped.startswith('import ') or stripped.startswith('from '):
                output.append(line)
            elif stripped.startswith('@'):
                output.append(line)
            elif stripped.startswith('class ') or stripped.startswith('def '):
                output.append(line)
                indent = re.match(r"^(\s*)", line).group(1)
                output.append(f"{indent}    ...")
        return "\n".join(output) if output else "# Skeleton unavailable"

    def _skeletonize_js_ts(self, content: str) -> str:
        lines = content.splitlines()
        output = []
        skip_depth = 0

        signature_patterns = [
            r"^(export\s+)?(async\s+)?function\s+\w+\s*\(",
            r"^(export\s+)?(const|let|var)\s+\w+\s*=\s*(async\s*)?\(",
            r"^(export\s+)?class\s+\w+",
            r"^(public|private|protected)?\s*\w+\s*\(.*\)\s*:\s*",
            r"^constructor\s*\(",
            r"^(export\s+)?type\s+\w+\s*=",
            r"^(export\s+)?interface\s+\w+",
            r"^(export\s+)?enum\s+\w+",
        ]

        def is_signature(line: str) -> bool:
            stripped = line.strip()
            return any(re.match(pat, stripped) for pat in signature_patterns)

        for line in lines:
            stripped = line.strip()

            if stripped.startswith('import ') or (stripped.startswith('export ') and 'from' in stripped):
                output.append(line)
                continue

            if is_signature(line):
                sig = line
                if '{' in sig:
                    sig = sig.split('{')[0].rstrip() + ';'
                elif sig.rstrip().endswith(')'):
                    sig = sig.rstrip() + ';'
                output.append(sig)
                if '{' in line:
                    skip_depth += line.count('{') - line.count('}')
                continue

            if skip_depth > 0:
                skip_depth += line.count('{') - line.count('}')
                continue

        return "\n".join(output) if output else "// Skeleton unavailable"


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
        
        if context.get('git_clues'):
            clues = "\n".join([f"- {p}" for p in context['git_clues']])
            context_parts.append("## Contextual Clues (Git Activity)\n" + clues + "\n")

        if context.get('hard_lock'):
            constraints = "\n".join([f"- {c}" for c in context['hard_lock']])
            context_parts.append("## Environment Constraints (Strict)\n" + constraints + "\n")

        if context.get('negative_constraints'):
            negatives = "\n".join([f"- {c}" for c in context['negative_constraints']])
            context_parts.append("## Negative Constraints\n" + negatives + "\n")

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
    contextify "fix bug in checkout" --target src/Checkout.tsx --tree-shake --skeleton-context
    contextify "fix the build error" --git-aware
  contextify "refactor auth" --output prompt.md
  contextify "my request" --model-name gemini-2.5-flash
  contextify "my request" --temperature 0.3
  contextify "my request" --no-tree
  contextify "my request" --no-style
  contextify "my request" --exclude-patterns "test_*.py" "temp_dir/"
  contextify "my request" --simple
  contextify "my request" --detailed
  contextify "my request" --dry-run
    contextify "update totals" --target src/utils/calc.ts --scope-function calculateTotal

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
    parser.add_argument('--target', type=str,
                       help='Primary file to include fully (used for tree-shaking and skeleton context)')
    parser.add_argument('--tree-shake', action='store_true',
                       help='Include only direct dependencies of --target (minimal context)')
    parser.add_argument('--skeleton-context', action='store_true',
                       help='Strip implementations from non-target files (signatures only)')
    parser.add_argument('--git-aware', action='store_true',
                       help='Include recently modified git files and inject intent clue')
    parser.add_argument('--hard-lock', action='store_true',
                       help='Inject strict tech stack constraints from config files')
    parser.add_argument('--no-negative-context', action='store_true',
                       help='Disable negative constraints injection')
    parser.add_argument('--scope-function', type=str,
                       help='Limit changes to a specific function name (negative constraint)')
    
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

    if args.tree_shake and not args.target:
        parser.error("--tree-shake requires --target")
    
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

    target_path = gatherer._resolve_target_path(args.target) if args.target else None
    if args.target and not target_path:
        parser.error("--target must point to an existing file relative to the project root")

    git_aware_files = gatherer.get_git_activity_files() if args.git_aware else set()
    git_clues = sorted([str(p.relative_to(gatherer.root)) for p in git_aware_files if p.exists()])

    hard_lock = gatherer.get_tech_constraints() if args.hard_lock else []
    negative_constraints = [] if args.no_negative_context else gatherer.get_negative_constraints(
        args.target, scope_function=args.scope_function
    )
    
    # Determine include_file_contents: simple mode excludes them, detailed (default) includes them
    include_file_contents = not args.simple  # True by default, False only if --simple is used
    
    context = {
        'file_tree': gatherer.gather_file_tree(args.focus, args.changed) if not args.no_tree else "File tree omitted by --no-tree flag.",
        'style': gatherer.analyze_codebase_style() if not args.no_style else {},
        'files': gatherer.get_important_files(
            args.focus,
            args.changed,
            args.max_files,
            target_file=args.target,
            tree_shake=args.tree_shake,
            git_aware_files=git_aware_files,
            skeleton_context=args.skeleton_context
        ),
        'no_tree': args.no_tree,
        'no_style': args.no_style,
        'git_clues': git_clues,
        'hard_lock': hard_lock,
        'negative_constraints': negative_constraints
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
        print(f"   - Target: {args.target or 'none'}")
        print(f"   - Tree-shake: {args.tree_shake}")
        print(f"   - Skeleton context: {args.skeleton_context}")
        print(f"   - Git-aware: {args.git_aware}")
        print(f"   - Hard-lock: {args.hard_lock}")
        print(f"   - Negative constraints: {not args.no_negative_context}")
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
