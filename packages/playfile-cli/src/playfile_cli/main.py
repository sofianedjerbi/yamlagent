"""Main CLI entry point."""

import os

import rich_click as click

from playfile_cli.commands import create, init, run, setup
from playfile_cli.commands.list import list_cmd

# Configure rich-click for clean, simple output
click.rich_click.USE_RICH_MARKUP = False
click.rich_click.USE_MARKDOWN = False
click.rich_click.SHOW_ARGUMENTS = True
click.rich_click.GROUP_ARGUMENTS_OPTIONS = True
click.rich_click.MAX_WIDTH = 100
click.rich_click.SHOW_METAVARS_COLUMN = False
click.rich_click.APPEND_METAVARS_HELP = True

# Command groups
click.rich_click.COMMAND_GROUPS = {
    "pf": [
        {
            "name": "Commands",
            "commands": ["setup", "init", "create", "run", "list"],
        },
    ]
}

# Clean, minimal styling
click.rich_click.STYLE_OPTION = "cyan"
click.rich_click.STYLE_ARGUMENT = "cyan"
click.rich_click.STYLE_COMMAND = "cyan"
click.rich_click.STYLE_SWITCH = "green"
click.rich_click.STYLE_METAVAR = "yellow"
click.rich_click.STYLE_REQUIRED_SHORT = "red"
click.rich_click.STYLE_REQUIRED_LONG = "red"


@click.group()
@click.version_option(version="0.1.0", prog_name="pf")
def cli() -> None:
    """Playfile - AI-powered development workflows

    Run AI agent tasks defined in playfile.yaml using natural language prompts.
    """
    pass


# Register commands
cli.add_command(setup)
cli.add_command(init)
cli.add_command(create)
cli.add_command(run)
cli.add_command(list_cmd)


if __name__ == "__main__":
    cli()
