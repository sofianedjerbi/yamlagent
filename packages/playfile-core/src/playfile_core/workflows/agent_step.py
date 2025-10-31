"""Agent invocation step model."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ValidationCommand:
    """Represents a validation command with description.

    Attributes:
        command: Shell command to execute
        description: Human-readable description of what this validation does
    """

    command: str
    description: str | None = None

    def __post_init__(self) -> None:
        """Validate command configuration."""
        if not self.command:
            msg = "Validation command cannot be empty"
            raise ValueError(msg)


@dataclass(frozen=True)
class StepValidation:
    """Validation and retry configuration for an agent step.

    Attributes:
        pre_command: Command to run before agent execution (environment check)
        command: Single command or list of commands to run after agent execution
        max_retries: Maximum number of retry attempts (0 = no retries)
        continue_on_failure: If True, continue to next step even if validation fails
    """

    pre_command: str | None = None
    command: str | list[ValidationCommand] | None = None
    max_retries: int = 0
    continue_on_failure: bool = False

    def __post_init__(self) -> None:
        """Validate step validation configuration."""
        if self.max_retries < 0:
            msg = f"max_retries must be >= 0, got {self.max_retries}"
            raise ValueError(msg)

    def get_commands(self) -> list[ValidationCommand]:
        """Get all validation commands as a list.

        Returns:
            List of ValidationCommand objects
        """
        if self.command is None:
            return []

        if isinstance(self.command, str):
            return [ValidationCommand(command=self.command, description=None)]

        return self.command


@dataclass(frozen=True)
class AgentInvocation:
    """Represents an agent invocation with parameters.

    Attributes:
        use: Agent ID to invoke
        with_params: Parameters to pass to the agent (prompt, etc.)
        context_from: List of step IDs to include context from (optional)
    """

    use: str
    with_params: dict[str, str] = field(default_factory=dict)
    context_from: list[str] = field(default_factory=list)

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
        id: Optional step ID for referencing in context_from
        name: Optional human-readable step name
        validate: Optional validation and retry configuration
    """

    agent: AgentInvocation
    id: str | None = None
    name: str | None = None
    validate: StepValidation | None = None

    def __post_init__(self) -> None:
        """Validate agent step."""
        if self.agent is None:
            msg = "Agent step must have an 'agent' field"
            raise ValueError(msg)
