"""Artifact system for passing context between agent steps."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class StepArtifact:
    """Artifact produced by an agent step.

    Contains a summary of the step's work to pass to subsequent agents.
    """

    step_number: int
    agent_id: str
    agent_role: str
    summary: str

    def format_for_context(self) -> str:
        """Format artifact for inclusion in next agent's context.

        Returns:
            Formatted string to include in prompt
        """
        return f"""[Previous Step {self.step_number}: {self.agent_role}]
{self.summary}
"""


class ArtifactCollector:
    """Collects and manages artifacts from agent steps."""

    def __init__(self) -> None:
        """Initialize artifact collector."""
        self._artifacts: list[StepArtifact] = []

    def add_artifact(self, artifact: StepArtifact) -> None:
        """Add an artifact to the collection.

        Args:
            artifact: Artifact to add
        """
        self._artifacts.append(artifact)

    def get_context_for_next_step(self) -> str:
        """Get formatted context from all previous artifacts.

        Returns:
            Formatted string with all artifact summaries
        """
        if not self._artifacts:
            return ""

        context_parts = ["## Context from Previous Steps\n"]
        for artifact in self._artifacts:
            context_parts.append(artifact.format_for_context())

        return "\n".join(context_parts)

    def has_artifacts(self) -> bool:
        """Check if any artifacts have been collected.

        Returns:
            True if artifacts exist
        """
        return len(self._artifacts) > 0
