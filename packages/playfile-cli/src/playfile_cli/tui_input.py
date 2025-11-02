"""Simple input handler for user intervention during agent execution."""

from __future__ import annotations

import threading
from typing import TYPE_CHECKING

from rich.console import Console
from rich.panel import Panel

if TYPE_CHECKING:
    from playfile_cli.instruction_queue import InstructionQueue


class TUIInputHandler:
    """Handles user input during agent execution with simple input prompts."""

    def __init__(self, instruction_queue: InstructionQueue, console: Console) -> None:
        """Initialize input handler.

        Args:
            instruction_queue: Queue to add instructions to
            console: Rich console for output
        """
        self._queue = instruction_queue
        self._console = console
        self._running = False
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        """Start the input handler in a background thread."""
        if self._running:
            return

        self._running = True

        # Show input panel
        self._console.print()
        self._console.print(
            Panel(
                "[cyan]Type instructions below and press Enter to send to the agent[/cyan]\n"
                "[dim]Type 'q' and press Enter to quit gracefully[/dim]",
                title="💬 [bold]Agent Instructions[/bold]",
                border_style="cyan",
            )
        )
        self._console.print()

        # Start background input loop
        self._thread = threading.Thread(target=self._input_loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        """Stop the input handler."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=1.0)

    def _input_loop(self) -> None:
        """Main input loop for getting user instructions."""
        while self._running:
            try:
                # Show prompt
                self._console.print("✏️  [cyan bold]→[/cyan bold] ", end="")

                # Get input
                instruction = input().strip()

                # Handle quit
                if instruction.lower() == "q":
                    self._console.print("\n[yellow]⏹  Stopping gracefully...[/yellow]\n")
                    import os
                    os._exit(0)

                # Queue instruction
                if instruction:
                    self._queue.add(instruction)
                    self._console.print("[green]✓ Queued[/green]\n")

            except (EOFError, KeyboardInterrupt):
                self._console.print("\n[yellow]⏹  Stopping gracefully...[/yellow]\n")
                import os
                os._exit(0)
            except Exception:
                # Ignore other errors and continue
                pass
