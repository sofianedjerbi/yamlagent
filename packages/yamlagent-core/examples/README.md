# YamlAgent Configuration Examples

This directory contains example configuration files demonstrating the unified YAML configuration system for yamlagent.

## Overview

The yamlagent configuration system supports a **unified, modular approach** where you can:

1. **Define everything in a single file** - All tools, agents, and workflows in one YAML
2. **Split across multiple files** - Separate concerns with imports
3. **Mix and match** - Import some sections, define others inline

## File Structure

```
examples/
├── config.yaml        # Main entry point with imports
├── tools.yaml         # Tool definitions (commands & MCP servers)
├── agents.yaml        # Agent configurations
├── usage_example.py   # Python usage demonstration
└── README.md          # This file
```

## Configuration Sections

### 1. Tools (`tools.yaml`)

Defines available commands and MCP servers:

```yaml
tools:
  commands:
    - id: git
      bin: git
      args_allow: ["clone", "push", "pull"]
      timeout: "5m"

  mcp:
    - id: fs
      transport: stdio
      command: ["node", "mcp/fs-server.js"]
      calls: ["fs.read", "fs.write"]
```

### 2. Agents (`agents.yaml`)

Defines agent configurations with roles, models, and permissions:

```yaml
agents:
  - id: fe-impl
    role: "Frontend Implementation Agent"
    model: claude-code
    instructions: |
      You are an expert frontend developer...
    tools:
      mode: whitelist
      commands: ["git", "npm"]
      mcp: ["fs", "gitmcp"]
    limits:
      runtime: "25m"
      iterations: 6
```

### 3. Workflows (`config.yaml`)

Defines tasks with multiple agent steps:

```yaml
tasks:
  - id: implement-feature
    description: "Implement a new feature"
    working_dir: "."
    files:
      read: ["**/*"]
      write: ["src/**/*"]
    steps:
      - agent:
          use: fe-impl
          with:
            prompt: "Build the UI..."
```

## Import System

The unified parser supports imports to organize configuration:

```yaml
# config.yaml
version: 1

imports:
  - ./tools.yaml
  - ./agents.yaml

tasks:
  - id: my-task
    # ... workflow definition
```

**Import Resolution:**
- Imports are resolved relative to the importing file's directory
- Multiple files can be imported
- Imported sections are merged (tools, agents, tasks are concatenated)
- Main file definitions are included alongside imports

## Usage

### Python API

```python
from yamlagent_core import YamlAgentConfigParser

# Parse configuration with imports
parser = YamlAgentConfigParser()
config = parser.parse_file("examples/config.yaml")

# Access all sections
print(f"Tools: {len(config.tools.commands)} commands")
print(f"Agents: {len(config.agents.agents)} agents")
print(f"Tasks: {len(config.workflows.tasks)} workflows")

# Query specific items
git_cmd = config.tools.get_command("git")
fe_agent = config.agents.get_agent("fe-impl")
task = config.workflows.get_task("implement-feature")

# Check agent permissions
if fe_agent.is_command_allowed("git"):
    print("Frontend agent can use git")
```

### Running the Example

```bash
cd /home/user/Documents/yamlagent/packages/yamlagent-core
uv run python examples/usage_example.py
```

## Configuration Patterns

### Pattern 1: Single File (Simple Projects)

```yaml
# all-in-one.yaml
version: 1

tools:
  commands:
    - id: git
      bin: git

agents:
  - id: dev-agent
    role: "Developer"
    model: claude-code
    instructions: "..."

tasks:
  - id: build
    description: "Build project"
    steps:
      - agent:
          use: dev-agent
```

### Pattern 2: Modular (Large Projects)

```
project/
├── config.yaml          # Main entry, imports everything
├── tools/
│   ├── dev-tools.yaml   # Development commands
│   └── ci-tools.yaml    # CI/CD commands
├── agents/
│   ├── frontend.yaml    # Frontend agents
│   └── backend.yaml     # Backend agents
└── workflows/
    └── tasks.yaml       # Task definitions
```

```yaml
# config.yaml
version: 1
imports:
  - ./tools/dev-tools.yaml
  - ./tools/ci-tools.yaml
  - ./agents/frontend.yaml
  - ./agents/backend.yaml
  - ./workflows/tasks.yaml
```

### Pattern 3: Hybrid (Flexibility)

```yaml
# config.yaml
version: 1

imports:
  - ./common-tools.yaml

# Additional tools specific to this config
tools:
  commands:
    - id: custom-script
      bin: ./scripts/custom.sh

agents:
  - id: special-agent
    role: "Special Purpose"
    model: gpt-4
    instructions: "..."
```

## Features

✅ **Import resolution** - Automatically merges imported configurations
✅ **Type safety** - Full validation with clear error messages
✅ **Modular design** - Organize by tools, agents, workflows
✅ **Flexible patterns** - Single file, multi-file, or hybrid
✅ **Path handling** - Automatic conversion of instruction file paths
✅ **Enum support** - Type-safe modes (whitelist/blacklist)
✅ **Default values** - Sensible defaults for optional fields
✅ **Query API** - Easy access to specific items

## Schema Reference

Complete schema with all available fields:

```yaml
version: 1  # Required

imports:  # Optional
  - ./path/to/import.yaml

tools:  # Optional
  commands:
    - id: string          # Required
      bin: string         # Required
      args_allow: []      # Optional
      timeout: string     # Optional (e.g., "5m", "1h")

  mcp:
    - id: string          # Required
      transport: stdio    # Required
      command: []         # Required (list of strings)
      calls: []           # Optional

agents:  # Optional
  - id: string            # Required
    role: string          # Required
    model: string         # Required
    instructions: string|path  # Required (inline or file path)
    tools:                # Optional
      mode: whitelist|blacklist  # Default: whitelist
      commands: []        # Optional
      mcp: []             # Optional
    limits:               # Optional
      runtime: string     # Optional (e.g., "25m")
      iterations: int     # Optional

tasks:  # Optional
  - id: string            # Required
    description: string   # Required
    working_dir: string   # Default: "."
    files:                # Optional
      read: []            # Glob patterns
      write: []           # Glob patterns
    steps:                # Default: []
      - agent:
          use: string     # Required (agent id)
          with:           # Optional parameters
            prompt: string
            # ... any other params
```

## Advanced Features

### Template Variables in Prompts

Use `{{ inputs.variable }}` in agent prompts:

```yaml
steps:
  - agent:
      use: fe-impl
      with:
        prompt: |
          Build UI for: {{ inputs.feature_name }}
          Requirements: {{ inputs.requirements }}
```

### Tool Permissions

Control agent access to commands and MCP servers:

```yaml
# Whitelist mode (only these tools allowed)
tools:
  mode: whitelist
  commands: ["git", "npm"]
  mcp: ["fs"]

# Blacklist mode (all except these allowed)
tools:
  mode: blacklist
  commands: ["rm", "dd"]  # Dangerous commands
  mcp: []
```

### Resource Limits

Prevent runaway agents:

```yaml
limits:
  runtime: "30m"      # Maximum execution time
  iterations: 10       # Maximum iterations
```

## Best Practices

1. **Organize by domain** - Separate tools, agents, and workflows
2. **Use descriptive IDs** - Clear, meaningful identifiers
3. **Document inline** - Use YAML comments and instruction fields
4. **Version control** - Track configuration changes
5. **Validate early** - Use the parser to catch errors
6. **Test incrementally** - Add one section at a time
7. **Secure by default** - Use whitelist mode for tools

## Error Handling

The parser provides clear error messages:

```python
try:
    config = parser.parse_file("config.yaml")
except ParseError as e:
    print(f"YAML parsing error: {e}")
except ValidationError as e:
    print(f"Configuration validation error: {e}")
```

Common errors:
- **Import file not found** - Check relative paths
- **Duplicate IDs** - Agent/tool IDs must be unique
- **Invalid mode** - Must be 'whitelist' or 'blacklist'
- **Missing required fields** - Check schema reference

## Testing

Run the comprehensive test suite:

```bash
uv run pytest tests/test_unified_parser.py -v
```

All 161 tests pass, covering:
- Single file configurations
- Multi-file imports
- Tools, agents, and workflows
- Validation and error handling
- Edge cases and defaults
