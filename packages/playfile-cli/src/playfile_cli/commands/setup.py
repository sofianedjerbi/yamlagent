"""Setup command - creates a new project from scratch with AI."""

from __future__ import annotations

from pathlib import Path

import rich_click as click
from rich.console import Console
from rich.panel import Panel


@click.command()
@click.argument("instructions", required=True)
@click.option(
    "--path",
    type=click.Path(path_type=Path),
    default=".",
    help="Directory to create project in (default: current directory)",
)
def setup(instructions: str, path: Path) -> None:
    """Setup a new project from scratch with AI

    Creates a complete project structure with configuration files and initial setup
    based on your instructions. The AI will set up everything following best practices.

    \b
    Examples:
      pf setup "Python CLI tool with typer"
      pf setup "React app with TypeScript and Vite"
      pf setup "Rust web API with axum" --path ./my-api
      pf setup "Go microservice with gRPC"
    """
    console = Console()

    try:
        target_dir = path.resolve()

        # Check if directory is empty (allow hidden files like .git)
        if target_dir.exists():
            non_hidden = [f for f in target_dir.iterdir() if not f.name.startswith(".")]
            if non_hidden:
                console.print(
                    f"[bold red]✗ Error:[/bold red] Directory is not empty: {target_dir}"
                )
                console.print("[dim]Use an empty directory for project setup.[/dim]")
                raise click.Abort

        # Create directory if it doesn't exist
        target_dir.mkdir(parents=True, exist_ok=True)

        console.print()
        console.print(
            Panel(
                f"[bold]Setting up project:[/bold]\n{instructions}\n\n"
                f"[dim]Location: {target_dir}[/dim]",
                border_style="cyan",
            )
        )
        console.print()

        # Setup project with AI
        try:
            from playfile_cli.intelligent_init import (
                customize_for_project,
                setup_project_with_claude,
            )
            from playfile_cli.templates import TemplateManager

            setup_project_with_claude(target_dir, instructions, console)

        except ImportError as e:
            console.print(f"[bold red]✗ Error:[/bold red] AI setup unavailable: {e}")
            raise click.Abort from e
        except Exception as e:
            console.print(f"[bold red]✗ Project setup failed:[/bold red] {e}")
            raise click.Abort from e

        # Initialize playfile automatically
        console.print()
        console.print("[bold cyan]🤖 Initializing Playfile configuration...[/bold cyan]")
        console.print()

        try:
            # Create playfile templates
            manager = TemplateManager()
            created, _ = manager.initialize_project(target_dir, overwrite=False)

            if created:
                console.print("[green]✓ Created Playfile configuration[/green]")

                # Customize for the project
                console.print()
                console.print("[bold cyan]🤖 Customizing configuration...[/bold cyan]")
                console.print()
                customize_for_project(target_dir, console)

        except Exception as e:
            console.print(f"[yellow]⚠ Playfile init failed: {e}[/yellow]")
            console.print("[dim]You can run 'pf init --intelligent' manually.[/dim]")

        # Success message
        console.print()
        console.print("[bold green]✓ Project ready![/bold green]")
        console.print()
        console.print("[bold]Next steps:[/bold]")
        console.print("  1. Review the generated files")
        console.print("  2. Start building: [cyan]pf run code --prompt \"...\"[/cyan]")
        console.print()

    except click.Abort:
        raise
    except Exception as e:
        console.print(f"[bold red]✗ Unexpected error:[/bold red] {e}")
        raise click.Abort from e
