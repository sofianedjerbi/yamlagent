"""Agent tools configuration model."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class ToolsMode(Enum):
    """Mode for tools access control."""

    WHITELIST = "whitelist"
    BLACKLIST = "blacklist"


@dataclass(frozen=True)
class AgentToolsConfig:
    """Configuration for agent tools access control.

    Attributes:
        mode: Access control mode (whitelist or blacklist)
        commands: List of command IDs to allow/deny
        mcp: List of MCP server IDs to allow/deny
    """

    mode: ToolsMode
    commands: list[str] = field(default_factory=list)
    mcp: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Validate tools configuration."""
        if not isinstance(self.mode, ToolsMode):
            msg = f"mode must be a ToolsMode enum, got {type(self.mode)}"
            raise ValueError(msg)
