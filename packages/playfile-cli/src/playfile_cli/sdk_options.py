"""Builder for Claude SDK options from agent configuration."""

from __future__ import annotations

from pathlib import Path

from claude_agent_sdk import ClaudeAgentOptions
from playfile_core.agents.agent import Agent


class SdkOptionsBuilder:
    """Builds ClaudeAgentOptions from Playfile agent configuration."""

    @staticmethod
    def build_options(
        agent: Agent,
        working_dir: str,
        files: list[str] | None = None,
    ) -> ClaudeAgentOptions:
        """Build Claude SDK options from agent config.

        Args:
            agent: Agent configuration
            working_dir: Working directory
            files: List of file paths to include in context

        Returns:
            ClaudeAgentOptions instance
        """
        # Get instructions
        system_prompt = agent.get_instructions_content()

        # Build allowed tools list
        allowed_tools = SdkOptionsBuilder._build_allowed_tools(agent)

        # Build options dict
        options_dict = {
            "model": agent.model,
            "system_prompt": system_prompt,
            "cwd": working_dir,
            # Allow agents to create/edit files without prompts
            "permission_mode": "bypassPermissions",
            "include_partial_messages": True,  # Enable finer-grained streaming
        }

        # Add allowed tools if any
        if allowed_tools:
            options_dict["allowed_tools"] = allowed_tools

        # Add files as directories to include
        if files:
            dirs: set[str] = set()
            for file_path in files:
                dirs.add(str(Path(file_path).parent))
            if dirs:
                options_dict["add_dirs"] = list(dirs)  # type: ignore[typeddict-item]

        return ClaudeAgentOptions(**options_dict)

    @staticmethod
    def _build_allowed_tools(agent: Agent) -> list[str] | None:
        """Build allowed tools list from agent config.

        Args:
            agent: Agent configuration

        Returns:
            List of allowed tool names or None (None = allow all tools)
        """
        if not agent.tools:
            # No tools config = allow all tools
            return None

        # In blacklist mode, we allow all tools by returning None
        # Commands in the blacklist are handled by Claude Code separately
        if agent.tools.mode.value == "blacklist":
            return None

        # In whitelist mode, build the allowed tools list
        allowed = []

        # Add allowed commands
        for cmd_id in agent.tools.commands:
            allowed.append(f"Bash({cmd_id}:*)")

        # Add allowed MCP tools
        for mcp_id in agent.tools.mcp:
            allowed.append(f"mcp__{mcp_id}__*")

        # For whitelist mode, also need to allow built-in tools explicitly
        # If commands list is provided, it means user wants specific tools
        return allowed if allowed else None
