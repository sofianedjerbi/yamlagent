"""Workflow configuration model."""

from __future__ import annotations

from dataclasses import dataclass, field

from playfile_core.workflows.task import Task


@dataclass(frozen=True)
class Workflow:
    """Complete workflow configuration.

    Attributes:
        version: Configuration version
        imports: List of file paths to import
        tasks: List of task definitions
    """

    version: int
    imports: list[str] = field(default_factory=list)
    tasks: list[Task] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Validate workflow configuration."""
        if self.version < 1:
            msg = f"Version must be >= 1, got {self.version}"
            raise ValueError(msg)

        # Validate unique task IDs
        task_ids = [task.id for task in self.tasks]
        if len(task_ids) != len(set(task_ids)):
            msg = "Duplicate task IDs found"
            raise ValueError(msg)

    def get_task(self, task_id: str) -> Task | None:
        """Get task by ID."""
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None
