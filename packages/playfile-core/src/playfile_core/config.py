"""Unified configuration model for Playfile."""

from __future__ import annotations

from dataclasses import dataclass, field

from playfile_core.agents.agent_config import AgentsConfig
from playfile_core.tools.agent_tools import AgentTools
from playfile_core.workflows.workflow import Workflow


@dataclass(frozen=True)
class YamlAgentConfig:
    """Complete unified configuration for Playfile.

    This is the root configuration that combines tools, agents, and workflows.
    Can be loaded from a single YAML file or multiple files using imports.

    Attributes:
        version: Configuration version
        tools: Tool configurations (commands and MCP servers)
        agents: Agent configurations
        workflows: Workflow configurations
    """

    version: int
    tools: AgentTools | None = None
    agents: AgentsConfig | None = None
    workflows: Workflow | None = None

    def __post_init__(self) -> None:
        """Validate unified configuration."""
        if self.version < 1:
            msg = f"Version must be >= 1, got {self.version}"
            raise ValueError(msg)
