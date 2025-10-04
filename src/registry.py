"""Tool registry for MCP DevOps Server."""
from typing import Callable, Dict, Any, List
from dataclasses import dataclass, field


@dataclass
class ToolDefinition:
    """Definition of an MCP tool."""
    name: str
    description: str
    function: Callable
    parameters: Dict[str, Any]
    category: str = "general"
    requires: List[str] = field(default_factory=list)


class ToolRegistry:
    """Registry for all MCP tools."""

    def __init__(self):
        self._tools: Dict[str, ToolDefinition] = {}
        self._categories: Dict[str, List[str]] = {}

    def register(self, name: str, description: str, function: Callable,
                 parameters: Dict[str, Any], category: str = "general",
                 requires: List[str] = None):
        """Register a new tool."""
        tool = ToolDefinition(
            name=name,
            description=description,
            function=function,
            parameters=parameters,
            category=category,
            requires=requires or []
        )
        self._tools[name] = tool

        if category not in self._categories:
            self._categories[category] = []
        self._categories[category].append(name)

    def get(self, name: str) -> ToolDefinition:
        """Get a tool by name."""
        if name not in self._tools:
            raise KeyError(f"Tool '{name}' not found")
        return self._tools[name]

    def list_tools(self, category: str = None) -> List[ToolDefinition]:
        """List all tools, optionally filtered by category."""
        if category:
            names = self._categories.get(category, [])
            return [self._tools[n] for n in names]
        return list(self._tools.values())

    def list_categories(self) -> List[str]:
        """List all tool categories."""
        return list(self._categories.keys())

    def check_requirements(self, name: str) -> Dict[str, bool]:
        """Check if tool requirements are met."""
        import shutil
        tool = self.get(name)
        return {req: shutil.which(req) is not None for req in tool.requires}


# Global registry
registry = ToolRegistry()
