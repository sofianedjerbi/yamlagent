"""Create command - creates custom agents, tasks, and tools."""

from __future__ import annotations

import asyncio
from pathlib import Path

import rich_click as click
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt

from playfile_cli.agent_builder import AgentBuilder
from playfile_cli.agent_builder.builder import AgentConfig, AgentWriter
from playfile_cli.commands.create_task import create_task
from playfile_cli.commands.create_tool import create_tool
from playfile_cli.config_loader import ConfigLoader


@click.group(name="create")
def create() -> None:
    """Create custom resources (agents, tasks, tools)"""


@create.command(name="agent")
@click.argument("name")
@click.argument("instructions", nargs=-1, required=True)
@click.option(
    "-c",
    "--config",
    "config_path",
    type=click.Path(exists=True, path_type=Path),
    help="Path to config file (default: playfile.yaml in project root)",
)
@click.option(
    "--model",
    default="claude-sonnet-4-20250514",
    help="Claude model to use for generation (default: claude-sonnet-4-20250514)",
)
def create_agent(
    name: str,
    instructions: tuple[str, ...],
    config_path: Path | None,
    model: str,
) -> None:
    """Create a custom agent using Claude's intelligence

    NAME is a simple identifier for the agent (will be converted to agent-id format)

    INSTRUCTIONS describe what the agent should do (can be multiple words)

    Claude will intelligently generate:
    - Complete agent configuration (role, model, tools, limits)
    - Detailed markdown instructions
    - Appropriate tool access based on requirements

    \b
    Examples:
      pf create agent security "Audit code for security vulnerabilities"
      pf create agent api-designer "Design RESTful APIs following best practices"
      pf create agent optimizer "Optimize code performance and reduce complexity"

    The agent will be added to .play/agents.yaml and instructions saved to
    .play/agents/<agent-id>.md
    """
    console = Console()

    try:
        # Get project root first
        if config_path:
            project_root = config_path.parent
        else:
            project_root = Path.cwd()

        # Load configuration to get available tools
        loader = ConfigLoader()
        config = loader.load(config_path)

        # Get available tools
        available_tools = []
        if config.tools and config.tools.commands:
            available_tools = [cmd.id for cmd in config.tools.commands]

        # Combine instructions
        user_instructions = f"Agent name: {name}\n\nRequirements: {' '.join(instructions)}"

        # Show what we're doing
        console.print()
        console.print(
            Panel(
                f"[bold]Creating custom agent:[/bold] {name}\n\n"
                f"[dim]Claude will explore your project and design the perfect agent...[/dim]",
                border_style="cyan",
            )
        )
        console.print()

        # Build agent with Claude (async)
        async def _build() -> AgentConfig:
            builder = AgentBuilder()
            return await builder.build_agent(
                user_instructions,
                available_tools,
                working_dir=str(project_root)
            )

        with console.status("[cyan]Claude is exploring your project and designing the agent...[/cyan]"):
            agent_config = asyncio.run(_build())

        # Display generated configuration
        console.print("[bold green]✓ Agent designed successfully![/bold green]")
        console.print()
        console.print("[bold]Generated Configuration:[/bold]")
        console.print(f"  ID:         {agent_config.id}")
        console.print(f"  Role:       {agent_config.role}")
        console.print(f"  Model:      {agent_config.model}")
        console.print(f"  Tools:      {agent_config.tools_mode} mode")
        console.print(f"  Commands:   {', '.join(agent_config.tools_commands)}")
        console.print(f"  Runtime:    {agent_config.runtime}")
        console.print(f"  Iterations: {agent_config.iterations}")
        console.print()

        # Show instructions preview
        instructions_preview = agent_config.instructions_content[:300]
        if len(agent_config.instructions_content) > 300:
            instructions_preview += "..."

        console.print("[bold]Instructions Preview:[/bold]")
        console.print(Panel(instructions_preview, border_style="dim"))
        console.print()

        # Write agent files
        with console.status("[cyan]Writing agent files...[/cyan]"):
            writer = AgentWriter(project_root)
            agents_yaml, instructions_file = writer.write_agent(agent_config)

        # Success
        console.print("[bold green]✓ Agent created successfully![/bold green]")
        console.print()
        console.print("[bold]Files updated:[/bold]")
        console.print(f"  [green]✓[/green] {agents_yaml.relative_to(project_root)}")
        console.print(
            f"  [green]✓[/green] {instructions_file.relative_to(project_root)}"
        )
        console.print()
        console.print("[bold]Next steps:[/bold]")
        console.print(
            f"  1. Review instructions: [cyan]{instructions_file.relative_to(project_root)}[/cyan]"
        )
        console.print(
            f"  2. Adjust configuration: [cyan]{agents_yaml.relative_to(project_root)}[/cyan]"
        )
        console.print(f"  3. Use in tasks: [cyan]use: {agent_config.id}[/cyan]")
        console.print()
        console.print("[dim]Tip: Run 'pf list --agents' to see all agents[/dim]")
        console.print()

    except FileNotFoundError as e:
        console.print(f"[bold red]✗ Error:[/bold red] {e}")
        console.print(
            "\n[dim]Tip: Run 'pf init' first to create the project structure[/dim]"
        )
        raise click.Abort from e
    except ValueError as e:
        console.print(f"[bold red]✗ Configuration error:[/bold red] {e}")
        raise click.Abort from e
    except RuntimeError as e:
        console.print(f"[bold red]✗ Error:[/bold red] {e}")
        raise click.Abort from e
    except Exception as e:
        console.print(f"[bold red]✗ Unexpected error:[/bold red] {e}")
        console.print_exception()
        raise click.Abort from e


# Register task and tool commands
create.add_command(create_task)
create.add_command(create_tool)
