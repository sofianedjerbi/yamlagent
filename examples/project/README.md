# 3D Calculator 🧮

A beautiful, modern 3D calculator web application built with Python and Flask.

## Features

- ✨ Stunning 3D visual design with glassmorphism effects
- 🎨 Smooth animations and hover effects
- ⌨️ Full keyboard support
- 📱 Responsive design for all devices
- 🚀 Fast and lightweight
- 🔢 Basic arithmetic operations (+, -, ×, ÷)
- 📐 Power operations (x²)
- 🎯 Clean, intuitive interface

## Prerequisites

- Python 3.11 or higher
- [uv](https://github.com/astral-sh/uv) package manager

### Installing uv

If you don't have `uv` installed:

```bash
# On macOS and Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# On Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

## Installation

1. Clone or navigate to the project directory:

```bash
cd calculator-3d
```

2. Install dependencies using uv:

```bash
uv sync
```

This will create a virtual environment and install all required dependencies.

## Usage

### Running the application

Start the calculator web server:

```bash
uv run calculator-3d
```

Or alternatively:

```bash
uv run python -m calculator_3d.app
```

The application will start on `http://localhost:5000`

Open your browser and navigate to the URL shown in the terminal.

### Keyboard Shortcuts

- **Numbers (0-9)**: Input numbers
- **Operators (+, -, *, /)**: Perform operations
- **Enter**: Calculate result
- **Backspace**: Delete last character
- **Escape**: Clear all

### Configuration

You can customize the application using environment variables:

```bash
# Change the port (default: 5000)
PORT=8080 uv run calculator-3d

# Enable debug mode
DEBUG=true uv run calculator-3d
```

## Development

### Project Structure

```
calculator-3d/
├── src/
│   └── calculator_3d/
│       ├── __init__.py
│       ├── app.py                 # Flask application
│       ├── static/
│       │   ├── css/
│       │   │   └── style.css      # 3D styling
│       │   └── js/
│       │       └── calculator.js  # Calculator logic
│       └── templates/
│           └── index.html         # Main HTML template
├── tests/
├── pyproject.toml                 # Project configuration
└── README.md
```

### Installing Development Dependencies

```bash
uv sync --extra dev
```

### Running Tests

```bash
uv run pytest
```

### Code Formatting

Format code with Black:

```bash
uv run black src/
```

Lint code with Ruff:

```bash
uv run ruff check src/
```

## Building for Production

To build the package:

```bash
uv build
```

This creates distribution packages in the `dist/` directory.

## License

This project is open source and available under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

Built with ❤️ using Python, Flask, and modern web technologies.
