"""MCP server model."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class MCP:
    """Represents an MCP (Model Context Protocol) server configuration.

    Attributes:
        id: Unique identifier for the MCP server
        transport: Transport protocol (e.g., "stdio")
        command: Command to start the server
        calls: List of API calls this server exposes
    """

    id: str
    transport: str
    command: list[str]
    calls: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Validate MCP configuration."""
        if not self.id:
            msg = "MCP id cannot be empty"
            raise ValueError(msg)
        if not self.transport:
            msg = "MCP transport cannot be empty"
            raise ValueError(msg)
        if not self.command:
            msg = "MCP command cannot be empty"
            raise ValueError(msg)
