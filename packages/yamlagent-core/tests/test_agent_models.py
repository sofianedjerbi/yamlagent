"""Tests for agent domain models."""

from pathlib import Path

import pytest

from yamlagent_core.agents import (
    Agent,
    AgentLimits,
    AgentsConfig,
    AgentToolsConfig,
    ToolsMode,
)


class TestToolsMode:
    def test_tools_mode_enum(self):
        assert ToolsMode.WHITELIST.value == "whitelist"
        assert ToolsMode.BLACKLIST.value == "blacklist"


class TestAgentToolsConfig:
    def test_tools_config_creation_whitelist(self):
        config = AgentToolsConfig(
            mode=ToolsMode.WHITELIST,
            commands=["git", "npm"],
            mcp=["fs", "web"],
        )
        assert config.mode == ToolsMode.WHITELIST
        assert config.commands == ["git", "npm"]
        assert config.mcp == ["fs", "web"]

    def test_tools_config_creation_blacklist(self):
        config = AgentToolsConfig(
            mode=ToolsMode.BLACKLIST,
            commands=["rm"],
            mcp=["dangerous"],
        )
        assert config.mode == ToolsMode.BLACKLIST
        assert config.commands == ["rm"]
        assert config.mcp == ["dangerous"]

    def test_tools_config_defaults(self):
        config = AgentToolsConfig(mode=ToolsMode.WHITELIST)
        assert config.commands == []
        assert config.mcp == []

    def test_tools_config_immutable(self):
        config = AgentToolsConfig(mode=ToolsMode.WHITELIST)
        with pytest.raises(Exception):
            config.mode = ToolsMode.BLACKLIST


class TestAgentLimits:
    def test_limits_creation_full(self):
        limits = AgentLimits(runtime="25m", iterations=6)
        assert limits.runtime == "25m"
        assert limits.iterations == 6

    def test_limits_defaults(self):
        limits = AgentLimits()
        assert limits.runtime is None
        assert limits.iterations is None

    def test_limits_runtime_only(self):
        limits = AgentLimits(runtime="1h")
        assert limits.runtime == "1h"
        assert limits.iterations is None

    def test_limits_iterations_only(self):
        limits = AgentLimits(iterations=10)
        assert limits.runtime is None
        assert limits.iterations == 10

    def test_limits_invalid_iterations(self):
        with pytest.raises(ValueError, match="iterations must be >= 1"):
            AgentLimits(iterations=0)

        with pytest.raises(ValueError, match="iterations must be >= 1"):
            AgentLimits(iterations=-1)

    def test_limits_immutable(self):
        limits = AgentLimits(runtime="25m")
        with pytest.raises(Exception):
            limits.runtime = "30m"


class TestAgent:
    def test_agent_creation_minimal(self):
        agent = Agent(
            id="fe-impl",
            role="Frontend Implementation",
            model="claude-code",
            instructions="./agents/frontend.md",
        )
        assert agent.id == "fe-impl"
        assert agent.role == "Frontend Implementation"
        assert agent.model == "claude-code"
        assert agent.instructions == "./agents/frontend.md"
        assert agent.tools is None
        assert agent.limits is None

    def test_agent_creation_full(self):
        tools = AgentToolsConfig(
            mode=ToolsMode.WHITELIST,
            commands=["git", "npm"],
            mcp=["fs", "web"],
        )
        limits = AgentLimits(runtime="25m", iterations=6)

        agent = Agent(
            id="fe-impl",
            role="Frontend Implementation",
            model="claude-code",
            instructions="./agents/frontend.md",
            tools=tools,
            limits=limits,
        )

        assert agent.id == "fe-impl"
        assert agent.tools == tools
        assert agent.limits == limits

    def test_agent_empty_id(self):
        with pytest.raises(ValueError, match="id cannot be empty"):
            Agent(
                id="",
                role="Test",
                model="gpt-4",
                instructions="test.md",
            )

    def test_agent_empty_role(self):
        with pytest.raises(ValueError, match="role cannot be empty"):
            Agent(
                id="test",
                role="",
                model="gpt-4",
                instructions="test.md",
            )

    def test_agent_empty_model(self):
        with pytest.raises(ValueError, match="model cannot be empty"):
            Agent(
                id="test",
                role="Test",
                model="",
                instructions="test.md",
            )

    def test_agent_empty_instructions(self):
        with pytest.raises(ValueError, match="instructions cannot be empty"):
            Agent(
                id="test",
                role="Test",
                model="gpt-4",
                instructions="",
            )

    def test_agent_get_instructions_path_file(self):
        agent = Agent(
            id="test",
            role="Test",
            model="gpt-4",
            instructions="./agents/test.md",
        )
        path = agent.get_instructions_path()
        assert path == Path("./agents/test.md")

    def test_agent_get_instructions_path_with_path_object(self):
        agent = Agent(
            id="test",
            role="Test",
            model="gpt-4",
            instructions=Path("./agents/test.md"),
        )
        path = agent.get_instructions_path()
        assert path == Path("./agents/test.md")

    def test_agent_get_instructions_path_inline(self):
        agent = Agent(
            id="test",
            role="Test",
            model="gpt-4",
            instructions="You are a helpful assistant",
        )
        path = agent.get_instructions_path()
        assert path is None

    def test_agent_is_command_allowed_whitelist(self):
        tools = AgentToolsConfig(
            mode=ToolsMode.WHITELIST,
            commands=["git", "npm"],
        )
        agent = Agent(
            id="test",
            role="Test",
            model="gpt-4",
            instructions="test.md",
            tools=tools,
        )

        assert agent.is_command_allowed("git") is True
        assert agent.is_command_allowed("npm") is True
        assert agent.is_command_allowed("rm") is False

    def test_agent_is_command_allowed_blacklist(self):
        tools = AgentToolsConfig(
            mode=ToolsMode.BLACKLIST,
            commands=["rm", "dd"],
        )
        agent = Agent(
            id="test",
            role="Test",
            model="gpt-4",
            instructions="test.md",
            tools=tools,
        )

        assert agent.is_command_allowed("rm") is False
        assert agent.is_command_allowed("dd") is False
        assert agent.is_command_allowed("git") is True

    def test_agent_is_command_allowed_no_tools(self):
        agent = Agent(
            id="test",
            role="Test",
            model="gpt-4",
            instructions="test.md",
        )

        assert agent.is_command_allowed("git") is None

    def test_agent_is_mcp_allowed_whitelist(self):
        tools = AgentToolsConfig(
            mode=ToolsMode.WHITELIST,
            mcp=["fs", "web"],
        )
        agent = Agent(
            id="test",
            role="Test",
            model="gpt-4",
            instructions="test.md",
            tools=tools,
        )

        assert agent.is_mcp_allowed("fs") is True
        assert agent.is_mcp_allowed("web") is True
        assert agent.is_mcp_allowed("dangerous") is False

    def test_agent_is_mcp_allowed_blacklist(self):
        tools = AgentToolsConfig(
            mode=ToolsMode.BLACKLIST,
            mcp=["dangerous"],
        )
        agent = Agent(
            id="test",
            role="Test",
            model="gpt-4",
            instructions="test.md",
            tools=tools,
        )

        assert agent.is_mcp_allowed("dangerous") is False
        assert agent.is_mcp_allowed("fs") is True

    def test_agent_is_mcp_allowed_no_tools(self):
        agent = Agent(
            id="test",
            role="Test",
            model="gpt-4",
            instructions="test.md",
        )

        assert agent.is_mcp_allowed("fs") is None

    def test_agent_immutable(self):
        agent = Agent(
            id="test",
            role="Test",
            model="gpt-4",
            instructions="test.md",
        )
        with pytest.raises(Exception):
            agent.id = "new-id"


class TestAgentsConfig:
    def test_agents_config_creation(self):
        agent1 = Agent(
            id="agent1",
            role="Role 1",
            model="gpt-4",
            instructions="test1.md",
        )
        agent2 = Agent(
            id="agent2",
            role="Role 2",
            model="claude-code",
            instructions="test2.md",
        )
        config = AgentsConfig(agents=[agent1, agent2])

        assert len(config.agents) == 2
        assert config.agents[0] == agent1
        assert config.agents[1] == agent2

    def test_agents_config_defaults(self):
        config = AgentsConfig()
        assert config.agents == []

    def test_agents_config_duplicate_ids(self):
        agent1 = Agent(
            id="same-id",
            role="Role 1",
            model="gpt-4",
            instructions="test1.md",
        )
        agent2 = Agent(
            id="same-id",
            role="Role 2",
            model="claude-code",
            instructions="test2.md",
        )
        with pytest.raises(ValueError, match="Duplicate agent IDs"):
            AgentsConfig(agents=[agent1, agent2])

    def test_agents_config_get_agent_exists(self):
        agent = Agent(
            id="test",
            role="Test",
            model="gpt-4",
            instructions="test.md",
        )
        config = AgentsConfig(agents=[agent])

        assert config.get_agent("test") == agent

    def test_agents_config_get_agent_not_exists(self):
        config = AgentsConfig()
        assert config.get_agent("nonexistent") is None

    def test_agents_config_immutable(self):
        config = AgentsConfig()
        with pytest.raises(Exception):
            config.agents = []
