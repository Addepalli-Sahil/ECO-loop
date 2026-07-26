"""Small, dependency-free tool registry for the building agent.

The hackathon permits an MCP server *or custom agentic tools*.  This registry is
the custom-tools boundary: callers can discover tools and invoke only named,
validated operations.  It is intentionally transport-independent so it can be
exposed through MCP/HTTP later without coupling the controller to a vendor SDK.
"""

from __future__ import annotations

from typing import Any, Callable, Dict, Iterable


class BuildingToolRegistry:
    """Expose a deliberately small allow-list of agent operations."""

    def __init__(self, tools: Dict[str, Callable[..., Any]]):
        self._tools = dict(tools)

    def list_tools(self) -> Iterable[str]:
        return tuple(sorted(self._tools))

    def call(self, name: str, **arguments: Any) -> Any:
        if name not in self._tools:
            raise ValueError(f"Tool '{name}' is not registered")
        return self._tools[name](**arguments)


def extract_runtime_errors(log_text: str, limit: int = 20) -> list[str]:
    """Return concise EnergyPlus error/warning lines for an agent prompt."""
    markers = ("severe", "fatal", "warning", "error")
    return [
        line.strip() for line in log_text.splitlines()
        if any(marker in line.lower() for marker in markers)
    ][:limit]
