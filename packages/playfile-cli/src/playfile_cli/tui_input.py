"""TUI input handler for user intervention during agent execution."""

from __future__ import annotations

import sys
import termios
import threading
import tty
from typing import TYPE_CHECKING

from rich.console import Console

if TYPE_CHECKING:
    from playfile_cli.instruction_queue import InstructionQueue


class TUIInputHandler:
    """Handles user input during agent execution via TUI."""

    def __init__(self, instruction_queue: InstructionQueue, console: Console) -> None:
        """Initialize TUI input handler.

        Args:
            instruction_queue: Queue to add instructions to
            console: Rich console for output
        """
        self._queue = instruction_queue
        self._console = console
        self._running = False
        self._thread: threading.Thread | None = None
        self._input_buffer = ""

    def start(self) -> None:
        """Start the input handler in a background thread."""
        if self._running:
            return

        self._running = True
        self._thread = threading.Thread(target=self._input_loop, daemon=True)
        self._thread.start()

        # Show help message
        self._console.print(
            "\n[dim]Press 'i' to add instructions, 'q' to quit, '?' for help[/dim]\n"
        )

    def stop(self) -> None:
        """Stop the input handler."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=1.0)

    def _input_loop(self) -> None:
        """Main input loop running in background thread."""
        # Save terminal settings
        old_settings = termios.tcgetattr(sys.stdin)

        try:
            # Set terminal to raw mode for character-by-character input
            tty.setcbreak(sys.stdin.fileno())

            while self._running:
                # Check if input is available
                if sys.stdin in [sys.stdin]:
                    char = sys.stdin.read(1)

                    if char == "i":
                        self._handle_instruction_input()
                    elif char == "q":
                        self._console.print("\n[yellow]User requested quit[/yellow]\n")
                        self._running = False
                        break
                    elif char == "?":
                        self._show_help()

        finally:
            # Restore terminal settings
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)

    def _handle_instruction_input(self) -> None:
        """Handle user instruction input."""
        # Restore terminal to normal mode for line input
        old_settings = termios.tcgetattr(sys.stdin)
        try:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)

            # Prompt for instruction
            self._console.print("\n[cyan]Enter instruction (or empty to cancel):[/cyan]")
            instruction = input("> ").strip()

            if instruction:
                self._queue.add(instruction)
                self._console.print(
                    f"[green]✓ Instruction queued:[/green] {instruction}\n"
                )
            else:
                self._console.print("[dim]Cancelled[/dim]\n")

        finally:
            # Set back to cbreak mode
            tty.setcbreak(sys.stdin.fileno())

    def _show_help(self) -> None:
        """Show help message."""
        self._console.print(
            "\n[cyan]TUI Controls:[/cyan]\n"
            "  [bold]i[/bold] - Add instruction to agent\n"
            "  [bold]q[/bold] - Request graceful quit\n"
            "  [bold]?[/bold] - Show this help\n"
        )
