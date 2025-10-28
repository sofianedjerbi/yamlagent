"""Create tool command."""

from __future__ import annotations

import asyncio
from pathlib import Path

import rich_click as click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from playfile_cli.tool_builder.builder import ToolBuilder, ToolWriter


@click.command(name="tool")
@click.argument("instructions", nargs=-1, required=True)
@click.option(
    "-c",
    "--config",
    "config_path",
    type=click.Path(exists=True, path_type=Path),
    help="Path to config file (default: playfile.yaml in project root)",
)
def create_tool(
    instructions: tuple[str, ...],
    config_path: Path | None,
) -> None:
    """Create custom tool configurations using Claude's intelligence

    INSTRUCTIONS describe what tools are needed for the project

    Claude will intelligently:
    - Explore your project to understand the tech stack
    - Determine what tools are actually needed
    - Configure appropriate arguments and timeouts
    - Be security-conscious with permissions

    \b
    Examples:
      pf create tool bash "Safe bash commands for development"
      pf create tool python "All Python dev tools needed for this project"
      pf create tool rust "Cargo and rust toolchain"
      pf create tool java "Maven build tools"

    The tools will be added to .play/tools.yaml
    """
    console = Console()

    try:
        # Get project root first
        if config_path:
            project_root = config_path.parent
        else:
            project_root = Path.cwd()

        # Combine instructions
        user_instructions = " ".join(instructions)

        # Show what we're doing
        console.print()
        console.print(
            Panel(
                f"[bold]Creating custom tools[/bold]\n\n"
                f"Requirements: {user_instructions}\n\n"
                f"[dim]Claude will explore your project and configure the perfect tools...[/dim]",
                border_style="cyan",
            )
        )
        console.print()

        # Build tools with Claude (async)
        async def _build():
            builder = ToolBuilder()
            return await builder.build_tools(
                user_instructions,
                working_dir=str(project_root)
            )

        with console.status("[cyan]Claude is exploring your project and designing tools...[/cyan]"):
            tool_configs = asyncio.run(_build())

        # Display generated tools
        console.print("[bold green]✓ Tools designed successfully![/bold green]")
        console.print()
        console.print("[bold]Generated Tools:[/bold]")

        # Create table for tools
        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("ID", style="cyan")
        table.add_column("Binary")
        table.add_column("Allowed Args")
        table.add_column("Timeout")

        for tool in tool_configs:
            args_display = ", ".join(tool.args_allow) if tool.args_allow else "[dim]all allowed[/dim]"
            table.add_row(
                tool.id,
                tool.bin,
                args_display,
                tool.timeout
            )

        console.print(table)
        console.print()

        # Write tools file
        with console.status("[cyan]Writing tools to .play/tools.yaml...[/cyan]"):
            writer = ToolWriter(project_root)
            tools_yaml = writer.write_tools(tool_configs)

        # Success
        console.print("[bold green]✓ Tools created successfully![/bold green]")
        console.print()
        console.print("[bold]File updated:[/bold]")
        console.print(f"  [green]✓[/green] {tools_yaml.relative_to(project_root)}")
        console.print()
        console.print("[bold]Next steps:[/bold]")
        console.print(f"  1. Review configuration: [cyan]{tools_yaml.relative_to(project_root)}[/cyan]")
        console.print(f"  2. Add to agent tools: [cyan]commands: ['{tool_configs[0].id}'][/cyan]")
        console.print()
        console.print("[dim]Tip: Run 'pf list --tools' to see all tools[/dim]")
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
