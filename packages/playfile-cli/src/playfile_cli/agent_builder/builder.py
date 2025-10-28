"""Agent builder using Claude to generate intelligent agent configurations."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from claude_agent_sdk import query
from claude_agent_sdk.types import ClaudeAgentOptions

from playfile_cli.agent_builder.prompts import (
    AGENT_BUILDER_SYSTEM_PROMPT,
    build_agent_creation_prompt,
)


@dataclass
class AgentConfig:
    """Generated agent configuration."""

    id: str
    role: str
    model: str
    instructions_file: str
    tools_mode: str
    tools_commands: list[str]
    runtime: str
    iterations: int
    instructions_content: str


class AgentBuilder:
    """Builds custom agents using Claude's intelligence via claude-agent-sdk."""

    async def build_agent(
        self, user_instructions: str, available_tools: list[str] | None = None, working_dir: str | None = None
    ) -> AgentConfig:
        """Use Claude to build an intelligent agent configuration.

        Args:
            user_instructions: User's description of what the agent should do
            available_tools: List of available tool IDs (defaults to common tools)
            working_dir: Current working directory for project exploration

        Returns:
            AgentConfig with all necessary configuration

        Raises:
            ValueError: If Claude's response is invalid
            RuntimeError: If query fails
        """
        if available_tools is None:
            available_tools = [
                "git",
                "python",
                "pytest",
                "ruff",
                "node",
                "npm",
                "npx",
                "make",
                "cat",
                "ls",
            ]

        # Build prompt with working directory context
        user_prompt = build_agent_creation_prompt(user_instructions, available_tools, working_dir)

        # Combine system and user prompt
        full_prompt = f"{AGENT_BUILDER_SYSTEM_PROMPT}\n\n{user_prompt}"

        try:
            # Query Claude using claude-agent-sdk
            options = ClaudeAgentOptions(
                system_prompt=AGENT_BUILDER_SYSTEM_PROMPT,
                permission_mode="bypassPermissions",  # No need for permissions for this task
                cwd=working_dir,  # Set working directory for file exploration
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
                json_end = content.rfind("```")  # Use rfind to get the last closing backticks
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
            if "agent" not in data or "instructions_content" not in data:
                msg = f"Invalid response format from Claude. Expected 'agent' and 'instructions_content' keys. Got: {list(data.keys())}"
                raise ValueError(msg)

            agent_data = data["agent"]

            return AgentConfig(
                id=agent_data["id"],
                role=agent_data["role"],
                model=agent_data["model"],
                instructions_file=agent_data["instructions_file"],
                tools_mode=agent_data["tools"]["mode"],
                tools_commands=agent_data["tools"]["commands"],
                runtime=agent_data["limits"]["runtime"],
                iterations=agent_data["limits"]["iterations"],
                instructions_content=data["instructions_content"],
            )

        except Exception as e:
            msg = f"Failed to build agent: {e}"
            raise RuntimeError(msg) from e


class AgentWriter:
    """Writes agent configuration to files (Single Responsibility)."""

    def __init__(self, project_root: Path) -> None:
        """Initialize agent writer.

        Args:
            project_root: Root directory of the project
        """
        self._project_root = project_root

    def write_agent(self, config: AgentConfig) -> tuple[Path, Path]:
        """Write agent configuration to files.

        Args:
            config: Agent configuration to write

        Returns:
            Tuple of (agents_yaml_path, instructions_path)

        Raises:
            FileNotFoundError: If .play/agents.yaml doesn't exist
            OSError: If file operations fail
        """
        agents_yaml_path = self._project_root / ".play" / "agents.yaml"
        if not agents_yaml_path.exists():
            msg = f"Agents configuration not found: {agents_yaml_path}"
            raise FileNotFoundError(msg)

        # Write instructions file
        instructions_path = self._project_root / config.instructions_file
        instructions_path.parent.mkdir(parents=True, exist_ok=True)
        instructions_path.write_text(config.instructions_content, encoding="utf-8")

        # Append to agents.yaml
        agent_yaml = self._generate_agent_yaml(config)
        with agents_yaml_path.open("a", encoding="utf-8") as f:
            f.write("\n")
            f.write(agent_yaml)

        return agents_yaml_path, instructions_path

    def _generate_agent_yaml(self, config: AgentConfig) -> str:
        """Generate YAML configuration for the agent.

        Args:
            config: Agent configuration

        Returns:
            YAML string for the agent
        """
        tools_commands = ", ".join(f'"{cmd}"' for cmd in config.tools_commands)

        return f"""  - id: {config.id}
    role: "{config.role}"
    model: {config.model}
    instructions: {config.instructions_file}
    tools:
      mode: {config.tools_mode}
      commands: [{tools_commands}]
    limits:
      runtime: "{config.runtime}"
      iterations: {config.iterations}
"""
