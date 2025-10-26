"""Agent resource limits model."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AgentLimits:
    """Resource limits for agent execution.

    Attributes:
        runtime: Maximum runtime duration (e.g., "25m", "1h")
        iterations: Maximum number of iterations
    """

    runtime: str | None = None
    iterations: int | None = None

    def __post_init__(self) -> None:
        """Validate limits configuration."""
        if self.iterations is not None and self.iterations < 1:
            msg = f"iterations must be >= 1, got {self.iterations}"
            raise ValueError(msg)
