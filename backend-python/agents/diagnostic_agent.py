import asyncio
import json

from langchain_openai import ChatOpenAI

from agents.state import AgentState
from agents.utils import emit_event, parse_llm_json
from config import settings
from mcp_local.tools.knowledge_search import search_runbooks
from mcp_local.tools.log_query import query_logs
from mcp_local.tools.metrics_query import query_metrics

_llm = ChatOpenAI(model=settings.llm_model, temperature=settings.llm_temperature)

DIAGNOSTIC_PROMPT = """You are an SRE diagnostic agent. Analyze the collected evidence and provide a diagnosis.

Alert: {alert_json}
Category: {category}
Severity: {severity}

=== Logs ===
{logs}

=== Metrics ===
{metrics}

=== Relevant Runbooks ===
{runbooks}

Provide your diagnosis as JSON:
- diagnosis: detailed analysis of what went wrong (2-4 paragraphs)
- root_cause: single sentence root cause
- confidence: float 0.0-1.0
"""


async def collect_evidence(state: AgentState) -> dict:
    scenario = state.get("scenario", "unknown")
    alert = state["alert"]
    query_text = f"{alert.get('rule_name', '')} {alert.get('message', '')}"

    log_result, metrics_result, runbook_result = await asyncio.gather(
        query_logs(scenario),
        query_metrics(scenario),
        search_runbooks(query_text, top_k=3),
    )

    output = {
        "logs": log_result.get("entries", []),
        "metrics": metrics_result.get("series", []),
        "runbook_matches": runbook_result.get("matches", []),
        "current_stage": "evidence_collection",
    }
    await emit_event(state, "evidence_collection", {
        "log_count": len(output["logs"]),
        "metric_count": len(output["metrics"]),
        "runbook_matches": len(output["runbook_matches"]),
    })
    return output


async def diagnostic_node(state: AgentState) -> dict:
    alert = state["alert"]
    logs = state.get("logs", [])
    metrics = state.get("metrics", [])
    runbook_matches = state.get("runbook_matches", [])

    runbook_texts = "\n".join(
        m.get("chunk_text", "No content") for m in runbook_matches
    ) or "No matching runbooks found."

    prompt = DIAGNOSTIC_PROMPT.format(
        alert_json=json.dumps(alert, indent=2),
        category=state.get("category", "unknown"),
        severity=state.get("severity", "MEDIUM"),
        logs=json.dumps(logs, indent=2)[:3000],
        metrics=json.dumps(metrics, indent=2)[:2000],
        runbooks=runbook_texts[:2000],
    )

    response = await _llm.ainvoke(prompt)
    result = parse_llm_json(response.content, fallback={
        "diagnosis": response.content,
        "root_cause": "Unable to parse structured diagnosis",
        "confidence": 0.3,
    })

    output = {
        "diagnosis": result.get("diagnosis", ""),
        "root_cause": result.get("root_cause", ""),
        "current_stage": "diagnostic",
    }
    await emit_event(state, "diagnostic", {
        "root_cause": output["root_cause"],
    })
    return output
