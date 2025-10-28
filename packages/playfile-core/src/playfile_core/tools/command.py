"""Command tool model."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Command:
    """Represents a command-line tool configuration.

    Attributes:
        id: Unique identifier for the command
        bin: Binary/executable name
        args_allow: List of allowed arguments
        timeout: Timeout duration (e.g., "5m", "10s")
    """

    id: str
    bin: str
    args_allow: list[str] = field(default_factory=list)
    timeout: str | None = None

    def __post_init__(self) -> None:
        """Validate command configuration."""
        if not self.id:
            msg = "Command id cannot be empty"
            raise ValueError(msg)
        if not self.bin:
            msg = "Command bin cannot be empty"
            raise ValueError(msg)
