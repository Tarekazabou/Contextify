# Project Analysis Feature

Contextify 1.2.0 introduces powerful project analysis capabilities to help you understand your codebase quickly and deeply.

## Overview

The project analysis feature provides two complementary analysis modes:
1. **Static Analysis** (`--analyze`) - Quick technical breakdown without AI
2. **AI-Enhanced Analysis** (`--analyze --ai`) - Deep AI-powered insights

## Static Analysis

### Quick Start

```bash
contextify --analyze
```

### What You Get

A comprehensive technical report of your project including:

- **Project Structure** - Directory organization and layout
- **Technology Stack** - Detected languages, frameworks, and major libraries
- **Entry Points** - Main application files (main.py, index.js, app.ts, etc.)
- **Languages Detected** - Programming languages used (Python, JavaScript/TypeScript, Go, Rust, Java, etc.)
- **Frameworks Detected** - Popular frameworks (Django, Flask, FastAPI, React, Next.js, Express, Vue, Angular, etc.)
- **Dependencies** - Import/require analysis showing what your code depends on
- **File Statistics** - Counts of files, estimated lines of code, code organization patterns
- **Configuration Files** - Package managers, build tools, configuration systems found
- **Inferred Dataflow** - How data appears to move through your application
- **Architecture Hints** - Suggested architecture patterns detected

### Example Output

```
PROJECT ANALYSIS REPORT
======================

Project Structure:
- Type: Python/Django Web Application
- Root: /home/user/my-project
- Main entry: manage.py

Technology Stack:
- Languages: Python 3.9+
- Framework: Django 4.2
- Database: PostgreSQL
- Frontend: React (bundled in /static)
- ORM: Django ORM
- Testing: pytest

Key Directories:
- /myapp/  (Django app with models, views, serializers)
- /api/    (REST API endpoints)
- /static/ (React frontend)
- /tests/  (Test suite)

Entry Points:
- manage.py (Django management)
- wsgi.py (Production server entry)
- frontend/package.json (Node/React build)

Core Dependencies:
- djangorestframework (API)
- celery (Background tasks)
- redis (Caching)
- psycopg2 (PostgreSQL adapter)
- react, react-dom (Frontend)

Inferred Architecture:
- Multi-layered architecture
- REST API with Django REST Framework
- React SPA frontend
- Async task processing with Celery
```

## AI-Enhanced Analysis

### Quick Start

```bash
contextify --analyze --ai
```

### What You Get

A detailed 10-section architectural analysis powered by your configured AI provider (GitHub Copilot, Gemini, etc.):

#### Section 1: Architecture Overview
A comprehensive overview of your system design, how components interact, and the overall structure.

#### Section 2: Project Purpose & Scope
Clear explanation of what the project is, what problem it solves, and what it's designed to handle.

#### Section 3: Technology Stack
Assessment of why certain technologies were chosen, how they fit together, and their roles in the system.

#### Section 4: Code Organization
Analysis of your directory structure, file organization, and design patterns used throughout.

#### Section 5: Data Flow
How data moves through your application, from inputs to outputs, including persistence.

#### Section 6: Key Components
Important files and modules, their responsibilities, and how they interconnect.

#### Section 7: Development Workflow
How other developers should work with your codebase, including build steps, testing, and deployment.

#### Section 8: Dependencies & Integrations
External services, APIs, and library dependencies with explanations of why they're used.

#### Section 9: Potential Issues
Areas of concern, technical debt, scalability considerations, and potential problems to watch for.

#### Section 10: Recommendations
Suggested improvements, modernization opportunities, and best practices to adopt.

### Example Output

```markdown
# Project Analysis Report

## 1. Architecture Overview

This is a full-stack TypeScript/Node.js application using Next.js for the frontend and Express.js 
for the backend API. The application follows a modern layered architecture with clear separation 
between presentation, business logic, and data persistence layers.

[... detailed analysis ...]

## 2. Project Purpose & Scope

The application is an e-commerce platform designed to:
- Allow users to browse and purchase products
- Manage shopping carts and orders
- Process payments securely
- Track inventory and stock levels

[... more details ...]

[... Sections 3-10 continue ...]
```

## Use Cases

### 1. Onboarding New Team Members

```bash
contextify --analyze --ai > ARCHITECTURE.md
```

Share the generated report with new team members for quick understanding.

### 2. Documentation

```bash
contextify --analyze --ai --output docs/TECHNICAL_OVERVIEW.md
```

Keep your technical documentation up-to-date automatically.

### 3. Architecture Reviews

```bash
contextify --analyze --ai --no-clipboard
```

Discuss architecture, identify issues, and plan improvements.

### 4. Codebase Understanding

```bash
contextify --analyze
```

Quick overview without AI cost for rapid technical assessment.

### 5. Project Evaluation

Before taking over a project:

```bash
contextify --analyze --ai
```

Get a comprehensive understanding of the codebase structure, technology choices, and potential issues.

## Options & Customization

### Basic Analysis

```bash
contextify --analyze
```

Static analysis only, no API calls, instant results.

### AI-Enhanced Analysis

```bash
contextify --analyze --ai
```

Uses your configured AI provider for detailed insights.

### Save to File

```bash
contextify --analyze --ai --output analysis.md
```

Save to a file instead of clipboard/stdout.

### Print to Console

```bash
contextify --analyze --ai --no-clipboard
```

Print directly to terminal for piping or immediate viewing.

### Combine with Focus

While `--focus` is primarily for prompt generation, you can use it with analysis:

```bash
contextify --analyze --focus frontend
```

Focus analysis on specific parts of your project.

## Requirements

### For Static Analysis
- None! `--analyze` works on any project immediately.

### For AI-Enhanced Analysis
- Configured AI provider (GitHub Copilot, Google Gemini, OpenAI, Anthropic, or Local Proxy)
- Valid credentials in `.env` file or environment variables

## Limitations & Notes

1. **Analysis Scope** - Analysis reflects the current state of your codebase at the moment of running
2. **Accuracy** - Static analysis is heuristic-based; AI analysis depends on provider quality
3. **Language Support** - Works best with JavaScript/TypeScript, Python, Go, Rust, and Java
4. **Large Projects** - Very large codebases (10K+ files) may take longer to analyze
5. **Privacy** - With `--analyze --ai`, project structure is sent to your AI provider

## Troubleshooting

### Analysis is Slow

```bash
# Use static analysis instead of AI
contextify --analyze
```

Or reduce files scanned:

```bash
contextify --analyze --max-files 50
```

### AI Analysis Is Generic

- Make sure you have a good `.gitignore` file to exclude noise
- Try with `--focus` to narrow the scope
- Ensure you're using a capable model (GPT-4, Claude, etc.)

### Analysis Doesn't Match My Codebase

- The analysis is heuristic-based; review and update it manually if needed
- Ensure your project structure is clear and follows conventions
- Well-organized projects get better analysis results

## See Also

- [FLAGS.md](FLAGS.md) - All available command-line options
- [QUICKSTART.md](QUICKSTART.md) - Quick start guide
- [README.md](../README.md) - Main documentation
