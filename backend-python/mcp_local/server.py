from mcp_local.tool_schemas import TOOLS, TOOL_SCHEMAS


def list_tools() -> list[dict]:
    return TOOL_SCHEMAS


def get_langchain_tools():
    return TOOLS
