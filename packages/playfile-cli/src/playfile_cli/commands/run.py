"""Run command - executes workflow tasks."""

from __future__ import annotations

from pathlib import Path

import rich_click as click
from playfile_core.exceptions import ParseError, ValidationError
from rich.console import Console
from rich.prompt import Prompt

from playfile_cli.config_loader import ConfigLoader
from playfile_cli.input_reader import InputReader
from playfile_cli.task_runner import TaskRunner


@click.command()
@click.argument("task_id")
@click.option(
    "--prompt",
    help="Prompt text ('-' for stdin, '@file' for file input). If omitted, asks interactively.",
)
@click.option(
    "-c",
    "--config",
    "config_path",
    type=click.Path(exists=True, path_type=Path),
    help="Path to config file (default: playfile.yaml in project root)",
)
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    help="Enable verbose output",
)
def run(
    task_id: str,
    prompt: str | None,
    config_path: Path | None,
    verbose: bool,
) -> None:
    """Execute a workflow task with AI agents

    \b
    Examples:
      pf run write-code --prompt "Create a REST API"
      pf run write-code  # Interactive mode
      cat file.txt | pf run analyze --prompt -
    """
    console = Console()

    try:
        # Load configuration
        loader = ConfigLoader()
        config = loader.load(config_path)

        if verbose:
            console.print(f"[dim]✓ Loaded configuration from {config_path or 'agent.yaml'}[/dim]")

        # Read prompt input
        prompt_text = InputReader.read_prompt(prompt)

        # If no prompt provided, ask for it interactively
        if not prompt_text:
            prompt_text = Prompt.ask(
                "[bold cyan]Enter your prompt[/bold cyan]",
                console=console,
            )

            # If still no prompt, show error
            if not prompt_text or not prompt_text.strip():
                console.print("[bold red]✗ Error:[/bold red] Prompt is required")
                raise click.Abort

        # Build inputs dict
        inputs = {"prompt": prompt_text}

        # Run task
        runner = TaskRunner(config, console)
        runner.run(task_id, inputs)

    except ParseError as e:
        console.print(f"[bold red]✗ Configuration error:[/bold red] {e}")
        raise click.Abort from e
    except ValidationError as e:
        console.print(f"[bold red]✗ Validation error:[/bold red] {e}")
        raise click.Abort from e
    except FileNotFoundError as e:
        console.print(f"[bold red]✗ File error:[/bold red] {e}")
        raise click.Abort from e
    except ValueError as e:
        console.print(f"[bold red]✗ Error:[/bold red] {e}")
        raise click.Abort from e
    except Exception as e:
        console.print(f"[bold red]✗ Unexpected error:[/bold red] {e}")
        if verbose:
            console.print_exception()
        raise click.Abort from e
