"""Tests for tool registry."""
import pytest
from src.registry import ToolRegistry


def test_register_and_get_tool():
    registry = ToolRegistry()
    registry.register(
        name="test_tool",
        description="A test tool",
        function=lambda: None,
        parameters={"param1": {"type": "string"}},
        category="testing"
    )

    tool = registry.get("test_tool")
    assert tool.name == "test_tool"
    assert tool.description == "A test tool"
    assert tool.category == "testing"


def test_get_nonexistent_tool():
    registry = ToolRegistry()
    with pytest.raises(KeyError):
        registry.get("nonexistent")


def test_list_tools_by_category():
    registry = ToolRegistry()
    registry.register("tool1", "desc", lambda: None, {}, category="k8s")
    registry.register("tool2", "desc", lambda: None, {}, category="k8s")
    registry.register("tool3", "desc", lambda: None, {}, category="aws")

    k8s_tools = registry.list_tools(category="k8s")
    assert len(k8s_tools) == 2

    aws_tools = registry.list_tools(category="aws")
    assert len(aws_tools) == 1


def test_list_categories():
    registry = ToolRegistry()
    registry.register("t1", "d", lambda: None, {}, category="k8s")
    registry.register("t2", "d", lambda: None, {}, category="aws")
    registry.register("t3", "d", lambda: None, {}, category="azure")

    categories = registry.list_categories()
    assert set(categories) == {"k8s", "aws", "azure"}


def test_check_requirements():
    registry = ToolRegistry()
    registry.register("t1", "d", lambda: None, {}, requires=["python3", "nonexistent_cmd"])

    reqs = registry.check_requirements("t1")
    assert reqs["python3"] is True
    assert reqs["nonexistent_cmd"] is False
