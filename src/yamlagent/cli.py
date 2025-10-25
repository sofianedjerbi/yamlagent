"""CLI commands"""

from pathlib import Path

import typer
from rich.console import Console
from yamlagent_core import process_data
from yamlagent_utils import format_output

app = typer.Typer(help="YamlAgent - A modern Python CLI application")
console = Console()


@app.command()
def hello(name: str = typer.Option("World", help="Name to greet")) -> None:
    """Say hello"""
    console.print(f"[bold green]Hello {name}![/bold green]")


@app.command()
def process(
    input_file: str = typer.Argument(..., help="Input file to process"),
    output: str | None = typer.Option(None, "--output", "-o", help="Output file"),
) -> None:
    """Process input file"""
    result = process_data(input_file)
    formatted = format_output(result)

    if output:
        with Path(output).open("w") as f:
            f.write(formatted)
        console.print(f"[green]Output written to {output}[/green]")
    else:
        console.print(formatted)


def main() -> None:
    """CLI entry point"""
    app()
