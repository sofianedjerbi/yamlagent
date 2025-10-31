# Calc3D - Beautiful 3D Calculator

A modern, interactive 3D calculator web application built with Python and Flask.

## Features

- Interactive 3D calculator interface
- Real-time calculations
- Beautiful, modern UI design
- Responsive layout

## Installation

This project uses [uv](https://github.com/astral-sh/uv) for dependency management.

```bash
# Install dependencies
uv sync

# Run the development server
uv run calc3d
```

## Development

```bash
# Install with dev dependencies
uv sync --all-extras

# Run tests
uv run pytest

# Format code
uv run ruff check --fix .
```

## Usage

1. Start the server:
   ```bash
   uv run calc3d
   ```

2. Open your browser and navigate to `http://localhost:5000`

3. Use the 3D calculator interface to perform calculations

## Project Structure

```
calc3d/
├── src/calc3d/          # Main application package
│   ├── __init__.py      # Package initialization
│   ├── app.py           # Flask application
│   ├── calculator.py    # Calculator logic
│   ├── static/          # Static assets (CSS, JS)
│   └── templates/       # HTML templates
├── tests/               # Test suite
├── pyproject.toml       # Project configuration
└── README.md            # This file
```

## License

MIT
