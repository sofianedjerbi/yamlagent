"""Tool builder for creating tool configurations."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from claude_agent_sdk import query
from claude_agent_sdk.types import ClaudeAgentOptions

from playfile_cli.tool_builder.prompts import (
    TOOL_BUILDER_SYSTEM_PROMPT,
    build_tool_creation_prompt,
)


@dataclass
class ToolConfig:
    """Tool configuration."""

    id: str
    bin: str
    args: list[str] | None = None
    args_mode: str = "whitelist"
    timeout: str = "5m"


class ToolBuilder:
    """Builds custom tools using Claude's intelligence."""

    async def build_tools(
        self,
        user_instructions: str,
        working_dir: str | None = None,
    ) -> list[ToolConfig]:
        """Use Claude to build tool configurations.

        Args:
            user_instructions: User's description of what tools are needed
            working_dir: Current working directory for project exploration

        Returns:
            List of ToolConfig objects

        Raises:
            ValueError: If Claude's response is invalid
            RuntimeError: If query fails
        """
        # Build prompt with working directory context
        user_prompt = build_tool_creation_prompt(user_instructions, working_dir)

        try:
            # Query Claude using claude-agent-sdk
            options = ClaudeAgentOptions(
                system_prompt=TOOL_BUILDER_SYSTEM_PROMPT,
                permission_mode="bypassPermissions",
                cwd=working_dir,
            )

            # Collect all messages from Claude's response
            final_content = ""
            async for message in query(prompt=user_prompt, options=options):
                # Try to extract content from any message type
                if hasattr(message, "content"):
                    if isinstance(message.content, str):
                        final_content += message.content
                    elif isinstance(message.content, list):
                        for block in message.content:
                            if hasattr(block, "text"):
                                final_content += block.text
                            elif isinstance(block, dict) and "text" in block:
                                final_content += block["text"]

            if not final_content:
                msg = "Empty response from Claude"
                raise ValueError(msg)

            content = final_content

            # Parse JSON response - always try extracting from code blocks first
            data = None

            # Try to extract JSON from markdown code blocks
            if "```json" in content:
                json_start = content.find("```json") + 7
                json_end = content.rfind("```")
                if json_end > json_start:
                    json_str = content[json_start:json_end].strip()
                    try:
                        data = json.loads(json_str)
                    except json.JSONDecodeError:
                        pass

            if data is None and "```" in content:
                json_start = content.find("```") + 3
                json_end = content.rfind("```")
                if json_end > json_start:
                    json_str = content[json_start:json_end].strip()
                    try:
                        data = json.loads(json_str)
                    except json.JSONDecodeError:
                        pass

            if data is None:
                # Try direct JSON parsing
                try:
                    data = json.loads(content)
                except json.JSONDecodeError as e:
                    msg = f"Failed to parse JSON response: {e}\nContent: {content[:500]}"
                    raise ValueError(msg) from e

            # Validate and extract data
            if "tools" not in data:
                msg = f"Invalid response format from Claude. Expected 'tools' key. Got: {list(data.keys())}"
                raise ValueError(msg)

            tools_data = data["tools"]

            # Convert to ToolConfig objects
            tool_configs = []
            for tool in tools_data:
                tool_configs.append(
                    ToolConfig(
                        id=tool["id"],
                        bin=tool["bin"],
                        args_allow=tool.get("args_allow"),
                        timeout=tool["timeout"],
                    )
                )

            return tool_configs

        except Exception as e:
            msg = f"Failed to build tools: {e}"
            raise RuntimeError(msg) from e


class ToolWriter:
    """Writes tool configuration to tools.yaml."""

    def __init__(self, project_root: Path) -> None:
        """Initialize tool writer.

        Args:
            project_root: Root directory of the project
        """
        self._project_root = project_root

    def write_tools(self, configs: list[ToolConfig]) -> Path:
        """Write multiple tool configurations to .play/tools.yaml.

        Args:
            configs: List of tool configurations to write

        Returns:
            Path to tools.yaml

        Raises:
            FileNotFoundError: If .play/tools.yaml doesn't exist
            OSError: If file operations fail
        """
        tools_yaml_path = self._project_root / ".play" / "tools.yaml"
        if not tools_yaml_path.exists():
            msg = f"Tools configuration not found: {tools_yaml_path}"
            raise FileNotFoundError(msg)

        # Generate YAML for all tools
        tools_yaml = "\n".join(self._generate_tool_yaml(config) for config in configs)

        # Read existing content
        content = tools_yaml_path.read_text(encoding="utf-8")

        # Find where to insert (after other commands, before any MCP section)
        if "  # Add language-specific tools" in content:
            # Insert before the comment
            insert_point = content.find("  # Add language-specific tools")
            new_content = content[:insert_point] + tools_yaml + "\n" + content[insert_point:]
        elif "  # Add MCP servers" in content or "  mcp:" in content:
            # Insert before MCP section
            if "  # Add MCP servers" in content:
                insert_point = content.find("  # Add MCP servers")
            else:
                insert_point = content.find("  mcp:")
            new_content = content[:insert_point] + tools_yaml + "\n" + content[insert_point:]
        else:
            # Just append
            new_content = content + "\n" + tools_yaml

        tools_yaml_path.write_text(new_content, encoding="utf-8")
        return tools_yaml_path

    def write_tool(self, config: ToolConfig) -> Path:
        """Write tool configuration to .play/tools.yaml.

        Args:
            config: Tool configuration to write

        Returns:
            Path to tools.yaml

        Raises:
            FileNotFoundError: If .play/tools.yaml doesn't exist
            OSError: If file operations fail
        """
        tools_yaml_path = self._project_root / ".play" / "tools.yaml"
        if not tools_yaml_path.exists():
            msg = f"Tools configuration not found: {tools_yaml_path}"
            raise FileNotFoundError(msg)

        # Append to tools.yaml commands section
        tool_yaml = self._generate_tool_yaml(config)

        # Read existing content
        content = tools_yaml_path.read_text(encoding="utf-8")

        # Find where to insert (after other commands, before any MCP section)
        if "  # Add language-specific tools" in content:
            # Insert before the comment
            insert_point = content.find("  # Add language-specific tools")
            new_content = content[:insert_point] + tool_yaml + "\n" + content[insert_point:]
        elif "  # Add MCP servers" in content or "  mcp:" in content:
            # Insert before MCP section
            if "  # Add MCP servers" in content:
                insert_point = content.find("  # Add MCP servers")
            else:
                insert_point = content.find("  mcp:")
            new_content = content[:insert_point] + tool_yaml + "\n" + content[insert_point:]
        else:
            # Just append
            new_content = content + "\n" + tool_yaml

        tools_yaml_path.write_text(new_content, encoding="utf-8")
        return tools_yaml_path

    def _generate_tool_yaml(self, config: ToolConfig) -> str:
        """Generate YAML configuration for the tool.

        Args:
            config: Tool configuration

        Returns:
            YAML string for the tool
        """
        yaml_parts = [
            f"    - id: {config.id}",
            f"      bin: {config.bin}",
        ]

        if config.args_allow:
            args_str = ", ".join(f'"{arg}"' for arg in config.args_allow)
            yaml_parts.append(f"      args_allow: [{args_str}]")

        yaml_parts.append(f'      timeout: "{config.timeout}"')

        return "\n".join(yaml_parts)
