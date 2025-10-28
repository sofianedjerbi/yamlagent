"""Agents configuration container."""

from __future__ import annotations

from dataclasses import dataclass, field

from playfile_core.agents.agent import Agent


@dataclass(frozen=True)
class AgentsConfig:
    """Container for all agent configurations.

    Attributes:
        agents: List of agent configurations
    """

    agents: list[Agent] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Validate agents configuration."""
        # Validate unique IDs
        agent_ids = [agent.id for agent in self.agents]
        if len(agent_ids) != len(set(agent_ids)):
            msg = "Duplicate agent IDs found"
            raise ValueError(msg)

    def get_agent(self, agent_id: str) -> Agent | None:
        """Get agent by ID."""
        for agent in self.agents:
            if agent.id == agent_id:
                return agent
        return None
