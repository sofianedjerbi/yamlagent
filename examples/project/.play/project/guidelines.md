I'll analyze the project to understand its structure, patterns, and conventions, then create comprehensive guidelines.# Project Guidelines & Best Practices

## 1. Code Organization

### Directory Structure
```
project/
├── src/project/          # Main application code (namespace package)
│   ├── __init__.py      # Package initialization, version, public API
│   └── __main__.py      # CLI entry point (python -m project)
├── tests/               # Test suite (pytest convention)
│   └── test_*.py        # Test files matching pytest pattern
├── dist/                # Build artifacts (gitignored except .gitignore)
├── .venv/               # Virtual environment (gitignored)
├── pyproject.toml       # Project metadata and dependencies
├── uv.lock              # Locked dependency versions (gitignored)
├── README.md            # Project documentation
├── playfile.yaml        # AI agent workflows (TDD, code, bugfix)
└── .gitignore           # Version control exclusions
```

### Code Placement Guidelines
- **Core logic**: Place in `src/project/` as separate modules
- **Public API**: Export from `src/project/__init__.py`
- **CLI/Entry point**: Keep in `src/project/__main__.py`
- **Tests**: Mirror source structure in `tests/` (e.g., `test_<module>.py`)
- **Config**: Keep build/dependency config in `pyproject.toml`

## 2. Naming Conventions

### Files
- **Modules**: `lowercase_with_underscores.py`
- **Tests**: `test_<module_name>.py` (pytest convention)
- **Entry point**: `__main__.py` for runnable packages
- **Init files**: `__init__.py` for package initialization

### Code Elements
- **Functions**: `lowercase_with_underscores()` (PEP 8)
  - Example: `greet(name: str) -> str`
- **Classes**: `CapitalizedWords` (PascalCase, PEP 8)
- **Variables**: `lowercase_with_underscores`
- **Constants**: `UPPER_CASE_WITH_UNDERSCORES`
- **Private**: `_leading_underscore` for internal use

### Test Naming
- **Test functions**: `test_<function>_<scenario>()`
  - Example: `test_greet_default()`, `test_greet_custom_name()`
- **Test classes**: `Test<ClassName>`

## 3. Architecture Patterns

### Package Structure
- **Namespace package**: `src/project/` layout (PEP 420)
- **Explicit exports**: Define `__all__` in `__init__.py` for public API
- **Version management**: Single source of truth in `__init__.py` (`__version__`)

### Code Patterns Observed
- **Type hints**: Full type annotations (PEP 484)
  - Functions: `def greet(name: str = "World") -> str:`
  - Return types explicitly declared
- **Docstrings**: Google-style format (PEP 257)
  ```python
  """Short description.
  
  Args:
      param: Description
  
  Returns:
      Description
  """
  ```
- **Entry points**: Separate `main()` function with `if __name__ == "__main__"` guard

### Design Principles
- **Simplicity**: Minimal, focused implementations
- **Type safety**: Use type hints throughout
- **Documentation**: Document all public functions/classes
- **Single responsibility**: Each module/function has one clear purpose

## 4. Development Workflow

### Setup
```bash
# Install production dependencies
uv sync

# Install with dev dependencies (pytest, ruff)
uv sync --extra dev
```

### Running Code
```bash
# Run as module
uv run python -m project

# Run specific script
uv run python path/to/script.py
```

### Testing
```bash
# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/test_example.py

# Run with verbose output
uv run pytest -v
```

### Code Quality
```bash
# Lint code (check for issues)
uv run ruff check .

# Format code (auto-fix)
uv run ruff format .
```

### Build & Distribution
```bash
# Build package (hatchling backend)
uv build

# Output: dist/project-0.1.0-py3-none-any.whl
#         dist/project-0.1.0.tar.gz
```

### Package Management
- **Tool**: `uv` (fast Python package manager)
- **Lock file**: `uv.lock` (gitignored, auto-generated)
- **Dependencies**: Define in `pyproject.toml` [project.dependencies]
- **Dev dependencies**: Define in [project.optional-dependencies.dev]

## 5. Best Practices

### Code Quality Standards

**Linting & Formatting (Ruff)**
- Line length: 88 characters (Black-compatible)
- Target: Python 3.9+
- Rules enabled: E (pycodestyle errors), F (pyflakes), I (isort)
- Run before committing: `uv run ruff check . && uv run ruff format .`

**Type Checking**
- Use type hints for all function signatures
- Specify parameter types and return types
- Use `Optional[T]` for nullable values
- Example: `def greet(name: str = "World") -> str:`

**Documentation**
- Docstrings required for all public functions/classes
- Format: Google-style (Args, Returns, Raises)
- Keep docstrings concise and informative
- Document complex logic with inline comments

### Testing Standards

**Test Organization**
- Location: `tests/` directory (separate from source)
- Naming: `test_<module>.py` for test files
- Pattern: `test_<function>_<scenario>()` for test functions
- Discovery: pytest auto-discovers `test_*.py` and `test_*()` functions

**Test Coverage**
- Test happy path (default behavior)
- Test edge cases (empty inputs, boundaries)
- Test error conditions (invalid inputs)
- Example from `test_example.py`:
  - `test_greet_default()` - default argument
  - `test_greet_custom_name()` - custom input

**Test Structure**
- Keep tests simple and focused
- One assertion per test (when possible)
- Use descriptive test names
- Avoid test interdependencies

### Dependency Management

**Production Dependencies**
- Keep minimal (currently empty)
- Add to `[project.dependencies]` in pyproject.toml
- Install: `uv add <package>`

**Development Dependencies**
- Include testing/linting tools only
- Current: pytest (>=7.4.0), ruff (>=0.1.0)
- Add to `[project.optional-dependencies.dev]`
- Install: `uv add --dev <package>`

**Version Constraints**
- Use minimum versions: `>=X.Y.Z`
- Lock exact versions in `uv.lock` (auto-managed)
- Update: `uv sync` (respects constraints)

### Version Control

**Gitignore Strategy**
- Exclude build artifacts (`dist/`, `build/`, `*.egg-info/`)
- Exclude virtual environments (`.venv/`, `venv/`)
- Exclude IDE files (`.vscode/`, `.idea/`)
- Exclude Python bytecode (`__pycache__/`, `*.pyc`)
- Exclude lock files (`uv.lock`) - regenerate locally
- Include: Source code, tests, config, README

**Commit Guidelines**
- Run tests before committing: `uv run pytest`
- Format code before committing: `uv run ruff format .`
- Keep commits atomic and focused
- Write clear commit messages

### AI Agent Workflows (playfile.yaml)

**Available Tasks**
1. **code-tdd**: Test-Driven Development (Red → Green → Refactor → Review)
   - Write tests first
   - Implement to pass tests
   - Refactor with validation
   - Review final code

2. **code**: Traditional flow (Implement → Test → Review)
   - Implement feature
   - Create tests with validation
   - Review implementation

3. **bugfix**: Bug resolution (Root cause → Fix → Validate → Review)
   - Investigate root cause (debugger agent)
   - Fix with best practices
   - Review bugfix

**Validation**
- Commands commented by default
- Uncomment `validate.post_command: "uv run pytest"` to enable auto-testing
- Configure `max_retries` and `continue_on_failure` per step

**Agent Roles**
- `tester`: Creates tests (simple, efficient, covers edge cases)
- `coder`: Implements features (follows best practices)
- `reviewer`: Reviews code (quality, best practices, coverage)
- `debugger`: Finds root causes (thorough investigation)

## 6. Integration Guidelines for AI Agents

### Finding Existing Code
1. **Search for functionality**: Use `grep` in `src/project/`
2. **Check public API**: Read `src/project/__init__.py`
3. **Find tests**: Look in `tests/test_<module>.py`
4. **Check entry point**: Read `src/project/__main__.py`

### Adding New Code
1. **Create module**: Add `src/project/<feature>.py`
2. **Export API**: Add to `src/project/__init__.py` if public
3. **Write tests**: Create `tests/test_<feature>.py`
4. **Follow patterns**: Match existing code style (types, docstrings)
5. **Validate**: Run `uv run pytest && uv run ruff check .`

### Modifying Existing Code
1. **Read first**: Always read existing file before editing
2. **Preserve style**: Match indentation, naming, docstring format
3. **Update tests**: Modify corresponding test files
4. **Run validation**: `uv run pytest` to ensure tests pass
5. **Format**: `uv run ruff format .` before finalizing

### Common Patterns to Follow
```python
# Function with type hints and docstring
def process_data(input: str, validate: bool = True) -> dict:
    """Process input data and return structured result.
    
    Args:
        input: Raw input string
        validate: Whether to validate input (default: True)
    
    Returns:
        Dictionary with processed data
    """
    # Implementation
    return {"result": input}

# Test with clear naming
def test_process_data_valid_input():
    """Test process_data with valid input."""
    result = process_data("test")
    assert result["result"] == "test"
```

### Quick Reference Commands
```bash
# Setup project
uv sync --extra dev

# Development cycle
uv run pytest              # Test
uv run ruff check .        # Lint
uv run ruff format .       # Format

# Run application
uv run python -m project

# Build distribution
uv build
```