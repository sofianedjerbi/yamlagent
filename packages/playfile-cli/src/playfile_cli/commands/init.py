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
def init(path: Path, force: bool) -> None:
    """Initialize a new Playfile project with default configuration

    Creates a playfile.yaml entry file and .play/ directory with:
    - agents.yaml: Agent definitions with roles and capabilities
    - tools.yaml: Available tools and commands
    - agents/: Directory with instruction markdown files

    The default setup includes general coding tools and agents for:
    - Writing code
    - Reviewing code
    - Documenting code
    - Writing tests

    \b
    Examples:
      pf init              # Initialize in current directory
      pf init --path ./my-project
      pf init --force      # Overwrite existing files
    """
    console = Console()

    try:
        # Resolve target directory
        target_dir = path.resolve()

        # Show what we're about to do
        console.print()
        console.print(
            Panel(
                f"[bold]Initializing Playfile project in:[/bold]\n{target_dir}",
                border_style="cyan",
            )
        )
        console.print()

        # Initialize project
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

        # Success message with next steps
        if created:
            console.print("[bold green]✓ Project initialized successfully![/bold green]")
            console.print()
            console.print("[bold]Next steps:[/bold]")
            console.print("  1. Review and customize [cyan]playfile.yaml[/cyan]")
            console.print("  2. Edit agent instructions in [cyan].play/agents/[/cyan]")
            console.print("  3. Configure tools in [cyan].play/tools.yaml[/cyan]")
            console.print()
            console.print("[bold]Try it out:[/bold]")
            console.print("  [cyan]pf list[/cyan]                    # List available tasks")
            console.print(
                "  [cyan]pf run code --prompt \"...\"[/cyan]  # Run a task"
            )
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
