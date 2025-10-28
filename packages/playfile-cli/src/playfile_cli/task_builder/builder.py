"""Task builder using Claude to generate workflow tasks."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from claude_agent_sdk import query
from claude_agent_sdk.types import ClaudeAgentOptions

from playfile_cli.task_builder.prompts import (
    TASK_BUILDER_SYSTEM_PROMPT,
    build_task_creation_prompt,
)


@dataclass
class TaskConfig:
    """Generated task configuration."""

    id: str
    description: str
    working_dir: str
    files_read: list[str] | None
    files_write: list[str] | None
    steps: list[dict]


class TaskBuilder:
    """Builds custom workflow tasks using Claude's intelligence."""

    async def build_task(
        self,
        user_instructions: str,
        available_agents: list[str] | None = None,
        working_dir: str | None = None,
    ) -> TaskConfig:
        """Use Claude to build a workflow task configuration.

        Args:
            user_instructions: User's description of what the task should do
            available_agents: List of available agent IDs
            working_dir: Current working directory for project exploration

        Returns:
            TaskConfig with complete task definition

        Raises:
            ValueError: If Claude's response is invalid
            RuntimeError: If query fails
        """
        if available_agents is None:
            available_agents = []

        # Build prompt with working directory context
        user_prompt = build_task_creation_prompt(
            user_instructions, available_agents, working_dir
        )

        try:
            # Query Claude using claude-agent-sdk
            options = ClaudeAgentOptions(
                system_prompt=TASK_BUILDER_SYSTEM_PROMPT,
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
            if "task" not in data:
                msg = f"Invalid response format from Claude. Expected 'task' key. Got: {list(data.keys())}"
                raise ValueError(msg)

            task_data = data["task"]

            # Extract file patterns
            files_read = None
            files_write = None
            if "files" in task_data:
                files_read = task_data["files"].get("read")
                files_write = task_data["files"].get("write")

            return TaskConfig(
                id=task_data["id"],
                description=task_data["description"],
                working_dir=task_data.get("working_dir", "."),
                files_read=files_read,
                files_write=files_write,
                steps=task_data["steps"],
            )

        except Exception as e:
            msg = f"Failed to build task: {e}"
            raise RuntimeError(msg) from e


class TaskWriter:
    """Writes task configuration to playfile.yaml."""

    def __init__(self, project_root: Path) -> None:
        """Initialize task writer.

        Args:
            project_root: Root directory of the project
        """
        self._project_root = project_root

    def write_task(self, config: TaskConfig) -> Path:
        """Write task configuration to playfile.yaml.

        Args:
            config: Task configuration to write

        Returns:
            Path to playfile.yaml

        Raises:
            FileNotFoundError: If playfile.yaml doesn't exist
            OSError: If file operations fail
        """
        playfile_path = self._project_root / "playfile.yaml"
        if not playfile_path.exists():
            msg = f"playfile.yaml not found: {playfile_path}"
            raise FileNotFoundError(msg)

        # Append to playfile.yaml
        task_yaml = self._generate_task_yaml(config)
        with playfile_path.open("a", encoding="utf-8") as f:
            f.write("\n")
            f.write(task_yaml)

        return playfile_path

    def _generate_task_yaml(self, config: TaskConfig) -> str:
        """Generate YAML configuration for the task.

        Args:
            config: Task configuration

        Returns:
            YAML string for the task
        """
        yaml_parts = [
            f"  - id: {config.id}",
            f'    description: "{config.description}"',
            f'    working_dir: "{config.working_dir}"',
        ]

        # Add files section if present
        if config.files_read or config.files_write:
            yaml_parts.append("    files:")
            if config.files_read:
                yaml_parts.append("      read:")
                for pattern in config.files_read:
                    yaml_parts.append(f'        - "{pattern}"')
            if config.files_write:
                yaml_parts.append("      write:")
                for pattern in config.files_write:
                    yaml_parts.append(f'        - "{pattern}"')

        # Add steps
        yaml_parts.append("    steps:")
        for step in config.steps:
            if "agent" in step:
                agent_data = step["agent"]
                yaml_parts.append("      - agent:")
                yaml_parts.append(f'          use: {agent_data["use"]}')
                if "with" in agent_data:
                    yaml_parts.append("          with:")
                    for key, value in agent_data["with"].items():
                        # Handle prompt specially to preserve template syntax
                        yaml_parts.append(f'            {key}: "{value}"')

        return "\n".join(yaml_parts)
