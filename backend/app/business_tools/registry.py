from typing import Any

from app.business_tools.base import BaseTool


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, BaseTool] = {}

    def register(self, tool: BaseTool) -> None:
        name = tool.name
        if not name:
            name = type(tool).__name__
        self._tools[name] = tool

    def get(self, name: str) -> BaseTool | None:
        return self._tools.get(name)

    def executor_map(self) -> dict[str, Any]:
        return {name: tool for name, tool in self._tools.items()}

    def __contains__(self, name: str) -> bool:
        return name in self._tools

    def __getitem__(self, name: str) -> BaseTool:
        tool = self._tools.get(name)
        if tool is None:
            raise KeyError(f"Tool not found: {name}")
        return tool

    def __repr__(self) -> str:
        items = ", ".join(sorted(self._tools))
        return f"ToolRegistry({items})"
