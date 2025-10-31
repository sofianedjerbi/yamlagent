"""Command tool model."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class ArgsMode(str, Enum):
    """Mode for argument filtering."""

    WHITELIST = "whitelist"
    BLACKLIST = "blacklist"


@dataclass(frozen=True)
class Command:
    """Represents a command-line tool configuration.

    Attributes:
        id: Unique identifier for the command
        bin: Binary/executable name
        args: List of arguments (whitelisted or blacklisted based on mode)
        args_mode: Whether args list is whitelist or blacklist (default: whitelist)
        timeout: Timeout duration (e.g., "5m", "10s")
    """

    id: str
    bin: str
    args: list[str] = field(default_factory=list)
    args_mode: ArgsMode = ArgsMode.WHITELIST
    timeout: str | None = None

    def __post_init__(self) -> None:
        """Validate command configuration."""
        if not self.id:
            msg = "Command id cannot be empty"
            raise ValueError(msg)
        if not self.bin:
            msg = "Command bin cannot be empty"
            raise ValueError(msg)

    def is_arg_allowed(self, arg: str) -> bool:
        """Check if an argument is allowed for this command.

        Args:
            arg: Argument to check

        Returns:
            True if allowed, False if denied
        """
        if not self.args:
            # No restrictions if args list is empty
            return True

        is_in_list = arg in self.args
        if self.args_mode == ArgsMode.WHITELIST:
            return is_in_list
        return not is_in_list
