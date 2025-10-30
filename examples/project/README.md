# Project

A clean Python project template.

## Setup

This project uses [uv](https://github.com/astral-sh/uv) for fast Python package management.

### Install dependencies

```bash
uv sync
```

### Install with dev dependencies

```bash
uv sync --extra dev
```

## Development

### Run the application

```bash
uv run python -m project
```

### Run tests

```bash
uv run pytest
```

### Format and lint

```bash
uv run ruff check .
uv run ruff format .
```

## Project Structure

```
project/
├── src/
│   └── project/
│       ├── __init__.py
│       └── __main__.py
├── tests/
│   └── test_example.py
├── pyproject.toml
├── README.md
└── .gitignore
```
