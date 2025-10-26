"""Tests for agent YAML parser."""

import tempfile
from pathlib import Path

import pytest

from yamlagent_core.agents import ToolsMode
from yamlagent_core.agents.parser import (
    AgentConfigParser,
    AgentLimitsParser,
    AgentsConfigParser,
    AgentToolsConfigParser,
    YAMLAgentLoader,
)
from yamlagent_core.exceptions import ParseError, ValidationError


class TestYAMLAgentLoader:
    def test_load_valid_yaml(self):
        content = "key: value\nlist:\n  - item1\n  - item2"
        loader = YAMLAgentLoader()
        result = loader.load(content)
        assert result == {"key": "value", "list": ["item1", "item2"]}

    def test_load_invalid_yaml(self):
        content = "key: value\n  invalid: indent"
        loader = YAMLAgentLoader()
        with pytest.raises(ParseError, match="Invalid YAML"):
            loader.load(content)

    def test_load_non_dict_yaml(self):
        content = "- item1\n- item2"
        loader = YAMLAgentLoader()
        with pytest.raises(ParseError, match="must be a dictionary"):
            loader.load(content)


class TestAgentToolsConfigParser:
    def test_parse_whitelist(self):
        data = {
            "mode": "whitelist",
            "commands": ["git", "npm"],
            "mcp": ["fs", "web"],
        }
        parser = AgentToolsConfigParser()
        config = parser.parse(data)

        assert config.mode == ToolsMode.WHITELIST
        assert config.commands == ["git", "npm"]
        assert config.mcp == ["fs", "web"]

    def test_parse_blacklist(self):
        data = {
            "mode": "blacklist",
            "commands": ["rm"],
            "mcp": ["dangerous"],
        }
        parser = AgentToolsConfigParser()
        config = parser.parse(data)

        assert config.mode == ToolsMode.BLACKLIST
        assert config.commands == ["rm"]
        assert config.mcp == ["dangerous"]

    def test_parse_default_mode(self):
        data = {"commands": ["git"]}
        parser = AgentToolsConfigParser()
        config = parser.parse(data)

        assert config.mode == ToolsMode.WHITELIST

    def test_parse_defaults(self):
        data = {"mode": "whitelist"}
        parser = AgentToolsConfigParser()
        config = parser.parse(data)

        assert config.commands == []
        assert config.mcp == []

    def test_parse_invalid_mode(self):
        data = {"mode": "invalid"}
        parser = AgentToolsConfigParser()
        with pytest.raises(ValidationError, match="Invalid tools mode"):
            parser.parse(data)


class TestAgentLimitsParser:
    def test_parse_full(self):
        data = {"runtime": "25m", "iterations": 6}
        parser = AgentLimitsParser()
        limits = parser.parse(data)

        assert limits.runtime == "25m"
        assert limits.iterations == 6

    def test_parse_runtime_only(self):
        data = {"runtime": "1h"}
        parser = AgentLimitsParser()
        limits = parser.parse(data)

        assert limits.runtime == "1h"
        assert limits.iterations is None

    def test_parse_iterations_only(self):
        data = {"iterations": 10}
        parser = AgentLimitsParser()
        limits = parser.parse(data)

        assert limits.runtime is None
        assert limits.iterations == 10

    def test_parse_empty(self):
        data = {}
        parser = AgentLimitsParser()
        limits = parser.parse(data)

        assert limits.runtime is None
        assert limits.iterations is None

    def test_parse_invalid_iterations(self):
        data = {"iterations": 0}
        parser = AgentLimitsParser()
        with pytest.raises(ValidationError, match="Invalid agent limits"):
            parser.parse(data)


class TestAgentConfigParser:
    def test_parse_minimal(self):
        data = {
            "id": "test-agent",
            "role": "Test Role",
            "model": "gpt-4",
            "instructions": "./agents/test.md",
        }
        parser = AgentConfigParser()
        agent = parser.parse(data)

        assert agent.id == "test-agent"
        assert agent.role == "Test Role"
        assert agent.model == "gpt-4"
        assert agent.instructions == Path("./agents/test.md")
        assert agent.tools is None
        assert agent.limits is None

    def test_parse_full(self):
        data = {
            "id": "fe-impl",
            "role": "Frontend Implementation",
            "model": "claude-code",
            "instructions": "./agents/frontend.md",
            "tools": {
                "mode": "whitelist",
                "commands": ["git", "npm", "sed"],
                "mcp": ["fs", "gitmcp", "web"],
            },
            "limits": {"runtime": "25m", "iterations": 6},
        }
        parser = AgentConfigParser()
        agent = parser.parse(data)

        assert agent.id == "fe-impl"
        assert agent.role == "Frontend Implementation"
        assert agent.model == "claude-code"
        assert agent.instructions == Path("./agents/frontend.md")

        assert agent.tools is not None
        assert agent.tools.mode == ToolsMode.WHITELIST
        assert agent.tools.commands == ["git", "npm", "sed"]
        assert agent.tools.mcp == ["fs", "gitmcp", "web"]

        assert agent.limits is not None
        assert agent.limits.runtime == "25m"
        assert agent.limits.iterations == 6

    def test_parse_inline_instructions(self):
        data = {
            "id": "test",
            "role": "Test",
            "model": "gpt-4",
            "instructions": "You are a helpful assistant",
        }
        parser = AgentConfigParser()
        agent = parser.parse(data)

        assert agent.instructions == "You are a helpful assistant"

    def test_parse_missing_id(self):
        data = {
            "role": "Test",
            "model": "gpt-4",
            "instructions": "test.md",
        }
        parser = AgentConfigParser()
        with pytest.raises(ValidationError, match="missing value"):
            parser.parse(data)

    def test_parse_missing_role(self):
        data = {
            "id": "test",
            "model": "gpt-4",
            "instructions": "test.md",
        }
        parser = AgentConfigParser()
        with pytest.raises(ValidationError, match="missing value"):
            parser.parse(data)

    def test_parse_missing_model(self):
        data = {
            "id": "test",
            "role": "Test",
            "instructions": "test.md",
        }
        parser = AgentConfigParser()
        with pytest.raises(ValidationError, match="missing value"):
            parser.parse(data)

    def test_parse_missing_instructions(self):
        data = {
            "id": "test",
            "role": "Test",
            "model": "gpt-4",
        }
        parser = AgentConfigParser()
        with pytest.raises(ValidationError, match="missing value"):
            parser.parse(data)


class TestAgentsConfigParser:
    def test_parse_complete_config(self):
        content = """
agents:
  - id: fe-impl
    role: "Frontend Implementation"
    instructions: ./agents/frontend.md
    model: claude-code
    tools:
      mode: whitelist
      commands: ["git","npm","sed"]
      mcp: ["fs","gitmcp","web"]
    limits:
      runtime: "25m"
      iterations: 6

  - id: be-impl
    role: "Backend Implementation"
    instructions: ./agents/backend.md
    model: gpt-4
    tools:
      mode: blacklist
      commands: ["rm"]
      mcp: []
    limits:
      runtime: "30m"
      iterations: 10
"""
        parser = AgentsConfigParser()
        config = parser.parse(content)

        assert len(config.agents) == 2

        # Check first agent
        fe_agent = config.get_agent("fe-impl")
        assert fe_agent is not None
        assert fe_agent.role == "Frontend Implementation"
        assert fe_agent.model == "claude-code"
        assert fe_agent.tools is not None
        assert fe_agent.tools.mode == ToolsMode.WHITELIST
        assert "git" in fe_agent.tools.commands
        assert fe_agent.limits is not None
        assert fe_agent.limits.runtime == "25m"
        assert fe_agent.limits.iterations == 6

        # Check second agent
        be_agent = config.get_agent("be-impl")
        assert be_agent is not None
        assert be_agent.role == "Backend Implementation"
        assert be_agent.model == "gpt-4"
        assert be_agent.tools is not None
        assert be_agent.tools.mode == ToolsMode.BLACKLIST

    def test_parse_minimal_config(self):
        content = """
agents:
  - id: simple-agent
    role: "Simple Agent"
    model: gpt-4
    instructions: "You are helpful"
"""
        parser = AgentsConfigParser()
        config = parser.parse(content)

        assert len(config.agents) == 1
        agent = config.get_agent("simple-agent")
        assert agent is not None
        assert agent.tools is None
        assert agent.limits is None

    def test_parse_empty_agents(self):
        content = "agents: []"
        parser = AgentsConfigParser()
        config = parser.parse(content)

        assert config.agents == []

    def test_parse_no_agents_key(self):
        content = "other_key: value"
        parser = AgentsConfigParser()
        config = parser.parse(content)

        assert config.agents == []

    def test_parse_invalid_yaml(self):
        content = "invalid: yaml:\n  - bad indent"
        parser = AgentsConfigParser()
        with pytest.raises(ParseError):
            parser.parse(content)

    def test_parse_file_success(self):
        content = """
agents:
  - id: test-agent
    role: "Test"
    model: gpt-4
    instructions: "Test instructions"
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(content)
            temp_path = f.name

        try:
            parser = AgentsConfigParser()
            config = parser.parse_file(temp_path)
            assert len(config.agents) == 1
        finally:
            Path(temp_path).unlink()

    def test_parse_file_not_found(self):
        parser = AgentsConfigParser()
        with pytest.raises(ParseError, match="File not found"):
            parser.parse_file("/nonexistent/file.yaml")

    def test_parse_duplicate_agent_ids(self):
        content = """
agents:
  - id: same-id
    role: "Agent 1"
    model: gpt-4
    instructions: "test1"
  - id: same-id
    role: "Agent 2"
    model: claude-code
    instructions: "test2"
"""
        parser = AgentsConfigParser()
        with pytest.raises(ValidationError, match="Duplicate agent IDs"):
            parser.parse(content)

    def test_parse_with_pathlib_path(self):
        content = """
agents:
  - id: test
    role: "Test"
    model: gpt-4
    instructions: "Test"
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(content)
            temp_path = Path(f.name)

        try:
            parser = AgentsConfigParser()
            config = parser.parse_file(temp_path)
            assert len(config.agents) == 1
        finally:
            temp_path.unlink()
