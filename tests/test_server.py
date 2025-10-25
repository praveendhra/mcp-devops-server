"""Tests for MCP server setup and tool registration."""

import pytest
from mcp_devops_server.server import create_server, TOOLS, build_tool_schema


class TestToolRegistry:
    def test_all_tools_have_handlers(self):
        for name, info in TOOLS.items():
            assert "handler" in info, f"Tool '{name}' missing handler"
            assert callable(info["handler"]), f"Tool '{name}' handler not callable"

    def test_all_tools_have_descriptions(self):
        for name, info in TOOLS.items():
            assert "description" in info, f"Tool '{name}' missing description"
            assert len(info["description"]) > 0

    def test_tool_count(self):
        assert len(TOOLS) >= 20, "Expected at least 20 tools"

    def test_tool_categories(self):
        prefixes = {name.split("_")[0] for name in TOOLS}
        expected = {"k8s", "docker", "aws", "tf", "gh", "prom"}
        assert expected.issubset(prefixes)


class TestBuildToolSchema:
    def test_basic_schema(self):
        info = {
            "description": "Test tool",
            "handler": lambda: None,
            "params": {
                "name": {"type": "string", "description": "A name", "required": True},
                "count": {"type": "integer", "description": "Count", "default": 10},
            },
        }
        tool = build_tool_schema("test_tool", info)
        assert tool.name == "test_tool"
        assert tool.description == "Test tool"
        assert "name" in tool.inputSchema["required"]
        assert "count" not in tool.inputSchema["required"]


class TestServerCreation:
    def test_create_server(self):
        server = create_server()
        assert server is not None
        assert server.name == "devops-mcp-server"
