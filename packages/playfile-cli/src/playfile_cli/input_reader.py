"""Input reader - handles stdin, inline, and file inputs."""

from __future__ import annotations

import sys
from pathlib import Path


class InputReader:
    """Reads input from various sources."""

    @staticmethod
    def read_prompt(prompt_arg: str | None) -> str | None:
        """Read prompt from argument, stdin, or return None.

        Args:
            prompt_arg: Prompt argument (can be "-" for stdin, text, or None)

        Returns:
            Prompt text or None if not provided
        """
        if prompt_arg is None:
            return None

        # Read from stdin
        if prompt_arg == "-":
            if sys.stdin.isatty():
                msg = "No input provided on stdin. Use '-' only when piping input."
                raise ValueError(msg)
            return sys.stdin.read().strip()

        # Check if it's a file path
        if prompt_arg.startswith("@"):
            file_path = Path(prompt_arg[1:])
            if not file_path.exists():
                msg = f"File not found: {file_path}"
                raise FileNotFoundError(msg)
            return file_path.read_text(encoding="utf-8").strip()

        # Treat as inline text
        return prompt_arg
