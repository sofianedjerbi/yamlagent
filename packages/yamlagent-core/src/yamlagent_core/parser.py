"""Unified parser for yamlagent configuration with import support."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from dacite import Config, from_dict
from dacite.exceptions import DaciteError

from yamlagent_core.agents.agent_config import AgentsConfig
from yamlagent_core.agents.parser import AgentsConfigParser
from yamlagent_core.agents.tools_config import ToolsMode
from yamlagent_core.config import YamlAgentConfig
from yamlagent_core.exceptions import ParseError, ValidationError
from yamlagent_core.tools.agent_tools import AgentTools
from yamlagent_core.tools.parser import AgentToolsParser
from yamlagent_core.workflows.parser import WorkflowParser
from yamlagent_core.workflows.workflow import Workflow


class YamlAgentConfigParser:
    """Unified parser for complete yamlagent configuration.

    Supports:
    - Single YAML file with all configuration
    - Multiple YAML files with imports
    - Merging tools, agents, and workflows from multiple sources
    """

    def __init__(self) -> None:
        """Initialize unified parser."""
        self._tools_parser = AgentToolsParser()
        self._agents_parser = AgentsConfigParser()
        self._workflow_parser = WorkflowParser()
        self._dacite_config = Config(
            strict=True,
            cast=[Path],
        )

    def parse(self, content: str, base_path: Path | None = None) -> YamlAgentConfig:
        """Parse YAML content into unified configuration.

        Args:
            content: YAML string content
            base_path: Base directory for resolving imports (optional)

        Returns:
            YamlAgentConfig object

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

        return self._parse_with_imports(data, base_path)

    def parse_file(self, file_path: str | Path) -> YamlAgentConfig:
        """Parse YAML file into unified configuration.

        Args:
            file_path: Path to YAML file

        Returns:
            YamlAgentConfig object

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

        return self.parse(content, base_path=path.parent)

    def _parse_with_imports(
        self, data: dict[str, Any], base_path: Path | None = None
    ) -> YamlAgentConfig:
        """Parse configuration and resolve imports.

        Args:
            data: Parsed YAML data
            base_path: Base directory for resolving imports

        Returns:
            YamlAgentConfig with merged data from imports

        Raises:
            ParseError: If import file not found or invalid
            ValidationError: If validation fails
        """
        # Process imports first
        imports = data.get("imports", [])
        if imports and base_path:
            data = self._merge_imports(data, imports, base_path)

        # Extract version (required)
        if "version" not in data:
            data["version"] = 1

        # Parse each section independently
        tools = None
        agents = None
        workflows = None

        try:
            # Parse tools section if present
            if "tools" in data:
                tools_data = {"version": data["version"], "tools": data["tools"]}
                tools = self._parse_tools_section(tools_data)

            # Parse agents section if present
            if "agents" in data:
                agents = self._parse_agents_section({"agents": data["agents"]})

            # Parse workflows section if present
            if "tasks" in data:
                workflow_data = {
                    "version": data["version"],
                    "tasks": data["tasks"],
                }
                workflows = self._parse_workflows_section(workflow_data)

            # Create unified config
            config_data = {
                "version": data["version"],
                "tools": tools,
                "agents": agents,
                "workflows": workflows,
            }

            return from_dict(
                data_class=YamlAgentConfig, data=config_data, config=self._dacite_config
            )

        except DaciteError as e:
            msg = f"Invalid configuration: {e}"
            raise ValidationError(msg) from e
        except ValueError as e:
            # Catch validation errors from __post_init__
            msg = f"Invalid configuration: {e}"
            raise ValidationError(msg) from e

    def _merge_imports(
        self, data: dict[str, Any], imports: list[str], base_path: Path
    ) -> dict[str, Any]:
        """Merge imported YAML files into main data.

        Args:
            data: Main configuration data
            imports: List of import file paths
            base_path: Base directory for resolving imports

        Returns:
            Merged configuration data

        Raises:
            ParseError: If import file not found or invalid
        """
        merged_tools = data.get("tools", {})
        merged_agents = data.get("agents", [])
        merged_tasks = data.get("tasks", [])

        for import_path in imports:
            import_file = base_path / import_path
            if not import_file.exists():
                msg = f"Import file not found: {import_file}"
                raise ParseError(msg)

            try:
                import_content = import_file.read_text(encoding="utf-8")
                import_data = yaml.safe_load(import_content)

                if not isinstance(import_data, dict):
                    msg = f"Import file must contain a dictionary: {import_file}"
                    raise ParseError(msg)

                # Merge tools
                if "tools" in import_data:
                    import_tools = import_data["tools"]
                    if "commands" in import_tools:
                        if "commands" not in merged_tools:
                            merged_tools["commands"] = []
                        merged_tools["commands"].extend(import_tools["commands"])
                    if "mcp" in import_tools:
                        if "mcp" not in merged_tools:
                            merged_tools["mcp"] = []
                        merged_tools["mcp"].extend(import_tools["mcp"])

                # Merge agents
                if "agents" in import_data:
                    merged_agents.extend(import_data["agents"])

                # Merge tasks
                if "tasks" in import_data:
                    merged_tasks.extend(import_data["tasks"])

            except yaml.YAMLError as e:
                msg = f"Invalid YAML in import file {import_file}: {e}"
                raise ParseError(msg) from e
            except OSError as e:
                msg = f"Failed to read import file {import_file}: {e}"
                raise ParseError(msg) from e

        # Update data with merged content
        if merged_tools:
            data["tools"] = merged_tools
        if merged_agents:
            data["agents"] = merged_agents
        if merged_tasks:
            data["tasks"] = merged_tasks

        return data

    def _parse_tools_section(self, data: dict[str, Any]) -> AgentTools | None:
        """Parse tools section using AgentToolsParser.

        Args:
            data: Tools configuration data

        Returns:
            AgentTools object or None if no tools
        """
        # Convert back to YAML string for existing parser
        if "tools" in data or "version" in data:
            yaml_str = yaml.dump(data)
            return self._tools_parser.parse(yaml_str)
        return None

    def _parse_agents_section(self, data: dict[str, Any]) -> AgentsConfig | None:
        """Parse agents section directly without re-serialization.

        Args:
            data: Agents configuration data

        Returns:
            AgentsConfig object or None if no agents
        """
        if not data.get("agents"):
            return None

        # Preprocess tools mode enum for all agents
        for agent_data in data["agents"]:
            if "tools" in agent_data and isinstance(agent_data["tools"], dict):
                if "mode" not in agent_data["tools"]:
                    agent_data["tools"]["mode"] = ToolsMode.WHITELIST
                elif isinstance(agent_data["tools"]["mode"], str):
                    try:
                        agent_data["tools"]["mode"] = ToolsMode(
                            agent_data["tools"]["mode"]
                        )
                    except ValueError as e:
                        agent_id = agent_data.get("id", "unknown")
                        msg = f"Invalid tools mode in agent '{agent_id}'"
                        raise ValidationError(msg) from e

            # Convert instruction paths
            if "instructions" in agent_data:
                inst = agent_data["instructions"]
                if isinstance(inst, str) and (
                    inst.endswith((".md", ".txt")) or "/" in inst or "\\" in inst
                ):
                    agent_data["instructions"] = Path(inst)

        # Parse directly using dacite instead of re-serializing to YAML
        try:
            filtered_data = {"agents": data.get("agents", [])}
            return from_dict(
                data_class=AgentsConfig,
                data=filtered_data,
                config=self._dacite_config,
            )
        except DaciteError as e:
            msg = f"Invalid agents configuration: {e}"
            raise ValidationError(msg) from e
        except ValueError as e:
            msg = f"Invalid agents configuration: {e}"
            raise ValidationError(msg) from e

    def _parse_workflows_section(self, data: dict[str, Any]) -> Workflow | None:
        """Parse workflows section using WorkflowParser.

        Args:
            data: Workflow configuration data

        Returns:
            Workflow object or None if no workflows
        """
        if not data.get("tasks"):
            return None

        yaml_str = yaml.dump(data)
        return self._workflow_parser.parse(yaml_str)
