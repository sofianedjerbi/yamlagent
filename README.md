# YamlAgent

## Project Structure

```
yamlagent/
├── src/yamlagent/           # Main CLI application entry point
├── packages/                # Workspace packages (monorepo)
│   ├── yamlagent-core/      # Core business logic and data processing
│   └── yamlagent-utils/     # Shared utilities and helper functions
├── tests/                   # Test files for all packages
└── pyproject.toml           # Project configuration and dependencies
```

### Directory Purposes

- **src/yamlagent/** - Main CLI application using Typer. Contains command definitions and user interface logic.

- **packages/yamlagent-core/** - Core business logic. Contains domain models, data processing, and main application functionality.

- **packages/yamlagent-utils/** - Reusable utilities. Contains helper functions, formatters, and shared code used across packages.

- **tests/** - Test suite. Contains unit tests and integration tests for all packages.
