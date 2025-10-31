"""Tests for YAML parser."""

import tempfile
from pathlib import Path

import pytest

from playfile_core.exceptions import ParseError, ValidationError
from playfile_core.tools.parser import AgentToolsParser, CommandParser, MCPParser, YAMLLoader


class TestYAMLLoader:
    def test_load_valid_yaml(self):
        content = "key: value\nlist:\n  - item1\n  - item2"
        loader = YAMLLoader()
        result = loader.load(content)
        assert result == {"key": "value", "list": ["item1", "item2"]}

    def test_load_invalid_yaml(self):
        content = "key: value\n  invalid: indent"
        loader = YAMLLoader()
        with pytest.raises(ParseError, match="Invalid YAML"):
            loader.load(content)

    def test_load_non_dict_yaml(self):
        content = "- item1\n- item2"
        loader = YAMLLoader()
        with pytest.raises(ParseError, match="must be a dictionary"):
            loader.load(content)


class TestCommandParser:
    def test_parse_valid_command(self):
        data = {"id": "git", "bin": "git", "args": ["clone"], "timeout": "5m"}
        parser = CommandParser()
        cmd = parser.parse(data)
        assert cmd.id == "git"
        assert cmd.bin == "git"
        assert cmd.args == ["clone"]
        assert cmd.timeout == "5m"

    def test_parse_command_with_defaults(self):
        data = {"id": "npm", "bin": "npm"}
        parser = CommandParser()
        cmd = parser.parse(data)
        assert cmd.args == []
        assert cmd.timeout is None

    def test_parse_command_missing_id(self):
        data = {"bin": "git"}
        parser = CommandParser()
        with pytest.raises(ValidationError, match="missing value"):
            parser.parse(data)

    def test_parse_command_missing_bin(self):
        data = {"id": "git"}
        parser = CommandParser()
        with pytest.raises(ValidationError, match="missing value"):
            parser.parse(data)


class TestMCPParser:
    def test_parse_valid_mcp(self):
        data = {
            "id": "fs",
            "transport": "stdio",
            "command": ["node", "server.js"],
            "calls": ["fs.read"],
        }
        parser = MCPParser()
        mcp = parser.parse(data)
        assert mcp.id == "fs"
        assert mcp.transport == "stdio"
        assert mcp.command == ["node", "server.js"]
        assert mcp.calls == ["fs.read"]

    def test_parse_mcp_with_defaults(self):
        data = {"id": "web", "transport": "stdio", "command": ["node", "web.js"]}
        parser = MCPParser()
        mcp = parser.parse(data)
        assert mcp.calls == []

    def test_parse_mcp_missing_id(self):
        data = {"transport": "stdio", "command": ["node", "server.js"]}
        parser = MCPParser()
        with pytest.raises(ValidationError, match="missing value"):
            parser.parse(data)

    def test_parse_mcp_missing_transport(self):
        data = {"id": "fs", "command": ["node", "server.js"]}
        parser = MCPParser()
        with pytest.raises(ValidationError, match="missing value"):
            parser.parse(data)

    def test_parse_mcp_missing_command(self):
        data = {"id": "fs", "transport": "stdio"}
        parser = MCPParser()
        with pytest.raises(ValidationError, match="missing value"):
            parser.parse(data)


class TestAgentToolsParser:
    def test_parse_complete_config(self):
        content = """
version: 1
tools:
  commands:
    - id: git
      bin: git
      args: ["clone", "push"]
      timeout: "5m"
    - id: npm
      bin: npm
      args: ["ci", "run"]
      timeout: "20m"
  mcp:
    - id: fs
      transport: stdio
      command: ["node", "mcp/fs-server.js"]
      calls: ["fs.read", "fs.write"]
    - id: web
      transport: stdio
      command: ["node", "mcp/web-server.js"]
      calls: ["http.get"]
"""
        parser = AgentToolsParser()
        tools = parser.parse(content)

        assert tools.version == 1
        assert len(tools.commands) == 2
        assert len(tools.mcp) == 2

        git_cmd = tools.get_command("git")
        assert git_cmd is not None
        assert git_cmd.bin == "git"
        assert git_cmd.timeout == "5m"

        fs_mcp = tools.get_mcp("fs")
        assert fs_mcp is not None
        assert fs_mcp.transport == "stdio"
        assert "fs.read" in fs_mcp.calls

    def test_parse_minimal_config(self):
        content = "version: 1"
        parser = AgentToolsParser()
        tools = parser.parse(content)
        assert tools.version == 1
        assert tools.commands == []
        assert tools.mcp == []

    def test_parse_default_version(self):
        content = "tools:\n  commands: []"
        parser = AgentToolsParser()
        tools = parser.parse(content)
        assert tools.version == 1

    def test_parse_invalid_yaml(self):
        content = "invalid: yaml:\n  - bad indent"
        parser = AgentToolsParser()
        with pytest.raises(ParseError):
            parser.parse(content)

    def test_parse_file_success(self):
        content = """
version: 1
tools:
  commands:
    - id: git
      bin: git
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(content)
            temp_path = f.name

        try:
            parser = AgentToolsParser()
            tools = parser.parse_file(temp_path)
            assert tools.version == 1
            assert len(tools.commands) == 1
        finally:
            Path(temp_path).unlink()

    def test_parse_file_not_found(self):
        parser = AgentToolsParser()
        with pytest.raises(ParseError, match="File not found"):
            parser.parse_file("/nonexistent/file.yaml")

    def test_parse_duplicate_command_ids(self):
        content = """
version: 1
tools:
  commands:
    - id: git
      bin: git
    - id: git
      bin: git2
"""
        parser = AgentToolsParser()
        with pytest.raises(ValidationError, match="Duplicate command IDs"):
            parser.parse(content)

    def test_parse_duplicate_mcp_ids(self):
        content = """
version: 1
tools:
  mcp:
    - id: fs
      transport: stdio
      command: ["node", "server1.js"]
    - id: fs
      transport: stdio
      command: ["node", "server2.js"]
"""
        parser = AgentToolsParser()
        with pytest.raises(ValidationError, match="Duplicate MCP IDs"):
            parser.parse(content)

    def test_parse_with_pathlib_path(self):
        content = "version: 1\ntools:\n  commands: []"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(content)
            temp_path = Path(f.name)

        try:
            parser = AgentToolsParser()
            tools = parser.parse_file(temp_path)
            assert tools.version == 1
        finally:
            temp_path.unlink()
