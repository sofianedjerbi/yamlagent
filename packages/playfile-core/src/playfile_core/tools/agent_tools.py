"""Agent tools container model."""

from __future__ import annotations

from dataclasses import dataclass, field

from playfile_core.tools.command import Command
from playfile_core.tools.mcp import MCP


@dataclass(frozen=True)
class AgentTools:
    """Complete agent tools configuration.

    Attributes:
        version: Configuration version
        commands: List of command configurations
        mcp: List of MCP server configurations
    """

    version: int
    commands: list[Command] = field(default_factory=list)
    mcp: list[MCP] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Validate agent tools configuration."""
        if self.version < 1:
            msg = f"Version must be >= 1, got {self.version}"
            raise ValueError(msg)

        # Validate unique IDs
        command_ids = [cmd.id for cmd in self.commands]
        if len(command_ids) != len(set(command_ids)):
            msg = "Duplicate command IDs found"
            raise ValueError(msg)

        mcp_ids = [m.id for m in self.mcp]
        if len(mcp_ids) != len(set(mcp_ids)):
            msg = "Duplicate MCP IDs found"
            raise ValueError(msg)

    def get_command(self, command_id: str) -> Command | None:
        """Get command by ID."""
        for cmd in self.commands:
            if cmd.id == command_id:
                return cmd
        return None

    def get_mcp(self, mcp_id: str) -> MCP | None:
        """Get MCP server by ID."""
        for m in self.mcp:
            if m.id == mcp_id:
                return m
        return None
