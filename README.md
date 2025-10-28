# Playfile

AI-powered development workflows defined in YAML.

## Quick Start

```bash
# Install
uv sync

# Initialize a new project with default setup
pf init

# List available tasks
pf list

# Run a task
pf run code --prompt "Create a Python function to calculate fibonacci numbers"

# Try the interactive playground
cd examples/project
python play.py

# Or run tasks directly
cd examples/simple
uv run pf run greet --prompt "Say hello!"

# Without --prompt, it will ask interactively
uv run pf run greet
```

## Project Structure

```
playfile/
├── packages/
│   ├── playfile-core/      # Configuration system (tools, agents, workflows)
│   ├── playfile-cli/       # CLI with Claude SDK integration
│   └── playfile-utils/     # Shared utilities
├── examples/               # Example configurations
│   ├── simple/            # Minimal getting started example
│   ├── project/           # Interactive Python playground
│   ├── config.yaml        # Full example with imports
│   └── usage_example.py   # Python API usage
├── playfile.yaml          # Project configuration (auto-discovered)
└── pyproject.toml         # Workspace configuration
```

## Features

- **Project Initialization** - `pf init` creates a complete setup with best practices
- **YAML Configuration** - Define tools, agents, and workflows
- **Import System** - Split config across multiple files
- **Auto-discovery** - Finds `playfile.yaml` at git root from any subdirectory
- **Multiple Inputs** - Inline, stdin, or file
- **Claude SDK** - Agent execution via claude-agent-sdk
- **Rich Output** - Beautiful terminal UI

## Commands

### `pf init`

Initialize a new Playfile project with a general coding setup:

```bash
pf init                    # Initialize in current directory
pf init --path ./my-project # Initialize in specific directory
pf init --force            # Overwrite existing files
```

Creates:
- `playfile.yaml` - Main entry file with task definitions
- `.play/agents.yaml` - Agent definitions (coder, reviewer, documenter, test-writer)
- `.play/tools.yaml` - Tool configurations (git, python, npm, etc.)
- `.play/agents/*.md` - Instruction files for each agent

Default tasks included:
- `code` - Write or modify code
- `review` - Review code for quality
- `refactor` - Refactor code with review
- `document` - Generate documentation
- `test` - Write tests

### `pf create agent`

Create a custom agent using Claude's intelligence:

```bash
pf create agent <name> "<instructions>"
pf create agent security "Audit code for security vulnerabilities"
pf create agent optimizer "Optimize code performance"
pf create agent api-designer "Design RESTful APIs following best practices"
```

Claude intelligently generates:
- **Explores your project first** - Reads your code, configs, and documentation
- Complete agent configuration (role, model, tools, limits)
- **Project-specific instructions** - Tailored to your tech stack, patterns, and tools
- Appropriate tool access based on what the agent needs to do

The agent is automatically added to `.play/agents.yaml` and instructions saved to `.play/agents/<agent-id>.md`.

**Example**: Creating a "monorepo-navigator" agent in this project produces instructions that specifically mention the Playfile workspace structure, the 3 packages (playfile-core, playfile-cli, playfile-utils), uv build system, and actual architectural patterns found in the code!

### `pf run`

Execute a workflow task:

```bash
pf run <task-id> --prompt "Your prompt"
pf run code --prompt "Create a REST API"
cat requirements.txt | pf run review --prompt -
```

### `pf list`

List available tasks, agents, and tools:

```bash
pf list              # List tasks (default)
pf list --agents     # List agents
pf list --tools      # List tools
```

## Examples

### Interactive Playground

```bash
cd examples/project
python play.py
```

An interactive TUI for testing agents with Python development tasks:
- Write code with the `coder` agent
- Review code with the `reviewer` agent
- Learn with the `explainer` agent
- Multi-step workflows

### Simple Example

```bash
cd examples/simple
pf run greet --prompt "Say hello!"
```

The most minimal Playfile configuration - perfect for getting started.

### Full Examples

See `examples/` directory for:
- `config.yaml` - Complete example with imports
- `usage_example.py` - Python API usage
- More YAML configurations
