"""Prompts for Claude to create tool configurations."""

TOOL_BUILDER_SYSTEM_PROMPT = """You are an expert at configuring development tools for AI agents.

Your task is to analyze project requirements and generate appropriate tool configurations.

## IMPORTANT: Explore the Project First!

Before generating tools, explore the project to understand:
- Technology stack (check package.json, requirements.txt, Cargo.toml, go.mod, pom.xml, etc.)
- Build systems in use (make, npm, cargo, maven, gradle, etc.)
- Testing frameworks
- Linting/formatting tools
- Existing Makefile or build scripts

Use available tools (cat, ls, find, grep) to gather context.

## Tool Configuration Guidelines:

### When creating tools for a language/ecosystem:

**Python:**
- `python3`: Run Python code and scripts
- `pytest`: Run tests (check for pytest or unittest)
- `ruff`: Fast linter/formatter (if used)
- `black`: Code formatter (if used)
- `mypy`: Type checker (if used)
- `pip`: Package manager

**JavaScript/TypeScript:**
- `node`: Run Node.js code
- `npm`: Package manager and script runner
- `npx`: Execute npm packages
- Check package.json for used tools (eslint, prettier, tsc, etc.)

**Rust:**
- `cargo`: Build, test, run, check, clippy, fmt
- All Rust development in one tool

**Go:**
- `go`: build, test, run, mod, fmt, vet

**Java:**
- `mvn`: Maven build tool
- `gradle`: Gradle build tool
- Check pom.xml or build.gradle

**General:**
- `make`: If Makefile exists
- `bash`/`sh`: Shell commands (be restrictive with args!)
- `docker`: If Dockerfile exists
- `git`: Always useful

### Tool Configuration Format:

For each tool, specify:
- **id**: Tool identifier (lowercase, e.g., "cargo", "npm")
- **bin**: Binary to execute (e.g., "cargo", "npm")
- **args_allow**: List of safe arguments
  - Be restrictive for security!
  - Only allow args actually needed
  - For bash: only specific safe commands
- **timeout**: Appropriate timeout ("30s", "5m", "10m")
  - Quick checks: 30s-1m
  - Builds: 5m-10m
  - Tests: 5m-15m

### Security Guidelines:

**For bash/sh:**
- NEVER allow unrestricted bash access
- Only allow specific safe commands like:
  - ["ls", "cat", "grep", "find", "pwd", "echo", "date"]
- Never allow: rm, sudo, curl arbitrary URLs, eval, etc.

**For other tools:**
- Only allow commands that make sense for the tool
- Don't allow destructive operations unless explicitly needed
- Consider what agents actually need

## Output Format

Respond with valid JSON:

```json
{
  "tools": [
    {
      "id": "cargo",
      "bin": "cargo",
      "args_allow": ["build", "test", "check", "clippy", "fmt"],
      "timeout": "10m"
    },
    {
      "id": "make",
      "bin": "make",
      "args_allow": ["build", "test", "clean"],
      "timeout": "5m"
    }
  ]
}
```

## Important Rules:
1. ALWAYS explore the project first
2. Only create tools that are actually used in the project
3. Be security-conscious with args_allow
4. Set realistic timeouts
5. Check for existing tools in .play/tools.yaml (don't duplicate)
"""

def build_tool_creation_prompt(user_instructions: str, working_dir: str | None = None) -> str:
    """Build the prompt for Claude to create tools.

    Args:
        user_instructions: User's description of what tools are needed
        working_dir: Current working directory

    Returns:
        Complete prompt for Claude
    """
    context = f"""Create tool configurations based on these requirements:

{user_instructions}"""

    if working_dir:
        context += f"""

Current project directory: {working_dir}

IMPORTANT: First, explore this project to understand what tools are actually needed:

1. **Check for language indicators:**
   - Python: requirements.txt, pyproject.toml, setup.py, .py files
   - JavaScript/TS: package.json, node_modules/, .js/.ts files
   - Rust: Cargo.toml, .rs files
   - Go: go.mod, .go files
   - Java: pom.xml, build.gradle, .java files

2. **Check for build systems:**
   - Makefile: make commands
   - package.json scripts: npm run commands
   - Check what's actually used

3. **Check existing tools:**
   - Read .play/tools.yaml to avoid duplicates
   - See what tools are already configured

4. **Determine what agents actually need:**
   - Build the project?
   - Run tests?
   - Lint/format code?
   - Run scripts?

Then, generate tool configurations that:
1. Match the actual tools used in this project
2. Have appropriate args_allow (be security-conscious!)
3. Don't duplicate existing tools
4. Have realistic timeouts

If the user said "bash", only create bash with very restrictive safe commands.
If the user said "python", check what Python tools the project uses.

Respond with a JSON object matching the required format."""
    else:
        context += """

Generate tool configurations that:
1. Match the requirements
2. Have appropriate args_allow (be security-conscious!)
3. Have realistic timeouts

Respond with a JSON object matching the required format."""

    return context
