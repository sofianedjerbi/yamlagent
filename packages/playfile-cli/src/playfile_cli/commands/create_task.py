"""Create task command."""

from __future__ import annotations

import asyncio
from pathlib import Path

import rich_click as click
from rich.console import Console
from rich.panel import Panel

from playfile_cli.config_loader import ConfigLoader
from playfile_cli.task_builder import TaskBuilder
from playfile_cli.task_builder.builder import TaskWriter


@click.command(name="task")
@click.argument("name")
@click.argument("instructions", nargs=-1, required=True)
@click.option(
    "-c",
    "--config",
    "config_path",
    type=click.Path(exists=True, path_type=Path),
    help="Path to config file (default: playfile.yaml in project root)",
)
def create_task(
    name: str,
    instructions: tuple[str, ...],
    config_path: Path | None,
) -> None:
    """Create a custom workflow task using Claude's intelligence

    NAME is a simple identifier for the task

    INSTRUCTIONS describe what the task should accomplish

    Claude will intelligently generate:
    - Complete task configuration (description, file access, agent steps)
    - Logical workflow sequence using available agents
    - Appropriate file access patterns

    \b
    Examples:
      pf create task deploy "Deploy the application to production"
      pf create task test-fix "Run tests, fix failures, and rerun"
      pf create task api-docs "Generate API documentation from code"

    The task will be added to playfile.yaml
    """
    console = Console()

    try:
        # Get project root first
        if config_path:
            project_root = config_path.parent
        else:
            project_root = Path.cwd()

        # Load configuration to get available agents
        loader = ConfigLoader()
        config = loader.load(config_path)

        # Get available agents
        available_agents = []
        if config.agents:
            available_agents = [agent.id for agent in config.agents.agents]

        # Combine instructions
        user_instructions = f"Task name: {name}\n\nRequirements: {' '.join(instructions)}"

        # Show what we're doing
        console.print()
        console.print(
            Panel(
                f"[bold]Creating custom task:[/bold] {name}\n\n"
                f"[dim]Claude will explore your project and design the workflow...[/dim]",
                border_style="cyan",
            )
        )
        console.print()

        # Build task with Claude (async)
        async def _build():
            builder = TaskBuilder()
            return await builder.build_task(
                user_instructions,
                available_agents,
                working_dir=str(project_root)
            )

        with console.status("[cyan]Claude is exploring your project and designing the task...[/cyan]"):
            task_config = asyncio.run(_build())

        # Display generated configuration
        console.print("[bold green]✓ Task designed successfully![/bold green]")
        console.print()
        console.print("[bold]Generated Configuration:[/bold]")
        console.print(f"  ID:          {task_config.id}")
        console.print(f"  Description: {task_config.description}")
        console.print(f"  Steps:       {len(task_config.steps)}")
        console.print()

        # Show steps
        console.print("[bold]Workflow Steps:[/bold]")
        for i, step in enumerate(task_config.steps, 1):
            if "agent" in step:
                agent_id = step["agent"]["use"]
                console.print(f"  {i}. Agent: [cyan]{agent_id}[/cyan]")
        console.print()

        # Write task file
        with console.status("[cyan]Writing task to playfile.yaml...[/cyan]"):
            writer = TaskWriter(project_root)
            playfile_yaml = writer.write_task(task_config)

        # Success
        console.print("[bold green]✓ Task created successfully![/bold green]")
        console.print()
        console.print("[bold]File updated:[/bold]")
        console.print(f"  [green]✓[/green] {playfile_yaml.relative_to(project_root)}")
        console.print()
        console.print("[bold]Try it:[/bold]")
        console.print(f'  [cyan]pf run {task_config.id} --prompt "your request"[/cyan]')
        console.print()
        console.print("[dim]Tip: Run 'pf list' to see all tasks[/dim]")
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
