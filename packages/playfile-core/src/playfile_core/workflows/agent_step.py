"""Agent invocation step model."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class AgentInvocation:
    """Represents an agent invocation with parameters.

    Attributes:
        use: Agent ID to invoke
        with_params: Parameters to pass to the agent (prompt, etc.)
    """

    use: str
    with_params: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate agent invocation."""
        if not self.use:
            msg = "Agent 'use' field cannot be empty"
            raise ValueError(msg)


@dataclass(frozen=True)
class AgentStep:
    """Represents a step that invokes an agent.

    Attributes:
        agent: Agent invocation configuration
    """

    agent: AgentInvocation

    def __post_init__(self) -> None:
        """Validate agent step."""
        if self.agent is None:
            msg = "Agent step must have an 'agent' field"
            raise ValueError(msg)
