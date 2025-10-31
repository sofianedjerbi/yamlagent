# Project Guidelines

## Code Organization
- src/calculator_3d/: Flask app with main.py, static/, and templates/
- tests/: pytest test files
- pyproject.toml: dependencies and configuration

## Key Patterns
- Flask factory pattern with create_app()
- Static file serving for CSS/JS frontend
- Template rendering for HTML pages

## Conventions
- Naming: snake_case for Python modules and functions
- Testing: pytest in tests/ directory
- Commands: uv sync (install), uv run pytest (test), uv run calculator-3d (run)
- Formatting: black (line-length 88), ruff linting
