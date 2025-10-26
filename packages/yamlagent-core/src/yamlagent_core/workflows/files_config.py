"""Files configuration model for workflow tasks."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class FilesConfig:
    """Configuration for file access permissions in a task.

    Attributes:
        read: List of file patterns allowed for reading
        write: List of file patterns allowed for writing
    """

    read: list[str] = field(default_factory=list)
    write: list[str] = field(default_factory=list)
