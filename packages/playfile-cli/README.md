# Playfile CLI

CLI for executing AI-powered development workflows defined in YAML.

## Installation

```bash
uv sync
```

## Usage

```bash
# Inline prompt
pf run implement-feature --prompt "Feature X: Apple Pay + retries"

# From stdin
cat specs.md | pf run implement-feature --prompt -

# From file
pf run implement-feature --prompt @specs.md

# List tasks
pf list

# List agents/tools
pf list --agents --tools
```

## Configuration

Place `playfile.yaml` at your project root. The CLI auto-discovers it from any subdirectory.

## Architecture

- `executor.py` - Claude SDK agent execution
- `task_runner.py` - Workflow orchestration
- `config_loader.py` - Auto-discovery from git root
- `input_reader.py` - Stdin/file/inline input
- `commands/` - CLI commands (run, list)

Clean, SOLID, DRY - ~600 lines total.
