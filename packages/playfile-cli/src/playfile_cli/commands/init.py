"""Init command - initializes a new Playfile project."""

from __future__ import annotations

from pathlib import Path

import rich_click as click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from playfile_cli.templates import TemplateManager


@click.command()
@click.option(
    "--path",
    type=click.Path(path_type=Path),
    default=".",
    help="Directory to initialize (default: current directory)",
)
@click.option(
    "--force",
    is_flag=True,
    help="Overwrite existing files",
)
@click.option(
    "--intelligent",
    is_flag=True,
    help="Customize configuration with AI for existing project",
)
def init(path: Path, force: bool, intelligent: bool) -> None:
    """Initialize Playfile in an existing project

    Creates playfile.yaml and .play/ directory with configuration
    for agents, tools, and tasks. Use --intelligent to auto-detect
    project settings and customize the configuration.

    \b
    Examples:
      pf init                      # Initialize with default templates
      pf init --path ./my-project  # Initialize in specific directory
      pf init --intelligent        # Auto-detect and customize for project
      pf init --force              # Overwrite existing files

    \b
    To create a new project from scratch, use:
      pf setup "Your project description"
    """
    console = Console()

    try:
        target_dir = path.resolve()

        console.print()
        console.print(
            Panel(
                f"[bold]Initializing Playfile in:[/bold]\n{target_dir}",
                border_style="cyan",
            )
        )
        console.print()

        manager = TemplateManager()
        created, skipped = manager.initialize_project(target_dir, overwrite=force)

        # Display results
        if created:
            table = Table(
                title="✓ Created Files",
                show_header=False,
                border_style="green",
                title_style="bold green",
            )
            table.add_column("File", style="green")

            for file_path in created:
                rel_path = file_path.relative_to(target_dir)
                table.add_row(f"  {rel_path}")

            console.print(table)
            console.print()

        if skipped:
            table = Table(
                title="⊘ Skipped Files (already exist)",
                show_header=False,
                border_style="yellow",
                title_style="bold yellow",
            )
            table.add_column("File", style="yellow")

            for file_path in skipped:
                rel_path = file_path.relative_to(target_dir)
                table.add_row(f"  {rel_path}")

            console.print(table)
            console.print()

            if not force:
                console.print(
                    "[dim]Tip: Use --force to overwrite existing files[/dim]\n"
                )

        # Run intelligent customization if requested
        if intelligent and created:
            console.print()
            console.print("[bold cyan]🤖 Customizing playfile configuration...[/bold cyan]")
            console.print()

            try:
                from playfile_cli.intelligent_init import customize_for_project

                customize_for_project(target_dir, console)

            except ImportError as e:
                console.print(f"[bold yellow]⚠ Customization unavailable:[/bold yellow] {e}")
                console.print("[dim]Install required dependencies or customize manually.[/dim]")
            except Exception as e:
                console.print(f"[bold yellow]⚠ Customization failed:[/bold yellow] {e}")
                console.print("[dim]Files created but not customized.[/dim]")

        # Success message with next steps
        if created:
            console.print("[bold green]✓ Project initialized successfully![/bold green]")
            console.print()
            if not intelligent:
                console.print("[bold]Next steps:[/bold]")
                console.print("  1. Review and customize [cyan]playfile.yaml[/cyan]")
                console.print("  2. Edit agent instructions in [cyan].play/agents/[/cyan]")
                console.print("  3. Configure tools in [cyan].play/tools.yaml[/cyan]")
                console.print()
            console.print("[bold]Try it out:[/bold]")
            console.print("  [cyan]pf list[/cyan]                    # List available tasks")
            console.print("  [cyan]pf run code --prompt \"...\"[/cyan]  # Run a task")
            console.print()
        else:
            console.print(
                "[bold yellow]⚠ No files were created (all files already exist)[/bold yellow]"
            )
            console.print()

    except OSError as e:
        console.print(f"[bold red]✗ Error:[/bold red] Failed to create files: {e}")
        raise click.Abort from e
    except Exception as e:
        console.print(f"[bold red]✗ Unexpected error:[/bold red] {e}")
        raise click.Abort from e
