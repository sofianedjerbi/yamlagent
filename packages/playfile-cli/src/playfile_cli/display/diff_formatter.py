"""Diff formatting for file edits."""

from __future__ import annotations

import difflib

from rich.console import Console
from rich.panel import Panel
from rich.text import Text


class DiffFormatter:
    """Formats file edit diffs for beautiful terminal display."""

    def __init__(self, console: Console | None = None) -> None:
        """Initialize diff formatter.

        Args:
            console: Rich console for output
        """
        self._console = console or Console()

    def print_edit_diff(
        self,
        file_path: str,
        old_string: str,
        new_string: str,
        context_lines: int = 2,
    ) -> None:
        """Print a beautiful diff for an edit operation.

        Args:
            file_path: Path to the file being edited
            old_string: Original text being replaced
            new_string: New text replacing the old text
            context_lines: Number of context lines to show
        """
        # Split into lines (no keepends to avoid double newlines)
        old_lines = old_string.splitlines()
        new_lines = new_string.splitlines()

        # Generate unified diff
        diff = difflib.unified_diff(
            old_lines,
            new_lines,
            fromfile=f"{file_path} (before)",
            tofile=f"{file_path} (after)",
            lineterm="",
            n=context_lines,
        )

        # Format the diff with colors and line numbers
        diff_text = Text()
        old_line_num = 0
        new_line_num = 0
        lines_list = list(diff)

        for idx, line in enumerate(lines_list):
            is_last = idx == len(lines_list) - 1

            if line.startswith("---") or line.startswith("+++"):
                # File headers - skip these, we show in panel title
                continue
            elif line.startswith("@@"):
                # Chunk headers - extract line numbers
                import re

                match = re.search(r"@@ -(\d+)", line)
                if match:
                    old_line_num = int(match.group(1))
                    new_line_num = old_line_num
                diff_text.append(
                    f"{line}\n" if not is_last else line, style="bold magenta"
                )
            elif line.startswith("+"):
                # Added lines
                diff_text.append(f"{new_line_num:4d} ", style="dim green")
                diff_text.append(
                    f"{line}\n" if not is_last else line, style="green"
                )
                new_line_num += 1
            elif line.startswith("-"):
                # Removed lines
                diff_text.append(f"{old_line_num:4d} ", style="dim red")
                diff_text.append(f"{line}\n" if not is_last else line, style="red")
                old_line_num += 1
            elif line.startswith(" "):
                # Context lines
                diff_text.append(f"{old_line_num:4d} ", style="dim")
                diff_text.append(f"{line}\n" if not is_last else line, style="dim")
                old_line_num += 1
                new_line_num += 1

        # Display in a panel
        if diff_text:
            self._console.print(
                Panel(
                    diff_text,
                    title=f"[bold yellow]Edit: {file_path}[/bold yellow]",
                    border_style="yellow",
                    padding=(0, 1),
                )
            )

    def print_compact_edit(
        self,
        file_path: str,
        old_string: str,
        new_string: str,
    ) -> None:
        """Print a compact inline diff for small edits.

        Args:
            file_path: Path to the file being edited
            old_string: Original text being replaced
            new_string: New text replacing the old text
        """
        # For very short edits (single line or very short), show inline
        old_lines = old_string.splitlines()
        new_lines = new_string.splitlines()

        if (
            len(old_lines) <= 3
            and len(new_lines) <= 3
            and len(old_string) < 150
            and len(new_string) < 150
        ):
            diff_display = Text()

            # Show removed lines
            for idx, line in enumerate(old_lines):
                diff_display.append("- ", style="red bold")
                diff_display.append(line, style="red strike")
                if idx < len(old_lines) - 1 or new_lines:
                    diff_display.append("\n")

            # Show added lines
            for idx, line in enumerate(new_lines):
                diff_display.append("+ ", style="green bold")
                diff_display.append(line, style="green")
                if idx < len(new_lines) - 1:
                    diff_display.append("\n")

            self._console.print(
                Panel(
                    diff_display,
                    title=f"[bold yellow]Edit: {file_path}[/bold yellow]",
                    border_style="yellow",
                    padding=(0, 1),
                )
            )
        else:
            # Fall back to full diff for longer edits
            self.print_edit_diff(file_path, old_string, new_string)

    def print_side_by_side_diff(
        self,
        file_path: str,
        old_string: str,
        new_string: str,
        width: int = 80,
    ) -> None:
        """Print a side-by-side diff comparison.

        Args:
            file_path: Path to the file being edited
            old_string: Original text being replaced
            new_string: New text replacing the old text
            width: Total width for the display
        """
        from rich.columns import Columns
        from rich.panel import Panel

        # Split into lines
        old_lines = old_string.splitlines()
        new_lines = new_string.splitlines()

        # Create side-by-side panels
        old_panel = Panel(
            "\n".join(old_lines),
            title="[red]Before[/red]",
            border_style="red",
            padding=(0, 1),
        )

        new_panel = Panel(
            "\n".join(new_lines),
            title="[green]After[/green]",
            border_style="green",
            padding=(0, 1),
        )

        # Display side by side
        self._console.print(
            Panel(
                Columns([old_panel, new_panel], equal=True, expand=True),
                title=f"[bold yellow]Edit: {file_path}[/bold yellow]",
                border_style="yellow",
            )
        )
