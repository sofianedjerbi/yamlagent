# yamlagent-core

Core package for yamlagent - provides domain models and YAML parsing for agent configurations and tool definitions.

## Features

- **YAML Configuration Parsers**: Parse both agent and tool configurations from YAML files or strings
- **Domain Models**: Type-safe, immutable data classes for agents, commands, and MCP servers
- **Access Control**: Whitelist/blacklist mode for agent tool permissions
- **Resource Limits**: Runtime and iteration limits for agent execution
- **Validation**: Comprehensive validation of configuration data
- **SOLID Principles**: Clean architecture following Single Responsibility, Open/Closed, and Dependency Injection
- **Type Safety**: Full type hints with strict pyright checking
- **Error Handling**: Custom exceptions for clear error reporting

## Installation

```bash
uv add yamlagent-core
```

## Usage

### Parsing Agent Configurations

```python
from yamlagent_core import AgentsConfigParser

# Parse agents from YAML string
parser = AgentsConfigParser()
agents_config = parser.parse("""
agents:
  - id: fe-impl
    role: "Frontend Implementation"
    instructions: ./agents/frontend.md
    model: claude-code
    tools:
      mode: whitelist
      commands: ["git", "npm", "sed"]
      mcp: ["fs", "gitmcp", "web"]
    limits:
      runtime: "25m"
      iterations: 6
""")

# Parse from file
agents_config = parser.parse_file("agents.yaml")

# Access agents
agent = agents_config.get_agent("fe-impl")
if agent:
    print(f"Role: {agent.role}")
    print(f"Model: {agent.model}")

    # Check permissions
    print(f"Can use git: {agent.is_command_allowed('git')}")
    print(f"Can use fs MCP: {agent.is_mcp_allowed('fs')}")
```

### Parsing Tool Definitions

```python
from yamlagent_core import AgentToolsParser

# Parse tool definitions from YAML string
parser = AgentToolsParser()
tools = parser.parse("""
version: 1
tools:
  commands:
    - id: git
      bin: git
      args_allow: ["clone", "push"]
      timeout: "5m"
  mcp:
    - id: fs
      transport: stdio
      command: ["node", "mcp/fs-server.js"]
      calls: ["fs.read", "fs.write"]
""")

# Parse from file
tools = parser.parse_file("tools.yaml")

# Access tools
git_cmd = tools.get_command("git")
if git_cmd:
    print(f"Binary: {git_cmd.bin}")
    print(f"Allowed args: {git_cmd.args_allow}")
```

## Architecture

The package follows SOLID principles with separated concerns:

### Agent Domain Models (`agent_models.py`)

- **Agent**: Represents an agent with role, model, instructions, tools, and limits
- **AgentToolsConfig**: Tools access control (whitelist/blacklist mode)
- **AgentLimits**: Resource limits (runtime, iterations)
- **AgentsConfig**: Container for all agent configurations
- **ToolsMode**: Enum for whitelist/blacklist modes

### Tool Domain Models (`models.py`)

- **Command**: Represents command-line tool configuration
- **MCP**: Represents Model Context Protocol server configuration
- **AgentTools**: Container for all tools configuration

All models are:
- Immutable (frozen dataclasses)
- Type-safe with full annotations
- Self-validating in `__post_init__`

### Agent Parser (`agent_parser.py`)

Follows Single Responsibility Principle with specialized parsers:

- **YAMLAgentLoader**: Handles YAML loading and basic validation
- **AgentToolsConfigParser**: Parses agent tools configuration
- **AgentLimitsParser**: Parses agent limits configuration
- **AgentConfigParser**: Parses individual agent configurations
- **AgentsConfigParser**: Orchestrates agent parsing (main entry point)

### Tool Parser (`parser.py`)

Follows Single Responsibility Principle with specialized parsers:

- **YAMLLoader**: Handles YAML loading and basic validation
- **CommandParser**: Parses command configurations
- **MCPParser**: Parses MCP server configurations
- **AgentToolsParser**: Orchestrates tool parsing (main entry point)

### Exceptions (`exceptions.py`)

- **YamlAgentError**: Base exception
- **ParseError**: YAML parsing failures
- **ValidationError**: Configuration validation failures

## Configuration Schemas

### Agent Configuration

```yaml
agents:  # List of agent configurations
  - id: string              # Required, unique identifier
    role: string            # Required, description of agent's role
    model: string           # Required, model identifier (e.g., "claude-code")
    instructions: string    # Required, file path or inline instructions

    tools:                  # Optional, access control for tools
      mode: string          # "whitelist" or "blacklist" (default: "whitelist")
      commands: [...]       # List of command IDs
      mcp: [...]            # List of MCP server IDs

    limits:                 # Optional, resource limits
      runtime: string       # Max runtime (e.g., "25m", "1h")
      iterations: number    # Max iterations (must be >= 1)
```

### Tool Configuration

```yaml
version: 1  # Required, must be >= 1
tools:
  commands:  # Optional list
    - id: string          # Required, unique identifier
      bin: string         # Required, executable name
      args_allow: [...]   # Optional, allowed arguments
      timeout: string     # Optional, e.g., "5m", "10s"

  mcp:  # Optional list
    - id: string          # Required, unique identifier
      transport: string   # Required, e.g., "stdio"
      command: [...]      # Required, command to start server
      calls: [...]        # Optional, API calls this server exposes
```

## Development

### Running Tests

```bash
# Run all tests (104 tests: 62 agent tests + 42 tool tests)
uv run pytest tests/ -v

# Run with coverage
uv run pytest tests/ --cov=yamlagent_core
```

### Code Quality

```bash
# Run linter
uv run ruff check .

# Run type checker
uv run pyright

# Auto-fix issues
uv run ruff check --fix .
```

## Design Principles

### KISS (Keep It Simple, Stupid)

- Each class has a single, clear purpose
- Simple, straightforward API
- Minimal dependencies (only PyYAML)

### SOLID

- **Single Responsibility**: Each parser class handles one type of configuration
- **Open/Closed**: Easy to extend with new parsers without modifying existing code
- **Dependency Injection**: AgentToolsParser accepts custom parser instances

### DRY (Don't Repeat Yourself)

- Shared validation logic in base models
- Reusable parser components
- Common error handling patterns

## License

MIT
