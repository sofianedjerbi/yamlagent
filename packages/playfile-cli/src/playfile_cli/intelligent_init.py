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
    instructions="""You are a technical writer specializing in project documentation.

CRITICAL: Output ONLY the requested content. NO explanations, NO thinking process, NO preamble.

When asked to write documentation:
- Write directly in the requested format
- Do NOT include "I'll analyze..." or "Let me..."
- Do NOT wrap in markdown code blocks
- Start immediately with the actual content""",
    tools=AgentToolsConfig(mode=ToolsMode.BLACKLIST, commands=[]),
    limits=AgentLimits(runtime="5m", iterations=20),
)

# Agent configuration for project setup
SETUP_AGENT = Agent(
    id="project-setup",
    role="Project Setup Specialist",
    model="claude-sonnet-4-5-20250929",
    instructions="Setup clean, minimal project with essential files and best practices.",
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

    # Build prompt for overview generation
    files_list = "\n".join(f"- {f}" for f in context.get("files", [])[:30])

    # Generate overview (very short)
    overview_prompt = f"""Write a 2-3 sentence project overview based on this context:

PROJECT CONTEXT:
- Type: {context['project_type']}
- Package manager: {context.get('package_manager', 'unknown')}
- Files: {', '.join(context.get('files', [])[:10])}

Output format: Just 2-3 sentences describing what this project does.
Example: "This is a web API built with FastAPI. It provides REST endpoints for
user management and authentication. The project uses PostgreSQL for data storage."

Write ONLY the sentences. Do NOT include thinking, explanations, or markdown blocks."""

    # Generate guidelines (best practices)
    guidelines_prompt = f"""Document this project's guidelines in markdown format.

PROJECT CONTEXT:
- Type: {context['project_type']}
- Package manager: {context.get('package_manager', 'unknown')}
- Test command: {context.get('test_command', 'unknown')}
- Build command: {context.get('build_command', 'unknown')}

FILES IN PROJECT:
{files_list}

Create a markdown document with these sections:

## Code Organization
(Directory structure and where code belongs)

## Naming Conventions
(Files, classes, functions, variables)

## Architecture Patterns
(Key abstractions and design patterns used)

## Development Workflow
(Install, test, build commands)

## Best Practices
(Code quality, testing, documentation)

Write ONLY the markdown document. Do NOT include thinking or code block wrappers."""

    try:
        executor = AgentExecutor(tools=None, console=console)

        # Generate overview
        overview_content = await executor.execute(
            agent=CUSTOMIZATION_AGENT,
            prompt=overview_prompt,
            working_dir=str(project_dir),
            files=None,
        )

        # Generate guidelines
        console.print("[dim]Generating project guidelines...[/dim]")
        guidelines_content = await executor.execute(
            agent=CUSTOMIZATION_AGENT,
            prompt=guidelines_prompt,
            working_dir=str(project_dir),
            files=None,
        )

        # Write files
        project_ctx_dir = project_dir / ".play" / "project"
        project_ctx_dir.mkdir(parents=True, exist_ok=True)

        if overview_content:
            overview_file = project_ctx_dir / "overview.md"
            overview_file.write_text(f"# Project Overview\n\n{overview_content.strip()}")
            console.print("[green]✓ Generated project overview[/green]")

        if guidelines_content:
            guidelines_file = project_ctx_dir / "guidelines.md"
            guidelines_file.write_text(guidelines_content.strip())
            console.print("[green]✓ Generated project guidelines[/green]")

        if not overview_content and not guidelines_content:
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
    """Validate that YAML has required structure.

    Args:
        yaml_content: YAML content to validate

    Returns:
        True if valid
    """
    return (
        yaml_content.startswith("version:")
        and "tasks:" in yaml_content
        and "imports:" in yaml_content
    )


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
- Each step has: agent (with use, with), optional validate (with post_command, max_retries)

CUSTOMIZATION TASKS:
1. UNCOMMENT validation blocks and set post_command to: {test_cmd}
2. Keep max_retries as-is (2 or 3 depending on step)
3. Update file patterns for {context['project_type']} if needed
4. Maintain all structure and comments

OUTPUT:
Return ONLY complete YAML starting with "version: 1".
NO markdown blocks, NO explanations.
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
