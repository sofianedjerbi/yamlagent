"""Tests for unified configuration parser."""

import tempfile
from pathlib import Path

import pytest

from playfile_core.config import YamlAgentConfig
from playfile_core.exceptions import ParseError, ValidationError
from playfile_core.parser import YamlAgentConfigParser


class TestYamlAgentConfig:
    def test_config_minimal(self):
        config = YamlAgentConfig(version=1)
        assert config.version == 1
        assert config.tools is None
        assert config.agents is None
        assert config.workflows is None

    def test_config_invalid_version(self):
        with pytest.raises(ValueError, match="Version must be >= 1"):
            YamlAgentConfig(version=0)


class TestYamlAgentConfigParser:
    def test_parse_minimal(self):
        content = "version: 1"
        parser = YamlAgentConfigParser()
        config = parser.parse(content)

        assert config.version == 1
        assert config.tools is None
        assert config.agents is None
        assert config.workflows is None

    def test_parse_with_tools_only(self):
        content = """
version: 1
tools:
  commands:
    - id: git
      bin: git
      args: ["clone"]
  mcp:
    - id: fs
      transport: stdio
      command: ["node", "server.js"]
"""
        parser = YamlAgentConfigParser()
        config = parser.parse(content)

        assert config.version == 1
        assert config.tools is not None
        assert len(config.tools.commands) == 1
        assert len(config.tools.mcp) == 1
        assert config.agents is None
        assert config.workflows is None

    def test_parse_with_agents_only(self):
        content = """
version: 1
agents:
  - id: test-agent
    role: "Test Agent"
    model: gpt-4
    instructions: "You are helpful"
"""
        parser = YamlAgentConfigParser()
        config = parser.parse(content)

        assert config.version == 1
        assert config.tools is None
        assert config.agents is not None
        assert len(config.agents.agents) == 1
        assert config.workflows is None

    def test_parse_with_workflows_only(self):
        content = """
version: 1
tasks:
  - id: test-task
    description: "Test task"
    working_dir: "."
    steps:
      - agent:
          use: test-agent
          with:
            prompt: "Do something"
"""
        parser = YamlAgentConfigParser()
        config = parser.parse(content)

        assert config.version == 1
        assert config.tools is None
        assert config.agents is None
        assert config.workflows is not None
        assert len(config.workflows.tasks) == 1

    def test_parse_complete_config(self):
        content = """
version: 1

tools:
  commands:
    - id: git
      bin: git
      args: ["clone", "push"]
  mcp:
    - id: fs
      transport: stdio
      command: ["node", "fs-server.js"]

agents:
  - id: fe-impl
    role: "Frontend Implementation"
    model: claude-code
    instructions: ./agents/frontend.md
    tools:
      mode: whitelist
      commands: ["git"]
      mcp: ["fs"]

tasks:
  - id: implement-feature
    description: "Implement new feature"
    working_dir: "."
    steps:
      - agent:
          use: fe-impl
          with:
            prompt: "Build the UI"
"""
        parser = YamlAgentConfigParser()
        config = parser.parse(content)

        assert config.version == 1
        assert config.tools is not None
        assert len(config.tools.commands) == 1
        assert config.agents is not None
        assert len(config.agents.agents) == 1
        assert config.workflows is not None
        assert len(config.workflows.tasks) == 1

    def test_parse_invalid_yaml(self):
        content = "version: 1\n  invalid: indent"
        parser = YamlAgentConfigParser()
        with pytest.raises(ParseError, match="Invalid YAML"):
            parser.parse(content)

    def test_parse_non_dict_yaml(self):
        content = "- item1\n- item2"
        parser = YamlAgentConfigParser()
        with pytest.raises(ParseError, match="must be a dictionary"):
            parser.parse(content)

    def test_parse_file_success(self):
        content = """
version: 1
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
            parser = YamlAgentConfigParser()
            config = parser.parse_file(temp_path)
            assert config.version == 1
            assert config.agents is not None
        finally:
            Path(temp_path).unlink()

    def test_parse_file_not_found(self):
        parser = YamlAgentConfigParser()
        with pytest.raises(ParseError, match="File not found"):
            parser.parse_file("/nonexistent/file.yaml")

    def test_parse_with_imports_tools(self):
        # Create tools import file
        tools_content = """
tools:
  commands:
    - id: npm
      bin: npm
      args: ["install", "run"]
  mcp:
    - id: web
      transport: stdio
      command: ["node", "web-server.js"]
"""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False, dir="/tmp"
        ) as tools_file:
            tools_file.write(tools_content)
            tools_path = Path(tools_file.name)

        # Create main config with import
        main_content = f"""
version: 1
imports:
  - {tools_path.name}

tools:
  commands:
    - id: git
      bin: git
"""
        try:
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".yaml", delete=False, dir="/tmp"
            ) as main_file:
                main_file.write(main_content)
                main_path = Path(main_file.name)

            parser = YamlAgentConfigParser()
            config = parser.parse_file(main_path)

            # Should have merged commands from both files
            assert config.tools is not None
            assert len(config.tools.commands) == 2  # git + npm
            assert len(config.tools.mcp) == 1  # web
            assert config.tools.get_command("git") is not None
            assert config.tools.get_command("npm") is not None
        finally:
            tools_path.unlink()
            main_path.unlink()

    def test_parse_with_imports_agents(self):
        # Create agents import file
        agents_content = """
agents:
  - id: be-impl
    role: "Backend Implementation"
    model: gpt-4
    instructions: "Backend agent"
"""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False, dir="/tmp"
        ) as agents_file:
            agents_file.write(agents_content)
            agents_path = Path(agents_file.name)

        # Create main config with import
        main_content = f"""
version: 1
imports:
  - {agents_path.name}

agents:
  - id: fe-impl
    role: "Frontend Implementation"
    model: claude-code
    instructions: "Frontend agent"
"""
        try:
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".yaml", delete=False, dir="/tmp"
            ) as main_file:
                main_file.write(main_content)
                main_path = Path(main_file.name)

            parser = YamlAgentConfigParser()
            config = parser.parse_file(main_path)

            # Should have both agents
            assert config.agents is not None
            assert len(config.agents.agents) == 2
            assert config.agents.get_agent("fe-impl") is not None
            assert config.agents.get_agent("be-impl") is not None
        finally:
            agents_path.unlink()
            main_path.unlink()

    def test_parse_with_imports_workflows(self):
        # Create workflow import file
        workflow_content = """
tasks:
  - id: task-1
    description: "Imported task"
    working_dir: "."
"""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False, dir="/tmp"
        ) as workflow_file:
            workflow_file.write(workflow_content)
            workflow_path = Path(workflow_file.name)

        # Create main config with import
        main_content = f"""
version: 1
imports:
  - {workflow_path.name}

tasks:
  - id: task-2
    description: "Main task"
    working_dir: "."
"""
        try:
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".yaml", delete=False, dir="/tmp"
            ) as main_file:
                main_file.write(main_content)
                main_path = Path(main_file.name)

            parser = YamlAgentConfigParser()
            config = parser.parse_file(main_path)

            # Should have both tasks
            assert config.workflows is not None
            assert len(config.workflows.tasks) == 2
            assert config.workflows.get_task("task-1") is not None
            assert config.workflows.get_task("task-2") is not None
        finally:
            workflow_path.unlink()
            main_path.unlink()

    def test_parse_with_multiple_imports(self):
        # Create tools import
        tools_content = """
tools:
  commands:
    - id: git
      bin: git
"""
        # Create agents import
        agents_content = """
agents:
  - id: test-agent
    role: "Test"
    model: gpt-4
    instructions: "Test"
"""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False, dir="/tmp"
        ) as tools_file:
            tools_file.write(tools_content)
            tools_path = Path(tools_file.name)

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False, dir="/tmp"
        ) as agents_file:
            agents_file.write(agents_content)
            agents_path = Path(agents_file.name)

        # Create main config importing both
        main_content = f"""
version: 1
imports:
  - {tools_path.name}
  - {agents_path.name}
"""
        try:
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".yaml", delete=False, dir="/tmp"
            ) as main_file:
                main_file.write(main_content)
                main_path = Path(main_file.name)

            parser = YamlAgentConfigParser()
            config = parser.parse_file(main_path)

            assert config.tools is not None
            assert len(config.tools.commands) == 1
            assert config.agents is not None
            assert len(config.agents.agents) == 1
        finally:
            tools_path.unlink()
            agents_path.unlink()
            main_path.unlink()

    def test_parse_import_file_not_found(self):
        content = """
version: 1
imports:
  - /nonexistent/import.yaml
"""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False, dir="/tmp"
        ) as f:
            f.write(content)
            temp_path = Path(f.name)

        try:
            parser = YamlAgentConfigParser()
            with pytest.raises(ParseError, match="Import file not found"):
                parser.parse_file(temp_path)
        finally:
            temp_path.unlink()
