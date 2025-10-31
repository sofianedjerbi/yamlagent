"""Tests for domain models."""

import pytest

from playfile_core.tools import AgentTools, Command, MCP


class TestCommand:
    def test_command_creation(self):
        cmd = Command(id="git", bin="git", args=["clone", "push"], timeout="5m")
        assert cmd.id == "git"
        assert cmd.bin == "git"
        assert cmd.args == ["clone", "push"]
        assert cmd.timeout == "5m"

    def test_command_defaults(self):
        cmd = Command(id="npm", bin="npm")
        assert cmd.args == []
        assert cmd.timeout is None

    def test_command_empty_id(self):
        with pytest.raises(ValueError, match="id cannot be empty"):
            Command(id="", bin="git")

    def test_command_empty_bin(self):
        with pytest.raises(ValueError, match="bin cannot be empty"):
            Command(id="git", bin="")

    def test_command_immutable(self):
        cmd = Command(id="git", bin="git")
        with pytest.raises(Exception):
            cmd.id = "new_id"


class TestMCP:
    def test_mcp_creation(self):
        mcp = MCP(
            id="fs",
            transport="stdio",
            command=["node", "server.js"],
            calls=["fs.read", "fs.write"],
        )
        assert mcp.id == "fs"
        assert mcp.transport == "stdio"
        assert mcp.command == ["node", "server.js"]
        assert mcp.calls == ["fs.read", "fs.write"]

    def test_mcp_defaults(self):
        mcp = MCP(id="web", transport="stdio", command=["node", "web.js"])
        assert mcp.calls == []

    def test_mcp_empty_id(self):
        with pytest.raises(ValueError, match="id cannot be empty"):
            MCP(id="", transport="stdio", command=["node", "server.js"])

    def test_mcp_empty_transport(self):
        with pytest.raises(ValueError, match="transport cannot be empty"):
            MCP(id="fs", transport="", command=["node", "server.js"])

    def test_mcp_empty_command(self):
        with pytest.raises(ValueError, match="command cannot be empty"):
            MCP(id="fs", transport="stdio", command=[])

    def test_mcp_immutable(self):
        mcp = MCP(id="fs", transport="stdio", command=["node", "server.js"])
        with pytest.raises(Exception):
            mcp.id = "new_id"


class TestAgentTools:
    def test_agent_tools_creation(self):
        cmd = Command(id="git", bin="git")
        mcp = MCP(id="fs", transport="stdio", command=["node", "server.js"])
        tools = AgentTools(version=1, commands=[cmd], mcp=[mcp])

        assert tools.version == 1
        assert len(tools.commands) == 1
        assert len(tools.mcp) == 1

    def test_agent_tools_defaults(self):
        tools = AgentTools(version=1)
        assert tools.commands == []
        assert tools.mcp == []

    def test_agent_tools_invalid_version(self):
        with pytest.raises(ValueError, match="Version must be >= 1"):
            AgentTools(version=0)

    def test_agent_tools_duplicate_command_ids(self):
        cmd1 = Command(id="git", bin="git")
        cmd2 = Command(id="git", bin="git")
        with pytest.raises(ValueError, match="Duplicate command IDs"):
            AgentTools(version=1, commands=[cmd1, cmd2])

    def test_agent_tools_duplicate_mcp_ids(self):
        mcp1 = MCP(id="fs", transport="stdio", command=["node", "server.js"])
        mcp2 = MCP(id="fs", transport="stdio", command=["node", "other.js"])
        with pytest.raises(ValueError, match="Duplicate MCP IDs"):
            AgentTools(version=1, mcp=[mcp1, mcp2])

    def test_get_command_exists(self):
        cmd = Command(id="git", bin="git")
        tools = AgentTools(version=1, commands=[cmd])
        assert tools.get_command("git") == cmd

    def test_get_command_not_exists(self):
        tools = AgentTools(version=1)
        assert tools.get_command("git") is None

    def test_get_mcp_exists(self):
        mcp = MCP(id="fs", transport="stdio", command=["node", "server.js"])
        tools = AgentTools(version=1, mcp=[mcp])
        assert tools.get_mcp("fs") == mcp

    def test_get_mcp_not_exists(self):
        tools = AgentTools(version=1)
        assert tools.get_mcp("fs") is None

    def test_agent_tools_immutable(self):
        tools = AgentTools(version=1)
        with pytest.raises(Exception):
            tools.version = 2
