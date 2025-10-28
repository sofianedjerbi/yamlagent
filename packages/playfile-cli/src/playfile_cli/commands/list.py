# ruff: noqa: E501
"""List command - shows available tasks and agents."""

from __future__ import annotations

from pathlib import Path

import rich_click as click
from playfile_core.exceptions import ParseError
from rich.console import Console
from rich.table import Table

from playfile_cli.config_loader import ConfigLoader


@click.command(name="list")
@click.option(
    "-c",
    "--config",
    "config_path",
    type=click.Path(exists=True, path_type=Path),
    help="Path to config file (default: playfile.yaml in project root)",
)
@click.option(
    "--tasks",
    "show_tasks",
    is_flag=True,
    default=True,
    help="Show available tasks (default)",
)
@click.option(
    "--agents",
    "show_agents",
    is_flag=True,
    help="Show available agents",
)
@click.option(
    "--tools",
    "show_tools",
    is_flag=True,
    help="Show available tools",
)
def list_cmd(
    config_path: Path | None,
    show_tasks: bool,
    show_agents: bool,
    show_tools: bool,
) -> None:
    """List tasks, agents, and tools from playfile.yaml"""
    console = Console()

    try:
        # Load configuration
        loader = ConfigLoader()
        config = loader.load(config_path)

        # Show all if no specific flags
        if not show_agents and not show_tools:
            show_tasks = True

        # List tasks
        if show_tasks and config.workflows:
            table = Table(title="Available Tasks", show_header=True, header_style="bold cyan")
            table.add_column("Task ID", style="cyan")
            table.add_column("Description")
            table.add_column("Steps", justify="right")

            for task in config.workflows.tasks:
                table.add_row(task.id, task.description, str(len(task.steps)))

            console.print()
            console.print(table)

        # List agents
        if show_agents and config.agents:
            table = Table(title="Available Agents", show_header=True, header_style="bold green")
            table.add_column("Agent ID", style="green")
            table.add_column("Role")
            table.add_column("Model")

            for agent in config.agents.agents:
                table.add_row(agent.id, agent.role, agent.model)

            console.print()
            console.print(table)

        # List tools
        if show_tools and config.tools:
            # Commands table
            if config.tools.commands:
                table = Table(
                    title="Available Commands",
                    show_header=True,
                    header_style="bold yellow",
                )
                table.add_column("Command ID", style="yellow")
                table.add_column("Binary")
                table.add_column("Timeout")

                for cmd in config.tools.commands:
                    table.add_row(cmd.id, cmd.bin, cmd.timeout or "none")

                console.print()
                console.print(table)

            # MCP servers table
            if config.tools.mcp:
                table = Table(
                    title="Available MCP Servers",
                    show_header=True,
                    header_style="bold magenta",
                )
                table.add_column("MCP ID", style="magenta")
                table.add_column("Transport")
                table.add_column("Calls", justify="right")

                for mcp in config.tools.mcp:
                    table.add_row(mcp.id, mcp.transport, str(len(mcp.calls)))

                console.print()
                console.print(table)

        console.print()

    except ParseError as e:
        console.print(f"[bold red]✗ Configuration error:[/bold red] {e}")
        raise click.Abort from e
    except Exception as e:
        console.print(f"[bold red]✗ Error:[/bold red] {e}")
        raise click.Abort from e
