"""Agent model."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from playfile_core.agents.limits import AgentLimits
from playfile_core.agents.tools_config import AgentToolsConfig, ToolsMode


@dataclass(frozen=True)
class Agent:
    """Represents an agent configuration.

    Attributes:
        id: Unique identifier for the agent
        role: Description of the agent's role
        instructions: Path to instructions file or inline instructions
        model: Model identifier (e.g., "claude-code", "gpt-4")
        tools: Tools access configuration
        limits: Resource limits for the agent
    """

    id: str
    role: str
    model: str
    instructions: str | Path
    tools: AgentToolsConfig | None = None
    limits: AgentLimits | None = None

    def __post_init__(self) -> None:
        """Validate agent configuration."""
        if not self.id:
            msg = "Agent id cannot be empty"
            raise ValueError(msg)
        if not self.role:
            msg = "Agent role cannot be empty"
            raise ValueError(msg)
        if not self.model:
            msg = "Agent model cannot be empty"
            raise ValueError(msg)
        if not self.instructions:
            msg = "Agent instructions cannot be empty"
            raise ValueError(msg)

    def get_instructions_path(self) -> Path | None:
        """Get instructions as Path if it's explicitly a file path.

        Only treats as file path if:
        1. It's already a Path object
        2. It's a string ending with .md or .txt
        3. It's a relative/absolute path starting with ./ / or ../

        Otherwise treats as inline instructions (agent can create files if needed).
        """
        if isinstance(self.instructions, Path):
            return self.instructions
        if isinstance(self.instructions, str):
            # Only treat as path if it's explicitly a file reference
            if self.instructions.endswith((".md", ".txt")):
                return Path(self.instructions)
            if self.instructions.startswith(("./", "/", "../")):
                return Path(self.instructions)
        return None

    def get_instructions_content(self) -> str:
        """Get instructions as string content.

        If instructions is a file path, reads and returns the file content.
        Otherwise returns the instructions string directly.

        Also prepends common.md if it exists in the same directory as the instructions file.

        Returns:
            The instructions content as a string
        """
        instructions_path = self.get_instructions_path()
        if instructions_path:
            # Read from file
            content = instructions_path.read_text(encoding="utf-8")

            # Check for common.md in the same directory
            common_path = instructions_path.parent / "common.md"
            if common_path.exists():
                common_content = common_path.read_text(encoding="utf-8")
                return f"{common_content}\n\n{content}"

            return content
        # Return inline instructions
        return str(self.instructions)

    def is_command_allowed(self, command_id: str) -> bool | None:
        """Check if a command is allowed for this agent.

        Returns:
            True if allowed, False if denied, None if no tools config
        """
        if self.tools is None:
            return None

        is_in_list = command_id in self.tools.commands
        if self.tools.mode == ToolsMode.WHITELIST:
            return is_in_list
        return not is_in_list

    def is_mcp_allowed(self, mcp_id: str) -> bool | None:
        """Check if an MCP server is allowed for this agent.

        Returns:
            True if allowed, False if denied, None if no tools config
        """
        if self.tools is None:
            return None

        is_in_list = mcp_id in self.tools.mcp
        if self.tools.mode == ToolsMode.WHITELIST:
            return is_in_list
        return not is_in_list
