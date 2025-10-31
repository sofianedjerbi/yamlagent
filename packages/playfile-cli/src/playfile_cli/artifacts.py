"""Artifact system for passing context between agent steps."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class StepArtifact:
    """Artifact produced by an agent step.

    Contains a summary of the step's work to pass to subsequent agents.
    """

    step_number: int
    step_id: str | None
    agent_id: str
    agent_role: str
    summary: str

    def format_for_context(self) -> str:
        """Format artifact for inclusion in next agent's context.

        Returns:
            Formatted string to include in prompt
        """
        label = self.step_id if self.step_id else f"Step {self.step_number}"
        return f"""[Previous {label}: {self.agent_role}]
{self.summary}
"""


class ArtifactCollector:
    """Collects and manages artifacts from agent steps."""

    def __init__(self) -> None:
        """Initialize artifact collector."""
        self._artifacts: list[StepArtifact] = []
        self._artifacts_by_id: dict[str, StepArtifact] = {}

    def add_artifact(self, artifact: StepArtifact) -> None:
        """Add an artifact to the collection.

        Args:
            artifact: Artifact to add
        """
        self._artifacts.append(artifact)
        if artifact.step_id:
            self._artifacts_by_id[artifact.step_id] = artifact

    def get_context_for_next_step(self, context_from: list[str] | None = None) -> str:
        """Get formatted context from specified or all previous artifacts.

        Args:
            context_from: List of step IDs to include. If None, includes all previous steps.

        Returns:
            Formatted string with artifact summaries
        """
        if not self._artifacts:
            return ""

        # If context_from is specified, filter artifacts
        if context_from is not None:
            artifacts_to_include = []
            for step_id in context_from:
                if step_id in self._artifacts_by_id:
                    artifacts_to_include.append(self._artifacts_by_id[step_id])
                else:
                    # Warning: step_id not found, but don't fail
                    pass

            if not artifacts_to_include:
                return ""

            context_parts = ["## Context from Previous Steps\n"]
            for artifact in artifacts_to_include:
                context_parts.append(artifact.format_for_context())

            return "\n".join(context_parts)

        # Default: include all artifacts
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
