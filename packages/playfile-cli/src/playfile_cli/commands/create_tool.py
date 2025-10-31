"""Create tool command."""

from __future__ import annotations

import asyncio
from pathlib import Path

import rich_click as click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from playfile_cli.tool_builder.builder import ToolBuilder, ToolConfig, ToolWriter


@click.command(name="tool")
@click.argument("tool_id", required=False)
@click.argument("binary", required=False)
@click.argument("instructions", nargs=-1, required=False)
@click.option(
    "-c",
    "--config",
    "config_path",
    type=click.Path(exists=True, path_type=Path),
    help="Path to config file (default: playfile.yaml in project root)",
)
@click.option(
    "--args",
    "args",
    help="Comma-separated list of allowed arguments (manual mode only)",
)
@click.option(
    "--timeout",
    default="10m",
    help="Timeout for the tool (default: 10m, manual mode only)",
)
def create_tool(
    tool_id: str | None,
    binary: str | None,
    instructions: tuple[str, ...],
    config_path: Path | None,
    args: str | None,
    timeout: str,
) -> None:
    """Create custom tool configurations

    Two modes:

    \b
    1. AI Mode (Claude-powered, intelligent):
       pf create tool bash "Safe bash commands for development"
       pf create tool python "All Python dev tools needed"

    2. Manual Mode (quick, explicit):
       pf create tool cargo cargo --args "build,test,check" --timeout 10m
       pf create tool git git --timeout 30s

    \b
    AI Mode:
    Claude will intelligently:
    - Explore your project to understand the tech stack
    - Determine what tools are actually needed
    - Configure appropriate arguments and timeouts
    - Be security-conscious with permissions

    \b
    Manual Mode:
    Quickly add a single tool with explicit configuration.
    Use --args to restrict allowed arguments (comma-separated).
    If --args is omitted, all arguments are allowed.

    The tools will be added to .play/tools.yaml
    """
    console = Console()

    try:
        # Get project root first
        if config_path:
            project_root = config_path.parent
        else:
            project_root = Path.cwd()

        # Determine mode: Manual (has --args or both tool_id and binary) vs AI (free-form instructions)
        is_manual_mode = args is not None or (tool_id and binary and not instructions)

        if is_manual_mode:
            # Manual Mode: Quick tool addition with explicit config
            if not tool_id or not binary:
                console.print("[bold red]✗ Error:[/bold red] Manual mode requires both TOOL_ID and BINARY")
                console.print("\n[dim]Usage: pf create tool <id> <binary> [--args ...] [--timeout ...]")
                console.print("   Or: pf create tool <instructions...> (for AI mode)[/dim]")
                raise click.Abort

            # Parse args
            args_list = None
            if args:
                args_list = [arg.strip() for arg in args.split(",")]

            # Create tool config
            tool_config = ToolConfig(
                id=tool_id,
                bin=binary,
                args=args_list,
                args_mode="whitelist",
                timeout=timeout or "5m",
            )

            # Show what we're creating
            console.print()
            console.print(
                Panel(
                    f"[bold]Creating tool:[/bold] {tool_id}\n\n"
                    f"Binary: {binary}\n"
                    f"Args: {', '.join(args_list) if args_list else 'all allowed'}\n"
                    f"Timeout: {timeout}",
                    border_style="cyan",
                )
            )
            console.print()

            # Write tool file
            with console.status("[cyan]Writing tool to .play/tools.yaml...[/cyan]"):
                writer = ToolWriter(project_root)
                tools_yaml = writer.write_tool(tool_config)

            tool_configs = [tool_config]

        else:
            # AI Mode: Use Claude to intelligently design tools
            if not tool_id and not instructions:
                console.print("[bold red]✗ Error:[/bold red] AI mode requires instructions")
                console.print("\n[dim]Usage: pf create tool <instructions...>")
                console.print('Example: pf create tool bash "Safe bash commands"[/dim]')
                raise click.Abort

            # Combine all arguments as instructions
            all_instructions = []
            if tool_id:
                all_instructions.append(tool_id)
            if binary:
                all_instructions.append(binary)
            if instructions:
                all_instructions.extend(instructions)

            user_instructions = " ".join(all_instructions)

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

            # Write tools file
            with console.status("[cyan]Writing tools to .play/tools.yaml...[/cyan]"):
                writer = ToolWriter(project_root)
                tools_yaml = writer.write_tools(tool_configs)

        # Display tools (AI mode shows table, manual mode already showed panel)
        if not is_manual_mode:
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
                args_display = ", ".join(tool.args) if tool.args else "[dim]all allowed[/dim]"
                table.add_row(
                    tool.id,
                    tool.bin,
                    args_display,
                    tool.timeout
                )

            console.print(table)
            console.print()

        # Success
        console.print("[bold green]✓ Tool created successfully![/bold green]" if is_manual_mode else "[bold green]✓ Tools created successfully![/bold green]")
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
