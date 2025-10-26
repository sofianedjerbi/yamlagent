"""YAML parser for workflow configurations using dacite."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from dacite import Config, from_dict

from yamlagent_core.exceptions import ParseError, ValidationError
from yamlagent_core.workflows.agent_step import AgentInvocation, AgentStep
from yamlagent_core.workflows.task import Task
from yamlagent_core.workflows.workflow import Workflow


class YAMLWorkflowLoader:
    """Loads and validates YAML files."""

    @staticmethod
    def load(content: str) -> dict[str, Any]:
        """Load YAML content and return as dictionary."""
        try:
            data = yaml.safe_load(content)
            if not isinstance(data, dict):
                msg = "YAML content must be a dictionary"
                raise ParseError(msg)
            return data
        except yaml.YAMLError as e:
            msg = f"Invalid YAML: {e}"
            raise ParseError(msg) from e


class WorkflowParser:
    """Main parser for Workflow configuration using dacite for auto-parsing."""

    def __init__(self, yaml_loader: YAMLWorkflowLoader | None = None) -> None:
        """Initialize parser with optional dependencies."""
        self._yaml_loader = yaml_loader or YAMLWorkflowLoader()
        self._dacite_config = Config(
            strict=True,  # Raise errors for unknown fields
            cast=[Path],  # Auto-convert strings to Path
        )

    def parse(self, content: str, base_path: Path | None = None) -> Workflow:
        """Parse YAML content into Workflow object.

        Args:
            content: YAML string content
            base_path: Base directory for resolving import paths (optional)

        Returns:
            Workflow object

        Raises:
            ParseError: If YAML parsing fails
            ValidationError: If validation fails
        """
        data = self._yaml_loader.load(content)
        return self._parse_workflow(data, base_path)

    def parse_file(self, file_path: str | Path) -> Workflow:
        """Parse YAML file into Workflow object."""
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

    def _parse_workflow(self, data: dict[str, Any], base_path: Path | None = None) -> Workflow:
        """Parse Workflow from dictionary data using dacite."""
        try:
            # Pre-process agent steps to handle nested 'with' field
            if "tasks" in data:
                for task_data in data["tasks"]:
                    if "steps" in task_data:
                        for step_data in task_data["steps"]:
                            if "agent" in step_data and "with" in step_data["agent"]:
                                # Rename 'with' to 'with_params' for Python compatibility
                                step_data["agent"]["with_params"] = step_data["agent"].pop("with")

            # Use dacite to automatically convert dict to dataclass
            workflow = from_dict(data_class=Workflow, data=data, config=self._dacite_config)

            # Process imports if base_path is provided
            if workflow.imports and base_path:
                imported_tasks = []
                for import_path in workflow.imports:
                    imported_tasks.extend(self._load_import(import_path, base_path))

                # Create new workflow with merged tasks
                all_tasks = list(workflow.tasks) + imported_tasks
                workflow = Workflow(
                    version=workflow.version,
                    imports=workflow.imports,
                    tasks=all_tasks,
                )

            return workflow
        except (ValueError, TypeError) as e:
            msg = f"Invalid workflow configuration: {e}"
            raise ValidationError(msg) from e

    def _load_import(self, import_path: str, base_path: Path) -> list[Task]:
        """Load and parse an imported file."""
        resolved_path = base_path / import_path
        if not resolved_path.exists():
            msg = f"Import file not found: {import_path}"
            raise ParseError(msg)

        try:
            content = resolved_path.read_text(encoding="utf-8")
            data = self._yaml_loader.load(content)

            # Pre-process steps
            if "tasks" in data:
                for task_data in data["tasks"]:
                    if "steps" in task_data:
                        for step_data in task_data["steps"]:
                            if "agent" in step_data and "with" in step_data["agent"]:
                                step_data["agent"]["with_params"] = step_data["agent"].pop("with")

            # Extract and parse tasks
            tasks_data = data.get("tasks", [])
            return [
                from_dict(data_class=Task, data=task_data, config=self._dacite_config)
                for task_data in tasks_data
            ]
        except OSError as e:
            msg = f"Failed to read import file {import_path}: {e}"
            raise ParseError(msg) from e
        except (KeyError, ValueError, TypeError) as e:
            msg = f"Invalid import file {import_path}: {e}"
            raise ValidationError(msg) from e


# Expose individual parsers for backward compatibility (but they're now trivial)
class FilesConfigParser:
    """Simplified parser using dacite."""

    @staticmethod
    def parse(data: dict[str, Any]):
        """Parse files configuration."""
        from dacite.exceptions import DaciteError

        from yamlagent_core.workflows.files_config import FilesConfig

        try:
            return from_dict(data_class=FilesConfig, data=data, config=Config(strict=True))
        except DaciteError as e:
            msg = f"Invalid files configuration: {e}"
            raise ValidationError(msg) from e


class AgentStepParser:
    """Simplified parser using dacite."""

    @staticmethod
    def parse(data: dict[str, Any]):
        """Parse agent step."""
        from dacite.exceptions import DaciteError

        try:
            if "agent" in data and "with" in data["agent"]:
                data["agent"]["with_params"] = data["agent"].pop("with")
            return from_dict(data_class=AgentStep, data=data, config=Config(strict=True))
        except DaciteError as e:
            msg = f"Invalid agent step: {e}"
            raise ValidationError(msg) from e


class TaskParser:
    """Simplified parser using dacite."""

    @staticmethod
    def parse(data: dict[str, Any]):
        """Parse task."""
        from dacite.exceptions import DaciteError

        try:
            if "steps" in data:
                for step_data in data["steps"]:
                    if "agent" in step_data and "with" in step_data["agent"]:
                        step_data["agent"]["with_params"] = step_data["agent"].pop("with")
            return from_dict(data_class=Task, data=data, config=Config(strict=True, cast=[Path]))
        except DaciteError as e:
            msg = f"Invalid task: {e}"
            raise ValidationError(msg) from e
