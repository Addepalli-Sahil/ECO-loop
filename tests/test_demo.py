from src.eco_loop.mcp_server import BuildingToolRegistry, extract_runtime_errors


def test_tool_registry_only_invokes_registered_tools():
    tools = BuildingToolRegistry({"errors": extract_runtime_errors})
    assert tools.call("errors", log_text="** Severe ** Missing schedule") == ["** Severe ** Missing schedule"]
