"""Template manager for project initialization.

This module handles template creation and file writing for project initialization,
following SOLID principles for maintainability and extensibility.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from playfile_cli.templates import template_content


class FileWriter(Protocol):
    """Protocol for writing files (Dependency Inversion Principle)."""

    def write(self, path: Path, content: str) -> None:
        """Write content to file."""
        ...

    def exists(self, path: Path) -> bool:
        """Check if file exists."""
        ...


class StandardFileWriter:
    """Standard file system writer implementation."""

    def write(self, path: Path, content: str) -> None:
        """Write content to file, creating parent directories if needed."""
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def exists(self, path: Path) -> bool:
        """Check if file exists."""
        return path.exists()


@dataclass
class TemplateFile:
    """Represents a template file to be created (Single Responsibility)."""

    relative_path: str
    content: str

    @property
    def path_obj(self) -> Path:
        """Get Path object for relative path."""
        return Path(self.relative_path)


class TemplateSet:
    """Collection of related template files (Single Responsibility)."""

    def __init__(self) -> None:
        """Initialize template set."""
        self._templates: list[TemplateFile] = []

    def add(self, relative_path: str, content: str) -> None:
        """Add a template to the set."""
        self._templates.append(TemplateFile(relative_path, content))

    @property
    def templates(self) -> list[TemplateFile]:
        """Get all templates."""
        return self._templates


class ProjectInitializer:
    """Initializes a project with template files (Open-Closed Principle)."""

    def __init__(self, file_writer: FileWriter | None = None) -> None:
        """Initialize project initializer.

        Args:
            file_writer: File writer implementation (defaults to StandardFileWriter)
        """
        self._file_writer = file_writer or StandardFileWriter()

    def initialize(
        self,
        template_set: TemplateSet,
        base_path: Path,
        overwrite: bool = False,
    ) -> tuple[list[Path], list[Path]]:
        """Initialize project with templates.

        Args:
            template_set: Set of templates to write
            base_path: Base directory for project
            overwrite: Whether to overwrite existing files

        Returns:
            Tuple of (created_files, skipped_files)
        """
        created: list[Path] = []
        skipped: list[Path] = []

        for template in template_set.templates:
            file_path = base_path / template.relative_path

            if self._file_writer.exists(file_path) and not overwrite:
                skipped.append(file_path)
                continue

            self._file_writer.write(file_path, template.content)
            created.append(file_path)

        return created, skipped


class TemplateManager:
    """Manages project templates and initialization (Facade Pattern)."""

    def __init__(self, initializer: ProjectInitializer | None = None) -> None:
        """Initialize template manager.

        Args:
            initializer: Project initializer (defaults to new ProjectInitializer)
        """
        self._initializer = initializer or ProjectInitializer()

    def create_default_templates(self) -> TemplateSet:
        """Create default project templates for general coding.

        Returns:
            TemplateSet with all default templates
        """
        templates = TemplateSet()

        # Main configuration file
        templates.add("playfile.yaml", template_content.PLAYFILE_YAML)

        # .play directory structure
        templates.add(".play/tools.yaml", template_content.TOOLS_YAML)
        templates.add(".play/agents.yaml", template_content.AGENTS_YAML)

        # Agent instruction files
        templates.add(".play/agents/coder.md", template_content.CODER_INSTRUCTIONS)
        templates.add(".play/agents/reviewer.md", template_content.REVIEWER_INSTRUCTIONS)
        templates.add(
            ".play/agents/documenter.md", template_content.DOCUMENTER_INSTRUCTIONS
        )
        templates.add(
            ".play/agents/test-writer.md", template_content.TEST_WRITER_INSTRUCTIONS
        )

        return templates

    def initialize_project(
        self,
        target_dir: Path,
        overwrite: bool = False,
    ) -> tuple[list[Path], list[Path]]:
        """Initialize a new project with default templates.

        Args:
            target_dir: Directory to initialize project in
            overwrite: Whether to overwrite existing files

        Returns:
            Tuple of (created_files, skipped_files)
        """
        templates = self.create_default_templates()
        return self._initializer.initialize(templates, target_dir, overwrite)
