# Project Overview

This is a minimal Python project template managed with `uv`, serving as a foundation for building Python applications. The project follows modern Python best practices with a clean architecture, comprehensive testing setup, and integrated Claude Agent SDK workflows for automated development tasks.

## Architecture

### Directory Structure

- **`src/myproject/`** - Main application package containing the core business logic
  - `__init__.py` - Package initialization and version metadata
  - `__main__.py` - Application entry point with the main() function

- **`tests/`** - Test suite using pytest framework
  - Test files mirror the source structure with `test_` prefix
  - Currently contains `test_main.py` for testing the main module

- **`.play/`** - Claude Agent SDK configuration for automated workflows
  - `agents.yaml` - Defines specialized AI agents (coder, tester, debugger, reviewer)
  - `tools.yaml` - Configures available CLI tools and permissions
  - `agents/` - Agent instruction files (markdown format)

- **Root Configuration Files**
  - `pyproject.toml` - Project metadata, dependencies, and tool configuration
  - `playfile.yaml` - Workflow definitions for TDD, traditional coding, and bugfixes
  - `README.md` - Project documentation and setup instructions

## Core Concepts

### Package Structure Pattern
- Source code lives in `src/myproject/` following the src-layout convention
- This prevents accidental imports from the source directory during testing
- Package is executable via `python -m myproject` using `__main__.py`

### Testing Strategy
- pytest as the testing framework with configuration in `pyproject.toml`
- Tests located in `tests/` directory with `pythonpath = ["src"]` for imports
- Tests use fixtures like `capsys` for capturing output
- Follow naming convention: `test_*.py` for files, `test_*` for functions

### Agent-Driven Development Workflows
- **TDD Workflow** (`code-tdd`): Red (write tests) → Green (implement) → Refactor → Review
- **Traditional Workflow** (`code`): Implement → Test → Review
- **Bugfix Workflow** (`bugfix`): Root cause analysis → Fix → Validate → Review
- Workflows use specialized agents with role-based access to tools

### Code Quality Standards
- Ruff for linting and formatting (replaces black, isort, flake8)
- Line length: 88 characters
- Target Python version: 3.9+
- Enabled linters: E (errors), F (pyflakes), I (import order)

## Tech Stack

### Core Language & Runtime
- **Python**: >=3.9
- **uv**: Fast Python package installer and dependency manager

### Development Tools
- **pytest**: >=7.0.0 - Testing framework
- **ruff**: >=0.1.0 - Fast Python linter and formatter

### Build System
- **hatchling**: PEP 517-compliant build backend
- Builds wheel packages from `src/myproject/`

### AI/Agent Infrastructure
- **Claude Agent SDK**: Orchestrates multi-agent development workflows
- **Agent Models**:
  - `claude-sonnet-4-5-20250929` - Primary model for all agents (smartest, best for complex coding)
  - `claude-haiku-4-5-20251001` - Available for faster tasks
  - `claude-opus-4-1-20250805` - Available for specialized reasoning

## Development Workflow

### Setup
```bash
# Install dependencies
uv sync
```

### Running the Application
```bash
# Execute the main module
uv run python -m myproject

# Expected output: "Hello from myproject!"
```

### Testing
```bash
# Run all tests
uv run pytest

# Tests are discovered in tests/ directory
# Configuration in [tool.pytest.ini_options] in pyproject.toml
```

### Code Quality
```bash
# Run linter (via ruff)
uv run ruff check .

# Auto-fix issues
uv run ruff check --fix .

# Format code
uv run ruff format .
```

### Agent Workflows
```bash
# TDD: Write tests first, implement, refactor, review
play run code-tdd --prompt "Add a greet(name) function"

# Traditional: Implement first, then test, then review
play run code --prompt "Add logging support"

# Bugfix: Analyze root cause, fix, validate, review
play run bugfix --prompt "Fix import error in __main__.py"
```

### Validation (Optional)
The playfile.yaml includes commented-out validation blocks that can be enabled:
- Uncomment `validate.post_command: "pytest"` in workflow steps
- Tests run automatically after implementation/refactoring
- Max retries configurable per step
- Can halt workflow on test failures

### Build/Distribution
```bash
# Build wheel package
uv build

# Output: dist/myproject-0.1.0-py3-none-any.whl
```

## Key Conventions

1. **Import Style**: Absolute imports from package name (`from myproject.__main__ import main`)
2. **Type Hints**: Use return type annotations (`-> None`) for functions
3. **Docstrings**: Module and function docstrings following standard format
4. **Version Management**: Single source of truth in `src/myproject/__init__.py`
5. **Agent Collaboration**: Use specialized agents for their strengths (debugger for investigation, coder for implementation, reviewer for quality checks)
