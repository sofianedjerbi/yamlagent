"""Task model for workflow definitions."""

from __future__ import annotations

from dataclasses import dataclass, field

from playfile_core.workflows.agent_step import AgentStep
from playfile_core.workflows.files_config import FilesConfig


@dataclass(frozen=True)
class Task:
    """Represents a workflow task.

    Attributes:
        id: Unique identifier for the task
        description: Human-readable description
        working_dir: Working directory for the task
        files: File access configuration
        steps: List of steps to execute (agent invocations)
    """

    id: str
    description: str
    working_dir: str = "."
    files: FilesConfig | None = None
    steps: list[AgentStep] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Validate task configuration."""
        if not self.id:
            msg = "Task id cannot be empty"
            raise ValueError(msg)
        if not self.description:
            msg = "Task description cannot be empty"
            raise ValueError(msg)
