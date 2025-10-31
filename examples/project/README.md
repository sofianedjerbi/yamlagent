# Calc3D - Beautiful 3D Calculator

A modern, interactive 3D calculator web application built with Python and Flask.

## Features

- **Interactive 3D Calculator Interface** - Beautiful glassmorphism design with 3D perspective effects
- **Real-time Calculations** - Instant expression evaluation via Flask backend
- **Sound Effects** 🔊
  - Unique sounds for different button types (numbers, operators, functions, power operations)
  - Pleasant musical chord feedback on successful calculations
  - Error feedback sounds for invalid expressions
  - Easily toggle sound on/off with persistent settings
- **Visual Feedback**
  - Ripple animations on button press
  - Shimmer effect on successful calculations
  - Shake animation for errors
  - Smooth hover and active states
- **Keyboard Support** - Full keyboard navigation and input
- **Responsive Layout** - Works seamlessly on desktop and mobile devices

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
   - Click buttons or use your keyboard to input expressions
   - Press `=` or `Enter` to calculate
   - Press `C` or `Escape` to clear
   - Click the 🔊 icon to toggle sound effects on/off

### Sound Effects

The calculator includes immersive sound effects powered by the Web Audio API:

- **Numbers & Decimal (440 Hz)** - Clean, neutral tone
- **Operators (523 Hz)** - Slightly higher pitch for distinction
- **Functions & Parentheses (587 Hz)** - Unique function tone
- **Power Operations (698 Hz)** - Higher tone for advanced operations
- **Equals** - Pleasant C-E-G major chord (success arpeggio)
- **Clear** - Descending tone (880 Hz → 220 Hz)
- **Delete** - Quick, short beep (392 Hz)
- **Error** - Dissonant chord for immediate feedback

Sound settings are automatically saved to localStorage and persist across sessions.

## Project Structure

```
calc3d/
├── src/calc3d/          # Main application package
│   ├── __init__.py      # Package initialization
│   ├── app.py           # Flask application
│   ├── calculator.py    # Calculator logic
│   ├── static/          # Static assets
│   │   ├── css/
│   │   │   └── style.css      # UI styles with animations
│   │   └── js/
│   │       ├── app.js         # Main calculator logic
│   │       └── audio.js       # Sound manager (Web Audio API)
│   └── templates/       # HTML templates
│       └── index.html   # Main calculator interface
├── tests/               # Test suite
├── pyproject.toml       # Project configuration
└── README.md            # This file
```

## License

MIT
