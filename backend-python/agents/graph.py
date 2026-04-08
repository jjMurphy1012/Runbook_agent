from langgraph.graph import END, StateGraph

from agents.diagnostic_agent import collect_evidence, diagnostic_node
from agents.memory import memory_read_node
from agents.postmortem_agent import postmortem_node
from agents.reflection import reflection_node
from agents.remediation_agent import remediation_node
from agents.state import AgentState
from agents.triage_agent import triage_node


def _route_after_triage(state: AgentState) -> str:
    if state.get("cache_hit"):
        return "remediation"
    return "collect_evidence"


def _route_after_evidence(state: AgentState) -> str:
    if state.get("use_reflection"):
        return "memory_read"
    return "diagnostic"


def _route_after_memory(state: AgentState) -> str:
    return "reflection"


def build_graph() -> StateGraph:
    graph = StateGraph(AgentState)

    # Add nodes
    graph.add_node("triage", triage_node)
    graph.add_node("collect_evidence", collect_evidence)
    graph.add_node("memory_read", memory_read_node)
    graph.add_node("diagnostic", diagnostic_node)
    graph.add_node("reflection", reflection_node)
    graph.add_node("remediation", remediation_node)
    graph.add_node("postmortem", postmortem_node)

    # Set entry point
    graph.set_entry_point("triage")

    # Conditional: after triage, skip to remediation if cache hit, else collect evidence
    graph.add_conditional_edges(
        "triage",
        _route_after_triage,
        {"remediation": "remediation", "collect_evidence": "collect_evidence"},
    )

    # Conditional: after evidence, use reflection if needed, else single-pass diagnostic
    graph.add_conditional_edges(
        "collect_evidence",
        _route_after_evidence,
        {"memory_read": "memory_read", "diagnostic": "diagnostic"},
    )

    # Memory read leads to reflection
    graph.add_conditional_edges(
        "memory_read",
        _route_after_memory,
        {"reflection": "reflection"},
    )

    # Both diagnostic paths lead to remediation
    graph.add_edge("diagnostic", "remediation")
    graph.add_edge("reflection", "remediation")

    # Remediation leads to postmortem
    graph.add_edge("remediation", "postmortem")

    # Postmortem ends the workflow
    graph.add_edge("postmortem", END)

    return graph


# Compile the graph once at module level
workflow = build_graph().compile()


async def run_alert_workflow(alert: dict) -> dict:
    """Execute the full agent pipeline for an alert."""
    initial_state: AgentState = {
        "alert": alert,
        "alert_id": alert.get("id", ""),
        "events": [],
    }
    result = await workflow.ainvoke(initial_state)
    return {
        "alert_id": result.get("alert_id", ""),
        "fingerprint": result.get("fingerprint", ""),
        "category": result.get("category", ""),
        "severity": result.get("severity", ""),
        "cache_hit": result.get("cache_hit", False),
        "diagnosis": result.get("diagnosis", ""),
        "root_cause": result.get("root_cause", ""),
        "use_reflection": result.get("use_reflection", False),
        "reflection_rounds": result.get("reflection_rounds", []),
        "remediation_actions": result.get("remediation_actions", []),
        "remediation_risk": result.get("remediation_risk", ""),
        "runbook_id": result.get("runbook_id", ""),
        "runbook_title": result.get("runbook_title", ""),
    }
