from langchain_core.tools import tool

from mcp_local.tools.execute_command import execute_command as _exec_cmd
from mcp_local.tools.knowledge_search import search_runbooks as _search
from mcp_local.tools.log_query import query_logs as _logs
from mcp_local.tools.metrics_query import query_metrics as _metrics


@tool
async def log_query(scenario: str) -> dict:
    """Query simulated incident logs for a given alert scenario."""
    return await _logs(scenario)


@tool
async def metrics_query(scenario: str) -> dict:
    """Query simulated infrastructure metrics for a given alert scenario."""
    return await _metrics(scenario)


@tool
async def knowledge_search(query: str) -> dict:
    """Search the runbook knowledge base using hybrid RAG retrieval."""
    return await _search(query)


@tool
async def execute_command(command: str, scenario: str = "") -> dict:
    """Simulate execution of an infrastructure command (never runs real shell)."""
    return await _exec_cmd(command, scenario)


TOOLS = [log_query, metrics_query, knowledge_search, execute_command]

TOOL_SCHEMAS = [
    {"name": t.name, "description": t.description} for t in TOOLS
]
