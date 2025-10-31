# Project Guidelines

## Code Organization
- `src/calc3d/` - Main application package (Flask app, calculator logic, templates, static assets)
- `tests/` - Test suite using pytest
- `pyproject.toml` - Project configuration and dependencies

## Key Patterns
- Flask web framework with JSON API endpoints
- Static Calculator class with operation mapping
- Expression evaluation with input validation
- Template-based rendering for UI

## Conventions
- **Naming**: Snake_case for files/functions, PascalCase for classes
- **Testing**: Tests in `tests/` directory, run with `uv run pytest`
- **Commands**: Install: `uv sync`, Test: `uv run pytest`, Run: `uv run calc3d`
