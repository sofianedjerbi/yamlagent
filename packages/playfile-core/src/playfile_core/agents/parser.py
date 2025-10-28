"""YAML parser for agent configurations using dacite."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from dacite import Config, from_dict
from dacite.exceptions import DaciteError

from playfile_core.agents.agent_config import AgentsConfig
from playfile_core.exceptions import ParseError, ValidationError


class AgentsConfigParser:
    """Parser for AgentsConfig using dacite for auto-parsing."""

    def __init__(self) -> None:
        """Initialize parser."""
        self._dacite_config = Config(
            strict=True,
            cast=[Path],  # Auto-convert strings to Path
        )

    def parse(self, content: str) -> AgentsConfig:
        """Parse YAML content into AgentsConfig object.

        Args:
            content: YAML string content

        Returns:
            AgentsConfig object

        Raises:
            ParseError: If YAML parsing fails
            ValidationError: If validation fails
        """
        try:
            data = yaml.safe_load(content)
            if not isinstance(data, dict):
                msg = "YAML content must be a dictionary"
                raise ParseError(msg)
        except yaml.YAMLError as e:
            msg = f"Invalid YAML: {e}"
            raise ParseError(msg) from e

        try:
            # Pre-process: convert file paths in instructions field and tools mode enum
            if "agents" in data:
                from playfile_core.agents.tools_config import ToolsMode

                for agent_data in data["agents"]:
                    # Convert instructions paths
                    if "instructions" in agent_data:
                        inst = agent_data["instructions"]
                        if isinstance(inst, str) and (
                            inst.endswith((".md", ".txt")) or "/" in inst or "\\" in inst
                        ):
                            agent_data["instructions"] = Path(inst)

                    # Convert tools mode enum
                    if "tools" in agent_data and isinstance(agent_data["tools"], dict):
                        if "mode" not in agent_data["tools"]:
                            agent_data["tools"]["mode"] = ToolsMode.WHITELIST
                        elif isinstance(agent_data["tools"]["mode"], str):
                            try:
                                agent_data["tools"]["mode"] = ToolsMode(agent_data["tools"]["mode"])
                            except ValueError as e:
                                msg = f"Invalid tools mode '{agent_data['tools']['mode']}' in agent '{agent_data.get('id', 'unknown')}'"
                                raise ValidationError(msg) from e

            # Filter to only known fields for AgentsConfig (just "agents")
            # This allows YAML files to have extra metadata that gets ignored
            filtered_data = {"agents": data.get("agents", [])}

            return from_dict(data_class=AgentsConfig, data=filtered_data, config=self._dacite_config)
        except DaciteError as e:
            msg = f"Invalid agents configuration: {e}"
            raise ValidationError(msg) from e
        except ValueError as e:
            # Catch validation errors from __post_init__
            msg = f"Invalid agents configuration: {e}"
            raise ValidationError(msg) from e

    def parse_file(self, file_path: str | Path) -> AgentsConfig:
        """Parse YAML file into AgentsConfig object.

        Args:
            file_path: Path to YAML file

        Returns:
            AgentsConfig object

        Raises:
            ParseError: If file reading or YAML parsing fails
            ValidationError: If validation fails
        """
        path = Path(file_path)
        if not path.exists():
            msg = f"File not found: {file_path}"
            raise ParseError(msg)

        try:
            content = path.read_text(encoding="utf-8")
        except OSError as e:
            msg = f"Failed to read file {file_path}: {e}"
            raise ParseError(msg) from e

        return self.parse(content)


# Expose individual parsers for backward compatibility (trivial wrappers)
class AgentToolsConfigParser:
    """Simplified parser using dacite."""

    @staticmethod
    def parse(data: dict[str, Any]):
        """Parse agent tools configuration."""
        from playfile_core.agents.tools_config import AgentToolsConfig, ToolsMode

        try:
            # Set default mode if not provided
            if "mode" not in data:
                data["mode"] = ToolsMode.WHITELIST
            # Convert mode string to enum if needed
            elif isinstance(data["mode"], str):
                try:
                    data["mode"] = ToolsMode(data["mode"])
                except ValueError as e:
                    msg = f"Invalid tools mode '{data['mode']}', must be 'whitelist' or 'blacklist'"
                    raise ValidationError(msg) from e
            return from_dict(data_class=AgentToolsConfig, data=data, config=Config(strict=True))
        except DaciteError as e:
            msg = f"Invalid tools configuration: {e}"
            raise ValidationError(msg) from e


class AgentLimitsParser:
    """Simplified parser using dacite."""

    @staticmethod
    def parse(data: dict[str, Any]):
        """Parse agent limits."""
        from playfile_core.agents.limits import AgentLimits

        try:
            return from_dict(data_class=AgentLimits, data=data, config=Config(strict=True))
        except DaciteError as e:
            msg = f"Invalid limits configuration: {e}"
            raise ValidationError(msg) from e
        except ValueError as e:
            # Catch validation errors from __post_init__
            msg = f"Invalid agent limits: {e}"
            raise ValidationError(msg) from e


class AgentConfigParser:
    """Simplified parser using dacite."""

    @staticmethod
    def parse(data: dict[str, Any]):
        """Parse individual agent."""
        from playfile_core.agents.agent import Agent
        from playfile_core.agents.tools_config import ToolsMode

        try:
            # Pre-process instructions path
            if "instructions" in data:
                inst = data["instructions"]
                if isinstance(inst, str) and (
                    inst.endswith((".md", ".txt")) or "/" in inst or "\\" in inst
                ):
                    data["instructions"] = Path(inst)

            # Pre-process nested tools mode enum
            if "tools" in data and isinstance(data["tools"], dict):
                if "mode" not in data["tools"]:
                    data["tools"]["mode"] = ToolsMode.WHITELIST
                elif isinstance(data["tools"]["mode"], str):
                    try:
                        data["tools"]["mode"] = ToolsMode(data["tools"]["mode"])
                    except ValueError as e:
                        msg = f"Invalid tools mode '{data['tools']['mode']}', must be 'whitelist' or 'blacklist'"
                        raise ValidationError(msg) from e

            return from_dict(data_class=Agent, data=data, config=Config(strict=True, cast=[Path]))
        except DaciteError as e:
            msg = f"Invalid agent configuration: {e}"
            raise ValidationError(msg) from e
        except ValueError as e:
            # Catch validation errors from __post_init__
            msg = f"Invalid agent configuration: {e}"
            raise ValidationError(msg) from e


class YAMLAgentLoader:
    """YAML loader - kept for backward compatibility."""

    @staticmethod
    def load(content: str) -> dict[str, Any]:
        """Load YAML content."""
        try:
            data = yaml.safe_load(content)
            if not isinstance(data, dict):
                msg = "YAML content must be a dictionary"
                raise ParseError(msg)
            return data
        except yaml.YAMLError as e:
            msg = f"Invalid YAML: {e}"
            raise ParseError(msg) from e
