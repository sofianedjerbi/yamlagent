"""YAML parser for tools configuration using dacite."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from dacite import Config, from_dict
from dacite.exceptions import DaciteError

from playfile_core.exceptions import ParseError, ValidationError
from playfile_core.tools.agent_tools import AgentTools
from playfile_core.tools.command import ArgsMode


class AgentToolsParser:
    """Parser for AgentTools configuration using dacite for auto-parsing."""

    def __init__(self) -> None:
        """Initialize parser."""
        self._dacite_config = Config(
            strict=True,
            cast=[Path, ArgsMode],
        )

    def parse(self, content: str) -> AgentTools:
        """Parse YAML content into AgentTools object.

        Args:
            content: YAML string content

        Returns:
            AgentTools object

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

        # Pre-process: flatten nested tools structure
        # YAML: {version: 1, tools: {commands: [...], mcp: [...]}}
        # AgentTools expects: {version: 1, commands: [...], mcp: [...]}
        if "tools" in data:
            tools_data = data.pop("tools")
            if "commands" in tools_data:
                data["commands"] = tools_data["commands"]
            if "mcp" in tools_data:
                data["mcp"] = tools_data["mcp"]

        # Set default version if not provided
        if "version" not in data:
            data["version"] = 1

        try:
            return from_dict(data_class=AgentTools, data=data, config=self._dacite_config)
        except DaciteError as e:
            msg = f"Invalid tools configuration: {e}"
            raise ValidationError(msg) from e
        except ValueError as e:
            # Catch validation errors from __post_init__
            msg = f"Invalid tools configuration: {e}"
            raise ValidationError(msg) from e

    def parse_file(self, file_path: str | Path) -> AgentTools:
        """Parse YAML file into AgentTools object.

        Args:
            file_path: Path to YAML file

        Returns:
            AgentTools object

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
class CommandParser:
    """Simplified parser using dacite."""

    @staticmethod
    def parse(data: dict[str, Any]):
        """Parse command configuration."""
        from playfile_core.tools.command import Command

        try:
            return from_dict(data_class=Command, data=data, config=Config(strict=True))
        except DaciteError as e:
            msg = f"Invalid command configuration: {e}"
            raise ValidationError(msg) from e


class MCPParser:
    """Simplified parser using dacite."""

    @staticmethod
    def parse(data: dict[str, Any]):
        """Parse MCP server configuration."""
        from playfile_core.tools.mcp import MCP

        try:
            return from_dict(data_class=MCP, data=data, config=Config(strict=True))
        except DaciteError as e:
            msg = f"Invalid MCP configuration: {e}"
            raise ValidationError(msg) from e


class YAMLLoader:
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
