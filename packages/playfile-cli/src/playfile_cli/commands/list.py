# ruff: noqa: E501
"""List command - shows available tasks and agents."""

from __future__ import annotations

from pathlib import Path

import rich_click as click
from playfile_core.exceptions import ParseError
from rich.console import Console

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
            console.print()
            console.print("[bold cyan]📋 Available Tasks[/bold cyan]")
            console.print()

            for task in config.workflows.tasks:
                # Task header
                console.print(f"[bold cyan]• {task.id}[/bold cyan]")
                console.print(f"  [dim]{task.description}[/dim]")
                console.print(f"  [dim]Working dir:[/dim] {task.working_dir}")

                # Steps
                if task.steps:
                    console.print(f"  [dim]Steps ({len(task.steps)}):[/dim]")
                    for i, step in enumerate(task.steps, 1):
                        agent_id = step.agent.use

                        # Get agent info if available
                        agent_role = None
                        if config.agents:
                            agent = config.agents.get_agent(agent_id)
                            if agent:
                                agent_role = agent.role

                        # Format step display: "1. Step Name - Agent Role (agent_id)"
                        step_parts = [f"[cyan]{i}.[/cyan]"]

                        # Add step name if present
                        if step.name:
                            step_parts.append(f"[bold]{step.name}[/bold]")

                        # Add agent info
                        if agent_role:
                            agent_display = f"{agent_role} ({agent_id})"
                        else:
                            agent_display = agent_id

                        # If we have step name, add dash separator
                        if step.name:
                            step_parts.append("-")

                        step_parts.append(agent_display)

                        console.print(f"    {' '.join(step_parts)}")

                        # Show validation if present
                        if step.validate:
                            validation_info = []
                            if step.validate.pre_command:
                                validation_info.append(f"pre: {step.validate.pre_command}")
                            if step.validate.post_command:
                                validation_info.append(f"validate: {step.validate.post_command}")
                            elif step.validate.post_commands:
                                validation_info.append(f"validate: {len(step.validate.post_commands)} checks")
                            if step.validate.max_retries > 0:
                                validation_info.append(f"retries: {step.validate.max_retries}")

                            if validation_info:
                                console.print(f"       [dim]→ {', '.join(validation_info)}[/dim]")

                console.print()  # Blank line between tasks

        # List agents
        if show_agents and config.agents:
            console.print()
            console.print("[bold green]🤖 Available Agents[/bold green]")
            console.print()

            for agent in config.agents.agents:
                console.print(f"[bold green]• {agent.id}[/bold green]")
                console.print(f"  [dim]Role:[/dim] {agent.role}")
                console.print(f"  [dim]Model:[/dim] {agent.model}")

                # Show limits if present
                if agent.limits:
                    limits_info = []
                    if agent.limits.runtime:
                        limits_info.append(f"runtime: {agent.limits.runtime}")
                    if agent.limits.iterations:
                        limits_info.append(f"iterations: {agent.limits.iterations}")
                    if limits_info:
                        console.print(f"  [dim]Limits:[/dim] {', '.join(limits_info)}")

                # Show tools access
                if agent.tools:
                    if agent.tools.mode.value == "whitelist" and agent.tools.commands:
                        console.print(f"  [dim]Tools:[/dim] {len(agent.tools.commands)} commands (whitelist)")
                    elif agent.tools.mode.value == "blacklist":
                        if agent.tools.commands:
                            console.print(f"  [dim]Tools:[/dim] All except {len(agent.tools.commands)} (blacklist)")
                        else:
                            console.print("  [dim]Tools:[/dim] Full access")

                console.print()

        # List tools
        if show_tools and config.tools:
            # Commands
            if config.tools.commands:
                console.print()
                console.print("[bold yellow]🛠️  Available Commands[/bold yellow]")
                console.print()

                for cmd in config.tools.commands:
                    console.print(f"[bold yellow]• {cmd.id}[/bold yellow]")
                    console.print(f"  [dim]Binary:[/dim] {cmd.bin}")
                    if cmd.timeout:
                        console.print(f"  [dim]Timeout:[/dim] {cmd.timeout}")
                    if cmd.args:
                        mode_label = "Allowed" if cmd.args_mode.value == "whitelist" else "Blocked"
                        console.print(f"  [dim]{mode_label} args:[/dim] {', '.join(cmd.args[:5])}")
                        if len(cmd.args) > 5:
                            console.print(f"    [dim]... and {len(cmd.args) - 5} more[/dim]")
                    console.print()

            # MCP servers
            if config.tools.mcp:
                console.print()
                console.print("[bold magenta]🔌 Available MCP Servers[/bold magenta]")
                console.print()

                for mcp in config.tools.mcp:
                    console.print(f"[bold magenta]• {mcp.id}[/bold magenta]")
                    console.print(f"  [dim]Transport:[/dim] {mcp.transport}")
                    console.print(f"  [dim]Command:[/dim] {' '.join(mcp.command)}")
                    if mcp.calls:
                        console.print(f"  [dim]Available calls:[/dim] {', '.join(mcp.calls[:5])}")
                        if len(mcp.calls) > 5:
                            console.print(f"    [dim]... and {len(mcp.calls) - 5} more[/dim]")
                    console.print()

        if show_tasks or show_agents or show_tools:
            console.print()

    except ParseError as e:
        console.print(f"[bold red]✗ Configuration error:[/bold red] {e}")
        raise click.Abort from e
    except Exception as e:
        console.print(f"[bold red]✗ Error:[/bold red] {e}")
        raise click.Abort from e
