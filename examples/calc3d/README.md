# Calc3D Example

A Flask-based calculator application built using Playfile's TDD workflow.

This example demonstrates how Playfile orchestrates multiple AI agents to build a complete feature from specification to implementation.

## What This Shows

**Complete TDD workflow in action:**
1. Software Architect creates technical specification
2. Test Engineer writes comprehensive tests
3. Software Developer implements the complete feature
4. Developer refactors following SOLID principles
5. Code Reviewer validates quality

**Context passing:**
Each agent gets exactly what they need. The coder sees both the architect's spec AND the test requirements, ensuring complete implementation.

**Validation checkpoints:**
Tests run automatically after implementation and refactoring, catching issues early.

## Project Structure

```
calc3d/
├── src/calc3d/
│   ├── api/                    # API routes and validators
│   ├── services/               # Business logic
│   ├── repositories/           # Data access layer
│   ├── models.py               # Data models
│   ├── constants.py            # Application constants
│   ├── app.py                  # Flask application factory
│   ├── templates/              # HTML templates
│   └── static/                 # CSS and JavaScript
├── tests/                      # Comprehensive test suite
├── playfile.yaml               # Workflow definitions
└── .play/                      # Agent and tool configurations
```

## Try It Out

```bash
# Install dependencies
uv sync

# Run the development server
python run.py

# Run tests
uv run pytest

# Build a feature with Playfile
pf run feature --prompt "Add calculation history"
```

## The Workflow

When you run `pf run feature`, here's what happens:

**Step 1: Architect designs**
Creates a detailed technical specification covering data models, API endpoints, file structure, and integration points.

**Step 2: Tester writes tests**
Receives the architect's spec and writes tests for all specified functionality.

**Step 3: Coder implements**
Gets both the spec and the tests. Implements EVERYTHING from the specification, not just what makes tests pass.

**Step 4: Refactor**
Improves code quality while keeping all functionality intact. Tests verify nothing breaks.

**Step 5: Review**
Final quality check for architecture, patterns, and test coverage.

## Key Features

**Backend:**
- RESTful API with Flask
- Clean architecture (services, repositories, models)
- Comprehensive error handling
- Input validation
- CORS support

**Frontend:**
- Responsive calculator interface
- Real-time calculations
- Error display
- Clean, modern UI

**Testing:**
- API endpoint tests
- Service layer tests
- Model validation tests
- Error handling tests
- 100% coverage of core functionality

## What Makes This Different

Most AI coding tools would give you either a backend OR frontend, maybe skip validation, probably forget error handling.

With Playfile's multi-agent workflow:
- The architect ensures nothing is forgotten
- The tester validates all paths
- The coder implements the complete spec
- The reviewer catches quality issues

You get a complete, production-ready implementation.

## Built With

- **Flask** for the web framework
- **pytest** for testing
- **uv** for dependency management
- **Playfile** for AI-orchestrated development

## Learn More

This example uses the default TDD workflow from `pf init`. You can customize every step, add new agents, change the workflow, or create entirely new processes.

Check the `playfile.yaml` to see the complete workflow definition.
