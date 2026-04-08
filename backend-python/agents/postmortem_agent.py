import json

from langchain_openai import ChatOpenAI

from agents.memory import write_incident
from agents.state import AgentState
from agents.utils import emit_event
from cache.diagnosis_cache import write_cache
from config import settings
from mcp_local.tools.runbook_crud import upsert_runbook

_llm = ChatOpenAI(model=settings.llm_model, temperature=settings.llm_temperature)

POSTMORTEM_PROMPT = """You are an SRE postmortem agent. Generate a reusable runbook from this incident's diagnosis and remediation.

Alert: {alert_json}
Diagnosis: {diagnosis}
Root Cause: {root_cause}
Remediation Actions: {actions}

Generate a runbook in markdown format with these sections:
# <Title>
## Symptoms
## Root Cause
## Diagnosis Steps
## Remediation
## Verification

Be specific and actionable. Include the actual commands and checks from this incident.
"""


async def postmortem_node(state: AgentState) -> dict:
    alert = state["alert"]
    fingerprint = state.get("fingerprint", "")

    prompt = POSTMORTEM_PROMPT.format(
        alert_json=json.dumps(alert, indent=2),
        diagnosis=state.get("diagnosis", ""),
        root_cause=state.get("root_cause", ""),
        actions=json.dumps(state.get("remediation_actions", []), indent=2)[:3000],
    )
    response = await _llm.ainvoke(prompt)
    runbook_content = response.content

    title = f"Runbook: {alert.get('rule_name', 'incident')}"
    crud_result = await upsert_runbook(
        title=title,
        content=runbook_content,
        root_cause=state.get("root_cause"),
    )

    # Cache the full diagnosis for future cache hits
    await write_cache(
        fingerprint,
        {
            "category": state.get("category", ""),
            "severity": state.get("severity", ""),
            "diagnosis": state.get("diagnosis", ""),
            "root_cause": state.get("root_cause", ""),
        },
    )

    # Write to incident memory
    await write_incident(
        alert=alert,
        fingerprint=fingerprint,
        diagnosis=state.get("diagnosis", ""),
        root_cause=state.get("root_cause", ""),
        runbook_id=crud_result.get("runbook_id"),
    )

    output = {
        "runbook_id": crud_result.get("runbook_id", ""),
        "runbook_title": title,
        "runbook_content": runbook_content,
        "current_stage": "postmortem",
    }
    await emit_event(state, "postmortem", {
        "runbook_id": output["runbook_id"],
        "runbook_title": title,
    })
    await emit_event(state, "complete", {"status": "done"})
    return output
