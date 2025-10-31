# 🧮 3D Calculator

A beautiful 3D calculator web application built with Python and Flask.

## 📋 Project Structure

```
calculator-3d/
├── src/
│   └── calculator_3d/
│       ├── __init__.py
│       ├── main.py                 # Flask application entry point
│       ├── static/
│       │   ├── css/                # CSS stylesheets for 3D effects
│       │   └── js/                 # JavaScript for calculator logic
│       └── templates/              # HTML templates
├── tests/
│   └── __init__.py
├── pyproject.toml                  # Project configuration and dependencies
├── README.md
└── .gitignore
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11 or higher
- [uv](https://github.com/astral-sh/uv) package manager

### Installation

1. **Install uv** (if not already installed):
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. **Clone or navigate to the project directory**:
```bash
cd calculator-3d
```

3. **Install dependencies with uv**:
```bash
uv sync
```

This will create a virtual environment and install all dependencies.

### Running the Application

#### Option 1: Using the installed command
```bash
uv run calculator-3d
```

#### Option 2: Running directly
```bash
uv run python -m calculator_3d.main
```

#### Option 3: Using the module directly
```bash
uv run python src/calculator_3d/main.py
```

The application will start on `http://localhost:5000`

## 🛠️ Development

### Install development dependencies
```bash
uv sync --extra dev
```

### Running tests
```bash
uv run pytest
```

### Code formatting
```bash
uv run black src/ tests/
```

### Code linting
```bash
uv run ruff check src/ tests/
```

## 📦 Building

To build the package:
```bash
uv build
```

## 🎯 Next Steps

The project structure is ready! You can now:

1. **Create HTML templates** in `src/calculator_3d/templates/`
   - Design the calculator interface with 3D elements

2. **Add CSS** in `src/calculator_3d/static/css/`
   - Implement 3D styling with CSS transforms and animations

3. **Add JavaScript** in `src/calculator_3d/static/js/`
   - Implement calculator logic and 3D interactions

4. **Add API routes** in `src/calculator_3d/main.py`
   - Create endpoints for calculator operations if needed

## 📝 License

This project is open source and available under the MIT License.
