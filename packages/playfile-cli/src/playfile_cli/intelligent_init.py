"""Intelligent initialization - uses Claude to customize configuration for the project."""

from __future__ import annotations

import asyncio
from pathlib import Path

from playfile_core.agents.agent import Agent, AgentLimits, AgentToolsConfig, ToolsMode
from rich.console import Console

from playfile_cli.executor import AgentExecutor

# Agent configuration for customization
CUSTOMIZATION_AGENT = Agent(
    id="playfile-customizer",
    role="Playfile Configuration Specialist",
    model="claude-sonnet-4-5-20250929",
    instructions="""You specialize in project documentation and configuration.

CRITICAL: Follow ALL constraints in prompts exactly. If a prompt says "maximum 20 lines",
you MUST count lines and stop at 20. Exceeding limits is a failure.

Use the Write tool to create files directly. Do not output content in chat.""",
    tools=AgentToolsConfig(mode=ToolsMode.WHITELIST, commands=["Write", "Read", "Glob"]),
    limits=AgentLimits(runtime="5m", iterations=20),
)

# Agent configuration for project setup
SETUP_AGENT = Agent(
    id="project-setup",
    role="Project Setup Specialist",
    model="claude-sonnet-4-5-20250929",
    instructions="""Create clean, minimal, working projects following official conventions.

CRITICAL:
- Research standard project structure for the language/framework
- Package names must match directory structure
- Include all required config files (build, deps, etc.)
- Project MUST build/install successfully
- Keep it simple and production-ready""",
    tools=AgentToolsConfig(mode=ToolsMode.BLACKLIST, commands=[]),
    limits=AgentLimits(runtime="5m", iterations=30),
)


async def customize_for_project_async(project_dir: Path, console: Console) -> None:
    """Customize the generated playfile configuration for the specific project.

    Args:
        project_dir: Directory where playfile.yaml was initialized
        console: Rich console for output
    """
    console.print("[dim]Analyzing project structure...[/dim]")

    project_context = analyze_project(project_dir)
    console.print(f"[dim]Detected: {project_context['project_type']}[/dim]")
    console.print()

    # Generate project.md for agent context
    await _generate_project_md(project_dir, project_context, console)

    playfile_path = project_dir / "playfile.yaml"
    current_content = playfile_path.read_text()

    # Retry up to 3 times
    for attempt in range(1, 4):
        if attempt > 1:
            console.print(f"\n[dim]Retry attempt {attempt}/3...[/dim]\n")

        try:
            customized_yaml = await _query_claude_for_customization(
                project_dir, project_context, current_content, console
            )

            if customized_yaml and _validate_yaml_structure(customized_yaml):
                playfile_path.write_text(customized_yaml)
                console.print("\n[green]✓ Customized playfile.yaml[/green]")
                _show_detected_settings(console, project_context)
                return

        except Exception as e:
            if attempt == 3:
                console.print(f"\n[yellow]⚠ Customization failed: {e}[/yellow]")
                console.print("[dim]Using default configuration.[/dim]")
                return

    console.print("\n[yellow]⚠ Could not customize configuration after 3 attempts[/yellow]")
    console.print("[dim]Using default configuration.[/dim]")


async def _generate_project_md(
    project_dir: Path, context: dict, console: Console
) -> None:
    """Generate project context files for agent awareness.

    Args:
        project_dir: Project directory
        context: Project context from analysis
        console: Rich console for output
    """
    console.print("[dim]Generating project context...[/dim]")

    # Build prompt for file generation
    files_list = "\n".join(f"- {f}" for f in context.get("files", [])[:30])

    prompt = f"""Create concise project documentation files analyzing this project.

PROJECT CONTEXT:
- Type: {context['project_type']}
- Package manager: {context.get('package_manager', 'unknown')}
- Test command: {context.get('test_command', 'unknown')}
- Build command: {context.get('build_command', 'unknown')}

FILES IN PROJECT:
{files_list}

Create these files using the Write tool:

1. `.play/project/overview.md`:
   Header: "# Project Overview"
   Content: 2-3 sentences ONLY describing what this project does

2. `.play/project/guidelines.md`:
   Header: "# Project Guidelines"

   CRITICAL CONSTRAINT: MAXIMUM 20 LINES TOTAL (including header).
   If you exceed 20 lines, you have FAILED.

   Use ONLY bullet points. NO prose, NO examples, NO explanations.

   ## Code Organization
   - Main directories (1 line each, max 3 items)

   ## Key Patterns
   - Core abstractions (max 3 bullet points)

   ## Conventions
   - Naming: brief convention
   - Testing: where and how
   - Commands: install/test/build

   Example of correct length (20 lines):
   # Project Guidelines
   ## Code Organization
   - src/: main code
   - tests/: test files
   ## Key Patterns
   - MVC architecture
   - Dependency injection
   ## Conventions
   - Naming: snake_case for functions
   - Testing: pytest in tests/
   - Commands: uv run pytest

   STOP AT 20 LINES. Count your lines before writing."""

    try:
        executor = AgentExecutor(tools=None, console=console)
        await executor.execute(
            agent=CUSTOMIZATION_AGENT,
            prompt=prompt,
            working_dir=str(project_dir),
            files=None,
        )

        # Verify files were created
        project_ctx_dir = project_dir / ".play" / "project"
        overview_file = project_ctx_dir / "overview.md"
        guidelines_file = project_ctx_dir / "guidelines.md"

        if overview_file.exists():
            console.print("[green]✓ Generated project overview[/green]")
        if guidelines_file.exists():
            console.print("[green]✓ Generated project guidelines[/green]")

        if not overview_file.exists() and not guidelines_file.exists():
            console.print("[yellow]⚠ Could not generate project context[/yellow]")

    except Exception as e:
        console.print(f"[yellow]⚠ Failed to generate project context: {e}[/yellow]")


async def _query_claude_for_customization(
    project_dir: Path, context: dict, current_yaml: str, console: Console
) -> str | None:
    """Query Claude agent to customize the YAML with live feedback.

    Args:
        project_dir: Project directory
        context: Project context
        current_yaml: Current YAML content
        console: Rich console for output

    Returns:
        Customized YAML or None
    """
    prompt = _build_customization_prompt(context, current_yaml)

    executor = AgentExecutor(tools=None, console=console)
    response = await executor.execute(
        agent=CUSTOMIZATION_AGENT,
        prompt=prompt,
        working_dir=str(project_dir),
        files=None,
    )

    return extract_yaml_from_response(response) if response else None


def _validate_yaml_structure(yaml_content: str) -> bool:
    """Validate that YAML has required structure and validation blocks are uncommented.

    Args:
        yaml_content: YAML content to validate

    Returns:
        True if valid
    """
    # Check basic structure
    if not (
        yaml_content.startswith("version:")
        and "tasks:" in yaml_content
        and "imports:" in yaml_content
    ):
        return False

    # Check that validation blocks are uncommented (not "# validate:")
    # Count commented vs uncommented validate blocks
    commented_validate = yaml_content.count("# validate:")
    uncommented_validate = yaml_content.count("\n  validate:")  # Proper indentation

    # If there are commented validate blocks but no uncommented ones, validation failed
    if commented_validate > 0 and uncommented_validate == 0:
        return False

    return True


def _show_detected_settings(console: Console, context: dict) -> None:
    """Show detected project settings.

    Args:
        console: Rich console
        context: Project context
    """
    if context.get("test_command"):
        console.print(f"  [dim]Test command:[/dim] {context['test_command']}")
    if context.get("build_command"):
        console.print(f"  [dim]Build command:[/dim] {context['build_command']}")


def customize_for_project(project_dir: Path, console: Console) -> None:
    """Synchronous wrapper for customize_for_project_async.

    Args:
        project_dir: Directory where playfile.yaml was initialized
        console: Rich console for output
    """
    asyncio.run(customize_for_project_async(project_dir, console))


def setup_project_with_claude(project_dir: Path, instructions: str, console: Console) -> None:
    """Setup a new project using Claude agent.

    Args:
        project_dir: Directory to setup project in
        instructions: User instructions for project setup
        console: Rich console for output
    """
    asyncio.run(_setup_project_async(project_dir, instructions, console))


async def _setup_project_async(project_dir: Path, instructions: str, console: Console) -> None:
    """Setup project using Claude agent SDK with live feedback.

    Args:
        project_dir: Directory to setup project in
        instructions: User instructions for project setup
        console: Rich console for output
    """
    prompt = f"""Setup a new project based on these instructions:

{instructions}

WORKING DIRECTORY: . (current directory)

You will create all files and directories in the current working directory.

CRITICAL: Create a COMPLETE, WORKING project following official conventions.

Requirements:
- Research the standard project structure for the language/framework
- Ensure package names match directory names (e.g., Python: src/package_name/, not just src/)
- Include all required configuration files (build system, dependencies, etc.)
- The project MUST build/install successfully after creation
- Follow official best practices and conventions for the ecosystem

Keep it simple, minimal, and production-ready."""

    try:
        executor = AgentExecutor(tools=None, console=console)
        await executor.execute(
            agent=SETUP_AGENT,
            prompt=prompt,
            working_dir=str(project_dir),
            files=None,
        )

        console.print("\n[green]✓ Project setup complete[/green]")

    except Exception as e:
        msg = f"Project setup failed: {e}"
        raise RuntimeError(msg) from e


def analyze_project(project_dir: Path) -> dict:
    """Analyze the project to understand its structure and tooling.

    Args:
        project_dir: Project directory

    Returns:
        Dictionary with project context
    """
    context = {
        "project_type": "unknown",
        "files": [],
        "test_command": None,
        "build_command": None,
        "package_manager": None,
    }

    # List files in project
    files = []
    for item in project_dir.iterdir():
        if item.name.startswith(".") and item.name not in [".play", ".git"]:
            continue
        if item.is_file():
            files.append(item.name)
        elif item.is_dir() and not item.name.startswith("."):
            files.append(f"{item.name}/")

    context["files"] = files[:50]  # Limit to first 50

    # Detect project type and commands
    if (project_dir / "package.json").exists():
        context["project_type"] = "Node.js/JavaScript"
        context["package_manager"] = detect_node_package_manager(project_dir)
        context["test_command"] = f"{context['package_manager']} test"
        context["build_command"] = f"{context['package_manager']} run build"

    elif (project_dir / "pyproject.toml").exists() or (project_dir / "setup.py").exists():
        context["project_type"] = "Python"

        # Check for specific test frameworks
        pytest_ini_exists = (project_dir / "pytest.ini").exists()
        pyproject_content = (project_dir / "pyproject.toml").read_text()
        has_pytest = pytest_ini_exists or "pytest" in pyproject_content

        if has_pytest:
            context["test_command"] = "pytest"
        else:
            context["test_command"] = "python -m pytest"

        # Check for build tools
        pyproject = project_dir / "pyproject.toml"
        if pyproject.exists():
            content = pyproject.read_text()
            if "uv" in content or (project_dir / "uv.lock").exists():
                context["package_manager"] = "uv"
                context["test_command"] = "uv run pytest"
            elif "poetry" in content:
                context["package_manager"] = "poetry"
                context["test_command"] = "poetry run pytest"

    elif (project_dir / "Cargo.toml").exists():
        context["project_type"] = "Rust"
        context["test_command"] = "cargo test"
        context["build_command"] = "cargo build"

    elif (project_dir / "go.mod").exists():
        context["project_type"] = "Go"
        context["test_command"] = "go test ./..."
        context["build_command"] = "go build"

    elif (project_dir / "Makefile").exists():
        context["project_type"] = "Make-based project"
        context["test_command"] = "make test"
        context["build_command"] = "make build"

    return context


def detect_node_package_manager(project_dir: Path) -> str:
    """Detect which Node.js package manager is used.

    Args:
        project_dir: Project directory

    Returns:
        Package manager command (npm, yarn, pnpm, bun)
    """
    if (project_dir / "bun.lockb").exists():
        return "bun"
    elif (project_dir / "pnpm-lock.yaml").exists():
        return "pnpm"
    elif (project_dir / "yarn.lock").exists():
        return "yarn"
    else:
        return "npm"


def _build_customization_prompt(context: dict, current_yaml: str) -> str:
    """Build customization prompt with YAML schema and validation requirements.

    Args:
        context: Project context from analysis
        current_yaml: Current playfile.yaml content

    Returns:
        Prompt for Claude
    """
    test_cmd = context.get('test_command', 'make test')
    files_list = ", ".join(context.get('files', [])[:20])  # First 20 files

    return f"""Customize this Playfile configuration for the detected project.

WORKING DIRECTORY: . (current directory)

PROJECT CONTEXT:
- Type: {context['project_type']}
- Test command: {test_cmd}
- Build command: {context.get('build_command', 'unknown')}
- Package manager: {context.get('package_manager', 'unknown')}
- Files in project: {files_list}

CURRENT YAML:
```yaml
{current_yaml}
```

YAML SCHEMA (must follow exactly):
- version: 1
- imports: [list of .play/*.yaml files]
- tasks: [list of task objects with id, description, working_dir, files, steps]
- Each step has: agent (with use, with), optional validate (with command, max_retries)

CRITICAL CUSTOMIZATION TASKS:
1. UNCOMMENT ALL validation blocks (remove the # comment markers)
2. Set command to: {test_cmd}
3. Keep max_retries as-is (2 or 3 depending on step)
4. Update file patterns for {context['project_type']} if needed
5. Maintain all step names and structure

EXAMPLE - Before:
```yaml
- name: "Create tests"
  agent:
    use: tester
    with:
      prompt: "..."
  # validate:
  #   command: "make test"
  #   max_retries: 2
```

EXAMPLE - After (UNCOMMENTED):
```yaml
- name: "Create tests"
  agent:
    use: tester
    with:
      prompt: "..."
  validate:
    command: "{test_cmd}"
    max_retries: 2
```

OUTPUT:
Return ONLY complete YAML starting with "version: 1".
NO markdown blocks, NO explanations.
ALL validation blocks MUST be uncommented.
"""


def extract_yaml_from_response(response_text: str) -> str | None:
    """Extract YAML content from Claude's response.

    Args:
        response_text: Response from Claude

    Returns:
        Extracted YAML content or None
    """
    # Remove markdown code blocks if present
    text = response_text.strip()

    if "```yaml" in text:
        # Extract from code block
        start = text.find("```yaml") + 7
        end = text.find("```", start)
        if end != -1:
            return text[start:end].strip()

    if "```" in text:
        # Extract from generic code block
        start = text.find("```") + 3
        end = text.find("```", start)
        if end != -1:
            content = text[start:end].strip()
            # Check if it starts with version: 1
            if content.startswith("version:"):
                return content

    # If no code blocks, check if response is pure YAML
    if text.startswith("version:"):
        return text

    return None
