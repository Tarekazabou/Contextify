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
import requests
import urllib.parse
from pathlib import Path
from typing import List, Dict, Set, Optional
import pyperclip

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

try:
    import google.genai as genai
except ImportError:
    print("Error: google-genai package not found.")
    print("Install it with: pip install google-genai")
    sys.exit(1)

try:
    import jwt
except ImportError:
    jwt = None

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
    """Simple CLI spinner for better UX - simplified to avoid threading issues"""
    
    def __init__(self, message="Processing"):
        self.message = message
        self.running = False
    
    def start(self):
        """Start the spinner animation."""
        self.running = True
        # Simplified: don't use threading to avoid deadlocks
        print(f"  {self.message}...", end=' ', flush=True)
    
    def stop(self, final_message=None):
        """Stop the spinner."""
        self.running = False
        if final_message:
            print(final_message)
        else:
            print("done!")


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
        lines = [f"[DIR] {self.root.name}/"]
        
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
                current = "`-- " if is_last else "|-- "
                extension = "    " if is_last else "|   "
                
                marker = "[D]" if item.is_dir() else "[F]"
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
                import itertools
                for ext in self.CODE_EXTENSIONS:
                    # Use itertools.islice to limit the search results
                    files_found = 0
                    max_files_per_ext = max_files - len(selected_files)
                    
                    for file in self.root.rglob(f'*{ext}'):
                        if len(selected_files) >= max_files:
                            break
                        
                        files_found += 1
                        # Early exit if scanning too many files without finding enough matches
                        if files_found > max_files * 20:  # Scan up to 20x max_files before giving up
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


class PromptProvider:
    """Abstract base class for AI prompt generation providers."""
    
    def generate_prompt(self, system_prompt: str, user_request: str, context: str, temperature: float = 0.7) -> str:
        """Generate a refined prompt using the provider's model."""
        raise NotImplementedError


class GeminiProvider(PromptProvider):
    """Provider for Google Gemini API."""
    
    def __init__(self, api_key: str, model_name: str = 'gemini-2.5-flash'):
        self.api_key = api_key
        self.model_name = model_name
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
    
    def generate_prompt(self, system_prompt: str, user_request: str, context: str, temperature: float = 0.7) -> str:
        """Generate refined prompt using Gemini."""
        prompt = f"""{system_prompt}

User Request: "{user_request}"

{context}

Now generate a detailed prompt for an AI coding assistant that will help them implement this request perfectly."""

        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(temperature=temperature)
            )
            return response.text
        except Exception as e:
            return f"Error generating prompt: {e}\n\nContext gathered:\n{context}"


class GitHubCopilotProvider(PromptProvider):
    """Provider for GitHub Copilot API."""
    
    GITHUB_DEVICE_AUTH_URL = "https://github.com/login/device/code"
    GITHUB_DEVICE_TOKEN_URL = "https://github.com/login/oauth/access_token"
    COPILOT_TOKEN_URL = "https://api.github.com/copilot_internal/v2/token"
    COPILOT_API_URL = "https://api.individual.githubcopilot.com"
    
    def __init__(self, github_token: Optional[str] = None):
        self.github_token = github_token
        self.copilot_api_token = None
        if not github_token:
            self.github_token = self._authenticate()
        if not self.github_token:
            raise ValueError("GitHub Copilot authentication failed")
        # Exchange GitHub token for Copilot API token
        self.copilot_api_token = self._exchange_for_copilot_token()
    
    def _authenticate(self) -> Optional[str]:
        """Perform GitHub device flow authentication."""
        try:
            # Step 1: Request device code
            print("\n[GitHub Copilot Authentication]")
            print("=" * 60)
            
            device_response = requests.post(
                self.GITHUB_DEVICE_AUTH_URL,
                headers={"Accept": "application/json"},
                json={"client_id": "Iv1.b507a08c87ecfe98"},  # GitHub Copilot client ID
                timeout=10
            )
            device_response.raise_for_status()
            device_data = device_response.json()
            
            device_code = device_data.get("device_code")
            user_code = device_data.get("user_code")
            verification_uri = device_data.get("verification_uri")
            expires_in = device_data.get("expires_in", 900)
            interval = device_data.get("interval", 5)
            
            # Step 2: Display instructions to user
            print(f"\n1. Open: {verification_uri}")
            print(f"2. Enter code: {user_code}")
            print(f"3. Authorize the application")
            print(f"\nWaiting for authorization (expires in {expires_in}s)...")
            print("=" * 60 + "\n")
            
            # Step 3: Poll for access token
            import time
            poll_start = time.time()
            while time.time() - poll_start < expires_in:
                time.sleep(interval)
                
                token_response = requests.post(
                    self.GITHUB_DEVICE_TOKEN_URL,
                    headers={"Accept": "application/json"},
                    json={
                        "client_id": "Iv1.b507a08c87ecfe98",
                        "device_code": device_code,
                        "grant_type": "urn:ietf:params:oauth:grant-type:device_code"
                    },
                    timeout=10
                )
                token_response.raise_for_status()
                token_data = token_response.json()
                
                if "access_token" in token_data:
                    print("✓ Successfully authenticated with GitHub!")
                    return token_data["access_token"]
                
                error = token_data.get("error")
                if error in ["authorization_pending", "slow_down"]:
                    continue
                elif error in ["expired_token", "access_denied"]:
                    print(f"✗ Authentication failed: {error}")
                    return None
            
            print("✗ Authentication timeout")
            return None
            
        except requests.RequestException as e:
            print(f"✗ Network error during authentication: {e}")
            return None
        except Exception as e:
            print(f"✗ Authentication error: {e}")
            return None
    
    def _exchange_for_copilot_token(self) -> Optional[str]:
        """Exchange GitHub OAuth token for Copilot API token."""
        try:
            headers = {
                "Authorization": f"Bearer {self.github_token}",
                "Accept": "application/json",
                "User-Agent": "Contextify/1.2.0"
            }
            
            response = requests.get(
                self.COPILOT_TOKEN_URL,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                token = data.get("token")
                if token:
                    return token
                else:
                    print("✗ No token in Copilot API response")
                    return None
            elif response.status_code == 401:
                print("✗ GitHub token invalid or expired")
                return None
            elif response.status_code == 403:
                print("✗ GitHub account not authorized for Copilot (requires active subscription)")
                return None
            else:
                print(f"✗ Token exchange failed: {response.status_code}")
                return None
                
        except requests.RequestException as e:
            print(f"✗ Network error during token exchange: {e}")
            return None
        except Exception as e:
            print(f"✗ Token exchange error: {e}")
            return None
    
    def generate_prompt(self, system_prompt: str, user_request: str, context: str, temperature: float = 0.7) -> str:
        """Generate refined prompt using GitHub Copilot."""
        try:
            if not self.copilot_api_token:
                return "Error: GitHub Copilot authentication token not available. Re-run onboarding."
            
            prompt = f"""{system_prompt}

User Request: "{user_request}"

{context}

Now generate a detailed prompt for an AI coding assistant that will help them implement this request perfectly."""

            # Call Copilot API - use correct format for Copilot endpoint
            # Note: Copilot API requires specific IDE headers even for third-party tools
            headers = {
                "Authorization": f"Bearer {self.copilot_api_token}",
                "Accept": "application/json",
                "Content-Type": "application/json",
                "User-Agent": "Contextify/1.2.0",
                "Editor-Version": "vscode/1.85.0",  # Copilot recognizes VSCode
                "Editor-Plugin-Version": "copilot/1.150.0",  # Required format
            }
            
            # Copilot API uses a specific format
            payload = {
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                "temperature": temperature,
                "max_tokens": 4096,
                "model": "gpt-4"  # or whatever model the user has access to
            }
            
            response = requests.post(
                f"{self.COPILOT_API_URL}/chat/completions",
                headers=headers,
                json=payload,
                timeout=60
            )
            
            # Debug bad requests
            if response.status_code == 400:
                try:
                    error_data = response.json()
                    print(f"DEBUG: Copilot API error response: {error_data}")
                except:
                    print(f"DEBUG: Copilot API 400 response body: {response.text}")
            
            response.raise_for_status()
            result = response.json()
            
            if "choices" in result and len(result["choices"]) > 0:
                return result["choices"][0]["message"]["content"]
            else:
                return f"Unexpected response format from Copilot API: {result}"
                
        except requests.RequestException as e:
            return f"Error calling Copilot API: {e}\n\nContext gathered:\n{context}"
        except Exception as e:
            return f"Error generating prompt: {e}\n\nContext gathered:\n{context}"


class PromptGenerator:
    """Generates refined prompts using AI providers."""
    
    SYSTEM_PROMPT_DETAILED = """You are an expert Prompt Engineer for AI Coding Assistants (GitHub Copilot, Cursor, Claude, etc.).

Your goal is to transform a vague user request into a comprehensive, actionable prompt that produces working code on the first try.

CRITICAL: Do not write the code yourself. Craft an instruction for an AI assistant to write the code.

PROMPT STRUCTURE YOU MUST FOLLOW:

1. **ROLE & EXPERTISE** (Opening)
   - Define the persona (e.g., "Act as a Senior React Developer specializing in...")
   - Establish expertise level and domain
   - Set the tone (pragmatic, production-ready, etc.)

2. **CONTEXT & UNDERSTANDING** (Foundation)
   - Project structure and architecture
   - Technology stack and frameworks in use
   - Code style and patterns observed
   - Key files and their responsibilities
   - Any environment or deployment constraints

3. **THE TASK** (Clear & Specific)
   - Restate the user request in technical terms
   - Break it into logical steps
   - Specify inputs and outputs
   - Define success criteria
   - Highlight any gotchas or edge cases

4. **REQUIREMENTS & CONSTRAINTS** (Guardrails)
   - What MUST be done (strict requirements)
   - What MUST NOT be done (forbidden patterns)
   - Compatibility requirements
   - Performance or security considerations
   - Code style and naming conventions to follow

5. **REFERENCE CODE** (When Applicable)
   - Relevant file snippets showing patterns to follow
   - Examples of existing implementations
   - Anti-patterns to avoid
   - Key imports or dependencies already in use

6. **OUTPUT & VALIDATION** (Success Criteria)
   - Describe expected output format
   - Testing considerations
   - How to validate the solution works
   - Edge cases to handle

Generate the complete prompt as a cohesive, ready-to-copy instruction block. Ensure it's specific enough to guide implementation but open enough for creative solutions."""

    SYSTEM_PROMPT_SIMPLE = """You are an expert technical writer who translates coding requests into clear, concise instructions.

Transform the given user request into a focused prompt for an AI coding assistant. Keep it brief but comprehensive.

STRUCTURE:
1. Role: Define the developer persona in one sentence
2. Task: Restate the request clearly with key details
3. Context: 2-3 key points about the codebase (tech stack, patterns, constraints)
4. Requirements: Critical must-do and must-not-do items
5. Output: What the code should accomplish

Keep the entire prompt under 300 words. Be direct and actionable."""

    def __init__(self, provider: PromptProvider):
        self.provider = provider
    
    def generate_prompt(self, user_request: str, context: Dict, include_file_contents: bool = True, simple_mode: bool = False) -> str:
        """Generate refined prompt using the AI provider.
        
        Args:
            user_request: The original user request
            context: Dictionary with codebase context information
            include_file_contents: Whether to include file contents (detailed mode)
            simple_mode: Whether to use simple or detailed prompt template
        """
        
        # Build context message with smart organization
        context_parts = []
        
        # Project structure (always helpful)
        if not context.get('no_tree'):
            context_parts.append(f"## Project Structure\n{context['file_tree']}")
        
        # Technology & style (critical for code generation)
        if context.get('style') and not context.get('no_style'):
            style_parts = []
            style = context['style']
            
            # Organize style info logically
            if style.get('language'):
                style_parts.append(f"**Language**: {style['language']}")
            if style.get('framework'):
                style_parts.append(f"**Framework**: {style['framework']}")
            if style.get('styling'):
                style_parts.append(f"**Styling**: {style['styling']}")
            if style.get('validation'):
                style_parts.append(f"**Validation**: {style['validation']}")
            if style.get('testing'):
                style_parts.append(f"**Testing**: {style['testing']}")
            if style.get('patterns'):
                style_parts.append(f"**Patterns**: {', '.join(style['patterns'])}")
            
            if style_parts:
                context_parts.append("## Technology Stack\n" + " | ".join(style_parts))
        
        # Environment constraints (strict requirements)
        if context.get('hard_lock'):
            constraints = "\n".join([f"• {c}" for c in context['hard_lock']])
            context_parts.append(f"## Environment Constraints\n{constraints}")
        
        # Negative constraints (what NOT to do)
        if context.get('negative_constraints'):
            negatives = "\n".join([f"• {c}" for c in context['negative_constraints']])
            context_parts.append(f"## Constraints & Limitations\n{negatives}")
        
        # Git activity clues
        if context.get('git_clues'):
            clues = "\n".join([f"• {p}" for p in context['git_clues']])
            context_parts.append(f"## Recent Activity\n{clues}")
        
        # Relevant code (in detailed mode only)
        if include_file_contents and context['files']:
            file_preview = []
            
            # Show first few files inline, summarize rest
            shown_files = min(3, len(context['files']))
            for i, file_data in enumerate(context['files'][:shown_files]):
                # Limit displayed content to 500 chars per file
                content_preview = file_data['content'][:500]
                if len(file_data['content']) > 500:
                    content_preview += "\n... (truncated)"
                
                file_preview.append(f"### {file_data['path']}\n```\n{content_preview}\n```")
            
            if len(context['files']) > shown_files:
                file_preview.append(f"\n*+ {len(context['files']) - shown_files} more relevant files available*")
            
            context_parts.append("## Relevant Code Snippets\n" + "\n".join(file_preview))
        elif context['files']:
            # In simple mode, just list files
            file_list = "\n".join([f"• {f['path']}" for f in context['files']])
            context_parts.append(f"## Related Files ({len(context['files'])} total)\n{file_list}")
        
        full_context = "\n\n".join(context_parts)
        
        # Select appropriate system prompt
        system_prompt = self.SYSTEM_PROMPT_SIMPLE if simple_mode else self.SYSTEM_PROMPT_DETAILED
        
        # Build the user message
        user_message = f"""# User Request
{user_request}

# Codebase Context
{full_context}

Please generate the optimal prompt for an AI coding assistant to handle this request."""
        
        # Generate prompt using provider
        temperature = context.get('temperature', 0.7)
        
        # Override generate_prompt to use our custom message structure
        return self.provider.generate_prompt(
            system_prompt,
            user_message,
            "",  # Empty context since we built it into user_message
            temperature=temperature
        )


def analyze_project(cwd: str = ".") -> str:
    """Analyze project structure, workflow, and dataflow."""
    from pathlib import Path
    import os
    
    analysis = []
    analysis.append("="*70)
    analysis.append("PROJECT ANALYSIS REPORT")
    analysis.append("="*70)
    
    root = Path(cwd)
    
    # 1. Project Structure
    analysis.append("\n[1] PROJECT STRUCTURE")
    analysis.append("-" * 70)
    
    # Detect language/framework
    languages = set()
    frameworks = []
    
    if (root / "package.json").exists():
        languages.add("JavaScript/TypeScript")
        frameworks.append("Node.js")
    
    # Check Python first, then read requirements
    req_file = root / "requirements.txt"
    setup_py = root / "setup.py"
    pyproject = root / "pyproject.toml"
    
    if req_file.exists() or setup_py.exists() or pyproject.exists():
        languages.add("Python")
    
    if (root / "go.mod").exists():
        languages.add("Go")
    if (root / "Cargo.toml").exists():
        languages.add("Rust")
    if (root / "pom.xml").exists() or (root / "build.gradle").exists():
        languages.add("Java")
    
    # Detect frameworks - consolidated check
    if pyproject.exists():
        content = pyproject.read_text()
        if "django" in content.lower():
            frameworks.append("Django")
        if "flask" in content.lower():
            frameworks.append("Flask")
        if "fastapi" in content.lower():
            frameworks.append("FastAPI")
    
    if req_file.exists():
        content = req_file.read_text().lower()
        if "django" in content and "Django" not in frameworks:
            frameworks.append("Django")
        if "flask" in content and "Flask" not in frameworks:
            frameworks.append("Flask")
        if "fastapi" in content and "FastAPI" not in frameworks:
            frameworks.append("FastAPI")
    
    if setup_py.exists():
        content = setup_py.read_text().lower()
        if "django" in content and "Django" not in frameworks:
            frameworks.append("Django")
        if "flask" in content and "Flask" not in frameworks:
            frameworks.append("Flask")
    
    package_json = root / "package.json"
    if package_json.exists():
        content = package_json.read_text()
        if "react" in content.lower():
            frameworks.append("React")
        if "next" in content.lower():
            frameworks.append("Next.js")
        if "express" in content.lower():
            frameworks.append("Express")
        if "vue" in content.lower():
            frameworks.append("Vue")
    
    analysis.append(f"Languages: {', '.join(languages) if languages else 'Not detected'}")
    analysis.append(f"Frameworks: {', '.join(frameworks) if frameworks else 'None detected'}")
    
    # 2. Directory structure
    analysis.append("\n[2] DIRECTORY STRUCTURE")
    analysis.append("-" * 70)
    
    main_dirs = []
    for item in sorted(root.iterdir()):
        if item.is_dir() and not item.name.startswith('.') and item.name not in ['__pycache__', 'node_modules', 'venv', '.venv']:
            file_count = len(list(item.rglob('*')))
            main_dirs.append(f"  {item.name}/ ({file_count} items)")
    
    if main_dirs:
        for d in main_dirs[:15]:  # Limit to 15 dirs
            analysis.append(d)
        if len(main_dirs) > 15:
            analysis.append(f"  ... and {len(main_dirs) - 15} more directories")
    
    # 3. Entry points
    analysis.append("\n[3] ENTRY POINTS & MAIN FILES")
    analysis.append("-" * 70)
    
    entry_points = []
    skip_dirs = {'__pycache__', '.venv', 'venv', 'node_modules', '.git', 'site-packages'}
    
    # Python entry points
    for entry in ['main.py', '__main__.py', 'app.py', 'wsgi.py', 'asgi.py', 'manage.py']:
        if (root / entry).exists():
            entry_points.append(f"  - {entry}")
        # Check subdirs
        for p in root.rglob(entry):
            parts = p.relative_to(root).parts
            if not any(part in skip_dirs for part in parts):
                entry_points.append(f"  - {p.relative_to(root)}")
    
    # JavaScript entry points
    if package_json.exists():
        try:
            import json
            data = json.loads(package_json.read_text())
            if "main" in data:
                entry_points.append(f"  - {data['main']} (package.json main)")
            if "scripts" in data and "start" in data["scripts"]:
                entry_points.append(f"  - start script: {data['scripts']['start']}")
        except:
            pass
    
    if entry_points:
        for ep in entry_points[:10]:
            analysis.append(ep)
    else:
        analysis.append("  No obvious entry points found")
    
    # 4. Dependencies
    analysis.append("\n[4] DEPENDENCIES & IMPORTS")
    analysis.append("-" * 70)
    
    imports = {}
    skip_dirs = {'__pycache__', 'venv', '.venv', 'node_modules', '.git', 'site-packages'}
    
    # Scan Python files
    for py_file in root.rglob("*.py"):
        if any(part in skip_dirs for part in py_file.parts):
            continue
        try:
            content = py_file.read_text(errors='ignore')
            for line in content.split('\n'):
                line = line.strip()
                if line.startswith(('import ', 'from ')):
                    module = line.split()[1].split('.')[0]
                    if module:  # Skip empty modules
                        imports[module] = imports.get(module, 0) + 1
        except:
            pass
    
    if imports:
        analysis.append("Top imports (Python):")
        for mod, count in sorted(imports.items(), key=lambda x: -x[1])[:10]:
            if mod:  # Filter empty
                analysis.append(f"  - {mod} ({count} occurrences)")
    else:
        analysis.append("  No imports found")
    
    # 5. File statistics
    analysis.append("\n[5] FILE STATISTICS")
    analysis.append("-" * 70)
    
    file_types = {}
    total_lines = 0
    skip_dirs = {'__pycache__', '.git', 'node_modules', '.venv', 'venv', 'site-packages'}
    
    for f in root.rglob("*"):
        if not any(part in skip_dirs for part in f.parts):
            if f.is_file():
                ext = f.suffix or "no_extension"
                file_types[ext] = file_types.get(ext, 0) + 1
                
                try:
                    total_lines += len(f.read_text(errors='ignore').split('\n'))
                except:
                    pass
    
    analysis.append(f"Total lines of code (estimate): {total_lines:,}")
    analysis.append("File types:")
    for ext, count in sorted(file_types.items(), key=lambda x: -x[1])[:10]:
        analysis.append(f"  - {ext}: {count} files")
    
    # 6. Likely dataflow
    analysis.append("\n[6] INFERRED DATAFLOW & WORKFLOW")
    analysis.append("-" * 70)
    
    if "django" in str(frameworks).lower():
        analysis.append("  Pattern: Django MVT (Models → Views → Templates)")
        analysis.append("  Flow: HTTP Request → URL Router → View → Model → Database → Template → Response")
    elif "fastapi" in str(frameworks).lower():
        analysis.append("  Pattern: FastAPI REST API")
        analysis.append("  Flow: HTTP Request → Route Handler → Business Logic → Database → JSON Response")
    elif "react" in str(frameworks).lower():
        analysis.append("  Pattern: React SPA (Single Page Application)")
        analysis.append("  Flow: User Interaction → React Component → State Update → Re-render → DOM Update")
    elif "express" in str(frameworks).lower():
        analysis.append("  Pattern: Express.js REST API")
        analysis.append("  Flow: HTTP Request → Middleware → Route Handler → Business Logic → Response")
    
    if "Python" in str(languages):
        analysis.append("  Data handling: Likely file/database I/O with Python libraries")
    if "JavaScript" in str(languages) or "TypeScript" in str(languages):
        analysis.append("  Data handling: Likely async/promise-based, possible real-time updates")
    
    # 7. Configuration files
    analysis.append("\n[7] CONFIGURATION & BUILD FILES")
    analysis.append("-" * 70)
    
    config_files = []
    for cf in ['.env', '.env.example', 'docker-compose.yml', 'Dockerfile', '.github', 'pytest.ini', 'setup.cfg', 'tox.ini']:
        if (root / cf).exists():
            config_files.append(f"  - {cf}")
    
    if config_files:
        for cf in config_files:
            analysis.append(cf)
    else:
        analysis.append("  No standard config files detected")
    
    analysis.append("\n" + "="*70)
    
    return "\n".join(analysis)


def main():
    # Load environment variables from .env files
    load_environment()
    
    parser = argparse.ArgumentParser(
        description="""
================================================================================
                              CONTEXTIFY v1.1.0
         Transform your coding requests into AI-ready context-aware prompts
================================================================================

Contextify analyzes your codebase and generates comprehensive prompts that
help AI coding assistants (GitHub Copilot, Claude, etc.) understand context,
constraints, and your coding style - resulting in better, production-ready code.

WHAT IT DOES:
  * Analyzes your project structure and detects technology stack
  * Gathers relevant code files and configuration
  * Creates smart, context-aware prompts for AI assistants
  * Supports multiple detail levels (simple vs detailed modes)
  * Integrates with GitHub Copilot, Google Gemini, and other providers

QUICK START:
  contextify "add dark mode toggle"
  contextify "fix login bug" -s                    # Simple mode (no code)
  contextify "create new component" --dry-run     # Preview context
  contextify onboard                              # Setup provider

USE CASES:
  > Code generation with full project context
  > Bug fixes with constraint awareness
  > Feature implementation with style matching
  > Refactoring with dependency understanding
  > Database migrations with schema awareness
================================================================================
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Main 'prompt' command (default if no command specified)
    prompt_parser = subparsers.add_parser(
        'prompt',
        help='Generate context-aware prompt',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="""
GENERATE CONTEXT-AWARE PROMPTS FOR YOUR CODING REQUESTS

The 'prompt' command (default) analyzes your codebase and generates an
optimized prompt that you can paste directly into any AI coding assistant.

COMMAND SYNTAX:
  contextify "your request"                 # Request (command is optional)
  contextify prompt "your request"          # Explicit prompt command
  contextify "your request" [options]       # With options

REQUEST EXAMPLES:
  "add dark mode toggle to the app"
  "fix the authentication bug"
  "create a new user profile component"
  "refactor the database layer"
  "implement pagination for posts"

DETAIL MODES:
  --simple, -s           Simple mode: concise prompt without code details
  --detailed, -d         Detailed mode: comprehensive with code samples (default)

CONTEXT GATHERING:
  --focus {frontend|backend|database|config|tests}
                         Focus on specific area (others still included, just prioritized)
  --target FILE          Primary file to analyze deeply (must exist)
  --changed              Only include recently modified files (via git)
  --git-aware            Include unstaged/staged files with activity clues
  --tree-shake           With --target: include only direct dependencies (minimal)
  --skeleton-context     With --target: show function signatures only (not impl)
  --max-files N          Max files to include (default: 30)
  --exclude-patterns P   Exclude paths matching patterns (glob syntax)

INFORMATION CONTROL:
  --no-tree              Omit the file tree visualization
  --no-style             Don't analyze code style and patterns
  --no-negative-context  Skip constraint injection from config/patterns
  --hard-lock            Inject strict environment constraints from configs
  --scope-function NAME  Limit changes to specific function (negative constraint)

AI PROVIDER & MODEL:
  --use-github           Use GitHub Copilot API (default: Google Gemini)
  --model-name MODEL     AI model name (default: gemini-2.5-flash)
  --temperature [0-1]    Randomness control: lower=deterministic, higher=creative
                         Default: 0.7 (balanced)

OUTPUT OPTIONS:
  --output FILE, -o      Save to file instead of copying to clipboard
  --no-clipboard         Don't copy to clipboard (show in terminal)
  --dry-run              Preview gathered context WITHOUT calling AI

ADVANCED PATTERNS:
  Tree-shaking (minimal context):
    contextify "fix bug" --target src/Bug.ts --tree-shake

  Skeleton context (function signatures only):
    contextify "refactor" --target src/utils.ts --skeleton-context

  Combined approach:
    contextify "optimize" --target src/api.ts --tree-shake --skeleton-context

  Focus on specific tech stack:
    contextify "new page" --focus frontend
    contextify "new endpoint" --focus backend --hard-lock

EXAMPLES:

  1. Basic code generation:
     $ contextify "add a dark mode toggle"

  2. Simple mode (quick, no code details):
     $ contextify "fix login bug" -s

  3. Preview what will be sent (dry run):
     $ contextify "new feature" --dry-run

  4. Target specific file with minimal context:
     $ contextify "optimize this function" --target src/heavy.ts --tree-shake

  5. Save to file instead of clipboard:
     $ contextify "large refactor" --output prompt.md

  6. Focus on specific part of codebase:
     $ contextify "new component" --focus frontend

  7. Use GitHub Copilot instead of Gemini:
     $ contextify "your request" --use-github

  8. Control AI creativity:
     $ contextify "deterministic code" --temperature 0.1
     $ contextify "creative solution" --temperature 0.9

  9. Only analyze recent changes:
     $ contextify "fix recent bugs" --changed

 10. Database migration with constraints:
     $ contextify "add users table" --focus database --hard-lock

ENVIRONMENT SETUP:
  Run 'contextify onboard' for interactive provider setup
  Or set: GEMINI_API_KEY or GITHUB_TOKEN environment variables

PERFORMANCE TIPS:
  • Use --tree-shake for large codebases (faster, focused)
  • Use -s (--simple) for quick requests (smaller prompts)
  • Use --skeleton-context for many files (reduces token usage)
  • Set --max-files lower for very large projects (default: 30)

TROUBLESHOOTING:
  • "No files found": Check your project has code files
  • "API key not found": Run 'contextify onboard' or set env vars
  • "Command failed": Use --dry-run to debug context gathering

See 'contextify --help' for global options
        """,
        epilog="""
QUICK REFERENCE:
  -s, --simple               Simple mode (no code)
  -d, --detailed             Detailed mode with code (default)
  --focus {area}             Focus on specific area
  --target FILE              Primary file to analyze
  --tree-shake               Minimal context (direct deps only)
  --dry-run                  Preview context without AI call
  -o, --output FILE          Save to file
  --no-clipboard             Don't copy to clipboard

Still confused? Try: contextify --help
Setup providers: contextify onboard
        """
    )
    
    prompt_parser.add_argument('request', nargs='?', default=None, help='Your coding request (e.g., "add dark mode")')
    prompt_parser.add_argument('--focus', choices=['frontend', 'backend', 'database', 'config', 'tests'],
                       help='Focus on specific part of codebase')
    prompt_parser.add_argument('--changed', action='store_true',
                       help='Only include files changed in git')
    prompt_parser.add_argument('--output', '-o', help='Save to file instead of clipboard')
    prompt_parser.add_argument('--max-files', type=int, default=30,
                       help='Maximum number of files to include (default: 30)')
    prompt_parser.add_argument('--no-clipboard', action='store_true',
                       help='Do not copy to clipboard')
    prompt_parser.add_argument('--model-name', type=str, default='gemini-2.5-flash',
                       help="Specify the generative AI model to use (default: 'gemini-2.5-flash')")
    prompt_parser.add_argument('--temperature', type=float, default=0.7, metavar='[0.0-1.0]',
                       help='Controls randomness in generation; lower values make output more deterministic (default: 0.7)')
    prompt_parser.add_argument('--use-github', action='store_true',
                       help='Use GitHub Copilot API instead of Gemini (requires GITHUB_TOKEN)')
    prompt_parser.add_argument('--no-tree', action='store_true',
                       help='Do not include the file tree in the generated prompt')
    prompt_parser.add_argument('--no-style', action='store_true',
                       help='Do not include the detected code style in the generated prompt')
    prompt_parser.add_argument('--exclude-patterns', type=str, nargs='*', default=[],
                       help='Glob patterns for files/directories to explicitly exclude from context gathering (e.g., "temp/*", "docs/")')
    prompt_parser.add_argument('--target', type=str,
                       help='Primary file to include fully (used for tree-shaking and skeleton context)')
    prompt_parser.add_argument('--tree-shake', action='store_true',
                       help='Include only direct dependencies of --target (minimal context)')
    prompt_parser.add_argument('--skeleton-context', action='store_true',
                       help='Strip implementations from non-target files (signatures only)')
    prompt_parser.add_argument('--git-aware', action='store_true',
                       help='Include recently modified git files and inject intent clue')
    prompt_parser.add_argument('--hard-lock', action='store_true',
                       help='Inject strict tech stack constraints from config files')
    prompt_parser.add_argument('--no-negative-context', action='store_true',
                       help='Disable negative constraints injection')
    prompt_parser.add_argument('--scope-function', type=str,
                       help='Limit changes to a specific function name (negative constraint)')
    
    # Add mutually exclusive group for detail level
    detail_group = prompt_parser.add_mutually_exclusive_group()
    detail_group.add_argument('-s', '--simple', action='store_true',
                              help='Generate simple paragraph prompt without code details')
    detail_group.add_argument('-d', '--detailed', action='store_true',
                              help='Generate detailed prompt with code suggestions (default)')
    prompt_parser.add_argument('--dry-run', action='store_true',
                       help='Preview gathered context without calling AI (useful for debugging)')
    prompt_parser.add_argument('--analyze', action='store_true',
                       help='Analyze project structure, workflow, and dataflow without generating a prompt')
    prompt_parser.add_argument('--ai', action='store_true',
                       help='Use AI to enhance analysis (combine with --analyze for detailed AI-powered report)')
    
    # Onboarding command
    onboard_parser = subparsers.add_parser(
        'onboard',
        help='Interactive setup wizard for providers and models',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="""
INTERACTIVE SETUP WIZARD FOR AI PROVIDERS

The 'onboard' command guides you through setting up your preferred AI provider
and securely storing credentials. Run this once to get started!

PROVIDERS AVAILABLE:
  • GitHub Copilot      - Access to GPT-4o and other models
  • Google Gemini       - Gemini 2.0 Flash, 1.5 Pro/Flash
  • OpenAI              - GPT-4 and GPT-3.5 Turbo
  • Anthropic           - Claude 3 Opus, Sonnet, Haiku
  • Local Proxy         - Connect to local AI server

AUTHENTICATION FLOW:
  1. Choose your preferred provider
  2. Select which model to use
  3. Authenticate securely (API key or device flow)
  4. Credentials saved to OS keyring (encrypted)

QUICK START:
  $ contextify onboard      # Interactive (recommended)

AUTOMATION / SCRIPTING:
  $ contextify onboard --non-interactive --auth-choice github-copilot
  $ contextify onboard --provider google-gemini

EXAMPLES:

  1. Interactive setup (recommended):
     $ contextify onboard

  2. Automated GitHub Copilot setup:
     $ contextify onboard --non-interactive --auth-choice github-copilot

  3. Automated Google Gemini setup:
     $ contextify onboard --non-interactive --auth-choice google-gemini

  4. Using provider alias:
     $ contextify onboard --provider github-copilot

ENVIRONMENT VARIABLES (Optional):
  GEMINI_API_KEY         - Google Gemini API key (if not storing in keyring)
  GITHUB_TOKEN           - GitHub personal access token
  OPENAI_API_KEY         - OpenAI API key
  ANTHROPIC_API_KEY      - Anthropic API key

CREDENTIAL STORAGE:
  • Credentials stored in OS keyring for maximum security:
    - Windows: Credential Manager
    - macOS: Keychain
    - Linux: libsecret
  • Fallback to encrypted file if keyring unavailable
  • Never stored in plain text

RECONFIGURATION:
  Run 'contextify onboard' anytime to change providers or credentials

TROUBLESHOOTING:
  • "Keyring not available": Environment variable fallback will be used
  • "Invalid API key": Check your token and try again
  • "Need model discovery": Check internet connection and API access

        """,
        epilog="""
Need help? Run: contextify --help
Start using: contextify "your request"
        """
    )
    onboard_parser.add_argument('--non-interactive', action='store_true',
                        help='Run in non-interactive mode (for scripting)')
    onboard_parser.add_argument('--auth-choice', type=str,
                        choices=['github-copilot', 'google-gemini', 'openai', 'anthropic', 'local-proxy', 'skip'],
                        help='Pre-select provider (non-interactive)')
    onboard_parser.add_argument('--provider', type=str, dest='provider_name',
                        help='Provider alias (alternative to --auth-choice)')
    
    parser.add_argument('--version', '-v', action='version', version=f'%(prog)s {__version__}')
    
    # Handle backward compatibility: contextify "request" -> contextify prompt "request"
    # Also handle: contextify --analyze -> contextify prompt --analyze
    # Check if first non-option argument is not a valid subcommand
    argv = sys.argv[1:]  # Skip program name
    if argv:
        # Check if only flags are present and no subcommand
        if all(arg.startswith('-') for arg in argv):
            # Only flags, no subcommand - inject 'prompt' command
            sys.argv = [sys.argv[0], 'prompt'] + argv
        elif argv[0].startswith('-'):
            # First arg is a flag, not a command - inject 'prompt' command
            sys.argv = [sys.argv[0], 'prompt'] + argv
        elif argv[0] not in ['prompt', 'onboard']:
            # First arg is likely a request string, not a command - inject 'prompt' command
            sys.argv = [sys.argv[0], 'prompt'] + argv
    
    args = parser.parse_args()
    
    # Additional safety check
    if not args.command:
        # This shouldn't happen now, but handle it gracefully
        parser.print_help()
        sys.exit(1)
    
    # Handle 'onboard' command
    if args.command == 'onboard':
        from .onboarding import run_onboarding
        success = run_onboarding(non_interactive=getattr(args, 'non_interactive', False))
        sys.exit(0 if success else 1)
    
    # Handle 'analyze' command (part of prompt)
    if args.command == 'prompt' and hasattr(args, 'analyze') and args.analyze:
        report = analyze_project()
        
        # If --ai flag is set, enhance the report with AI
        if hasattr(args, 'ai') and args.ai:
            # Load configuration and provider
            from .config import get_config_manager
            from .auth import get_auth_manager
            
            config_mgr = get_config_manager()
            auth_mgr = get_auth_manager(config_mgr.config_dir)
            
            # Determine provider - try GitHub first, then Gemini
            provider = None
            
            # Try GitHub Copilot
            if hasattr(args, 'use_github') and args.use_github:
                github_token = os.environ.get('GITHUB_TOKEN')
                if not github_token:
                    try:
                        github_token = auth_mgr.get_credential("github-copilot:default")
                    except:
                        github_token = None
                
                if github_token:
                    try:
                        provider = GitHubCopilotProvider(github_token)
                    except Exception as e:
                        pass
            
            # Try Gemini if no GitHub provider
            if not provider:
                google_token = os.environ.get('GEMINI_API_KEY')
                if not google_token:
                    try:
                        google_token = auth_mgr.get_credential("google-gemini:default")
                    except:
                        google_token = None
                
                if google_token:
                    try:
                        provider = GeminiProvider(google_token)
                    except Exception as e:
                        pass
            
            if provider:
                # Use AI to enhance the analysis with a structured report format
                ai_prompt = f"""You are an expert software architect. Analyze this project structure report and provide a comprehensive analysis structured EXACTLY as follows. Each section must have a clear heading and detailed explanation.

DO NOT include any introductory text, preamble, or instructions. START DIRECTLY with section 1.

---

## 1. Architecture Overview

Describe the high-level architecture based on the report. Note the absence of detected frameworks and discuss implications. Consider the large scripts/ directory with diverse file types (.py, .ps1, .bat, .sh) and what this reveals about the architectural pattern.

## 2. Project Purpose & Scope

Infer the main objective using clues from: project name (contextify), key imports (keyring for credentials, requests for HTTP, google for APIs), and the prevalence of scripting files. What domain or problem does this solve?

## 3. Technology Stack

List detected languages (Python) and frameworks (None detected). For each key import listed (os, pathlib, json, typing, keyring, subprocess, requests, google, sys, time), explain its typical use. Note the diverse shell script types (.ps1, .bat, .sh).

## 4. Code Organization

Describe the role of each directory:
- contextify/ (15 items): Core application with main.py and __main__.py
- scripts/ (5349 items): Analyze this extraordinary volume and diverse content
- docs/, tests/, examples/: Their roles in the project

Comment on the imbalance: only 9 Python files vs 5349+ script items.

## 5. Data Flow

Explain how data flows through the system:
- INPUT: CLI arguments, environment variables, files, network (requests), credentials (keyring)
- PROCESSING: File I/O (os/pathlib), JSON parsing, network communication, system commands
- OUTPUT: Files, network responses, console output, system changes

What types of data are handled (configuration, credentials, JSON, text)?

## 6. Key Components

Identify main functional modules:
- contextify module: Core application logic, entry points, context management, credential interaction
- scripts/ directory: Collection of automation scripts and task executors
- keyring integration: Secure credential management
- requests/google: External API communication

## 7. Development Workflow

Based on docs/, tests/, examples/, and .env.example:
- How is configuration handled?
- What role does documentation and testing play?
- Implications of maintaining a large scripts/ directory
- What is the primary development environment?

## 8. Dependencies & Integrations

List:
- Internal dependencies: modules within contextify and orchestration of scripts
- External Python libraries: keyring (credentials), requests (HTTP), google (APIs), os/sys/subprocess (OS interactions)
- External services: What APIs or services likely integrate? (infer from imports)
- OS-level interactions: Indicated by shell script types and subprocess usage

## 9. Potential Issues

Identify red flags and concerns:
- **CRITICAL:** The extremely large scripts/ directory (5349 items) - implications for maintainability, testability, organization, discoverability
- Absence of detected framework at this scale
- Only 9 Python files in core vs massive script count
- Lack of explicit database/persistent storage solutions (if relevant)
- Any other obvious anti-patterns or concerns

## 10. Recommendations

Provide actionable suggestions:
- **Strategies for scripts/ directory:** Categorization, logic extraction to Python modules, CLI framework adoption, testing strategies
- Enhanced documentation for scripts
- Expanded test coverage
- Formal dependency management (requirements.txt, Poetry, etc.)
- Consider lightweight Python framework for CLI/configuration
- Any other structural improvements

---

PROJECT ANALYSIS REPORT:
{report}

---

Now provide the analysis following the exact 10-section structure above. Be detailed and insightful. Start with Section 1."""

                try:
                    ai_report = provider.generate_prompt(
                        system_prompt="You are an expert software architect. Provide detailed technical analysis structured in exactly 10 sections with clear headings. Be specific, analytical, and actionable. Do not include any preamble or meta-commentary.",
                        user_request=ai_prompt,
                        context="",
                        temperature=0.7
                    )
                    
                    print("\n" + "="*70)
                    print("AI-ENHANCED PROJECT ANALYSIS")
                    print("="*70 + "\n")
                    print(ai_report)
                except Exception as e:
                    print(report)
                    print(f"\n[WARNING] Failed to enhance with AI: {e}")
            else:
                print(report)
                print("\n[WARNING] AI provider not configured. Showing basic analysis.")
                print("Run 'contextify onboard' to configure an AI provider.")
        else:
            print(report)
        
        sys.exit(0)
    
    # From here on, we're handling the 'prompt' command
    if args.command != 'prompt':
        parser.error(f"Unknown command: {args.command}")
    
    # Validate request
    if not getattr(args, 'request', None):
        parser.error("'request' is required")
    
    # Validate temperature
    if hasattr(args, 'temperature') and not 0.0 <= args.temperature <= 1.0:
        parser.error("--temperature must be between 0.0 and 1.0")

    if hasattr(args, 'tree_shake') and args.tree_shake and not args.target:
        parser.error("--tree-shake requires --target")
    
    # Load configuration
    from .config import get_config_manager
    from .auth import get_auth_manager
    
    config_mgr = get_config_manager()
    auth_mgr = get_auth_manager(config_mgr.config_dir)
    
    # Determine provider from config or CLI flags
    provider = None
    
    # First, check if user specified provider via CLI
    if hasattr(args, 'use_github') and args.use_github:
        # User explicitly requested GitHub Copilot
        github_token = os.environ.get('GITHUB_TOKEN')
        if not github_token:
            # Try to get from auth manager
            profile = auth_mgr.get_profile("github-copilot:default")
            if profile:
                github_token = auth_mgr.get_credential("github-copilot:default")
        
        if not github_token and not args.dry_run:
            print("[ERROR] GitHub Copilot not configured")
            print("\nTo set up GitHub Copilot:")
            print("  contextify onboard")
            print("\nOr set GITHUB_TOKEN environment variable:")
            print("  export GITHUB_TOKEN='your-token'")
            sys.exit(1)
        
        if not args.dry_run:
            try:
                provider = GitHubCopilotProvider(github_token)
            except Exception as e:
                print(f"[ERROR] Failed to initialize GitHub Copilot provider: {e}")
                sys.exit(1)
    else:
        # Use configured model/provider from config, fall back to Gemini
        default_model = config_mgr.get_default_model()
        
        if default_model and not args.dry_run:
            # Use configured provider
            provider_name = default_model.split('/')[0]  # e.g., "github-copilot" from "github-copilot/gpt-4o"
            
            if provider_name == "github-copilot":
                # Get GitHub token from auth
                github_token = auth_mgr.get_credential("github-copilot:default")
                if github_token:
                    try:
                        provider = GitHubCopilotProvider(github_token)
                    except Exception as e:
                        print(f"[WARN] Failed to use configured GitHub Copilot: {e}")
                        print("Falling back to Gemini...")
                        provider = None
            elif provider_name == "google" or provider_name == "google-gemini":
                # Get Gemini API key
                api_key = auth_mgr.get_credential("google-gemini:default")
                if api_key:
                    provider = GeminiProvider(api_key, model_name=default_model.split('/')[-1])
                else:
                    print(f"[WARN] Configured provider not found in auth store: {provider_name}")
                    provider = None
        
        # Fall back to Gemini if no config or provider init failed
        if not provider:
            api_key = os.environ.get('GEMINI_API_KEY')
            if not api_key:
                # Try to get from auth manager
                profile = auth_mgr.get_profile("google-gemini:default")
                if profile:
                    api_key = auth_mgr.get_credential("google-gemini:default")
            
            if not api_key and not args.dry_run:
                print("[ERROR] No default provider configured and GEMINI_API_KEY not set")
                print("\nTo set up a provider:")
                print("  contextify onboard")
                print("\nOr set GEMINI_API_KEY environment variable:")
                print("  export GEMINI_API_KEY='your-key'")
                sys.exit(1)
            
            if api_key and not args.dry_run:
                model_name = getattr(args, 'model_name', 'gemini-2.5-flash')
                provider = GeminiProvider(api_key, model_name=model_name)
    
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
        'negative_constraints': negative_constraints,
        'temperature': args.temperature
    }
    
    spinner.stop()
    
    detail_level = "simple (no code)" if args.simple else "detailed (with code)"
    print(f"[+] Found {len(context['files'])} relevant files")
    if not args.no_style:
        print(f"[STYLE] Detected: {context['style'].get('language', 'unknown')} with {context['style'].get('framework', 'no framework')}")
    
    # Handle dry-run mode
    if args.dry_run:
        print("\n" + "="*60)
        print("[DRY RUN] Context Preview")
        print("="*60)
        
        if not args.no_tree:
            print(f"\n[FILE TREE]\n{context['file_tree']}")
        
        if not args.no_style and context['style']:
            print(f"\n[CODE STYLE]")
            for key, value in context['style'].items():
                if value:
                    if isinstance(value, list):
                        print(f"   - {key.title()}: {', '.join(value)}")
                    else:
                        print(f"   - {key.title()}: {value}")
        
        print(f"\n[FILES] Files to include ({len(context['files'])})")
        for i, f in enumerate(context['files'][:10], 1):
            print(f"   {i}. {f['path']}")
        if len(context['files']) > 10:
            print(f"   ... and {len(context['files']) - 10} more")
        
        print(f"\n[SETTINGS]")
        print(f"   - Detail level: {detail_level}")
        print(f"   - Focus: {args.focus or 'all'}")
        print(f"   - Target: {args.target or 'none'}")
        print(f"   - Tree-shake: {args.tree_shake}")
        print(f"   - Skeleton context: {args.skeleton_context}")
        print(f"   - Git-aware: {args.git_aware}")
        print(f"   - Hard-lock: {args.hard_lock}")
        print(f"   - Negative constraints: {not args.no_negative_context}")
        # Derive provider name from flags and model name for clearer output
        if args.use_github:
            provider_name = "GitHub Copilot"
        else:
            mn = (args.model_name or "").lower()
            if "gemini" in mn:
                provider_name = "Gemini"
            elif "gpt" in mn or "openai" in mn:
                provider_name = "GPT"
            elif "claude" in mn or "anthropic" in mn:
                provider_name = "Claude"
            else:
                provider_name = args.model_name.split('/')[0].capitalize() if args.model_name else 'Unknown'

        print(f"   - Provider: {provider_name}")
        print(f"   - Model: {args.model_name}")
        print(f"   - Temperature: {args.temperature}")
        print("="*60)
        sys.exit(0)
    
    # Reuse provider_name computed above (fall back if missing)
    provider_name = provider_name if 'provider_name' in locals() else ("GitHub Copilot" if args.use_github else "Gemini")
    spinner2 = Spinner(f"Generating refined prompt with {provider_name} ({args.model_name}, temperature={args.temperature}, {detail_level})")
    spinner2.start()
    
    # Generate prompt
    generator = PromptGenerator(provider)
    refined_prompt = generator.generate_prompt(
        args.request, 
        context, 
        include_file_contents=include_file_contents,
        simple_mode=args.simple  # Pass simple mode flag
    )
    
    spinner2.stop()
    
    # Output
    if args.output:
        output_path = Path(args.output)
        with open(output_path, 'w') as f:
            f.write(refined_prompt)
        print(f"[SUCCESS] Prompt saved to: {output_path}")
    
    if not args.no_clipboard:
        try:
            pyperclip.copy(refined_prompt)
            print("[CLIPBOARD] Prompt copied to clipboard!")
        except:
            print("[WARNING] Could not copy to clipboard (pyperclip not available)")
            if not args.output:
                print("\n" + "="*80)
                print(refined_prompt)
                print("="*80)
    
    if not args.output and args.no_clipboard:
        print("\n" + "="*80)
        print(refined_prompt)
        print("="*80)
    
    print("\n[DONE] Paste the prompt into your AI coding assistant.")


if __name__ == '__main__':
    main()
