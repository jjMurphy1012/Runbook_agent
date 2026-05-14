import json

from langchain_openai import ChatOpenAI

from agents.llm import llm_invoke
from agents.state import AgentState
from agents.utils import emit_event, parse_llm_json
from config import settings
from mcp_local.tools.execute_command import execute_command

_llm = ChatOpenAI(model=settings.llm_model, temperature=settings.llm_temperature)

REMEDIATION_PROMPT = """You are an SRE remediation agent. Based on the diagnosis, propose safe recovery steps.

Alert: {alert_json}
Diagnosis: {diagnosis}
Root Cause: {root_cause}
Scenario: {scenario}

Requirements:
- All commands are SIMULATED — never run real shell commands
- Classify each step's risk: LOW, MEDIUM, HIGH
- Order steps from safest to most impactful
- Include a verification step after each action

Respond in JSON:
- actions: list of objects with "step" (int), "description", "command", "risk" (LOW/MEDIUM/HIGH), "verification"
- overall_risk: LOW/MEDIUM/HIGH
"""


async def remediation_node(state: AgentState) -> dict:
    alert = state["alert"]
    scenario = state.get("scenario", "unknown")

    prompt = REMEDIATION_PROMPT.format(
        alert_json=json.dumps(alert, indent=2),
        diagnosis=state.get("diagnosis", "No diagnosis available"),
        root_cause=state.get("root_cause", "Unknown"),
        scenario=scenario,
    )
    response = await llm_invoke(_llm, prompt)

    result = parse_llm_json(response.content, fallback={
        "actions": [
            {
                "step": 1,
                "description": "Review diagnosis and plan remediation manually",
                "command": "N/A",
                "risk": "LOW",
                "verification": "Confirm with on-call engineer",
            }
        ],
        "overall_risk": "MEDIUM",
    })

    actions = result.get("actions", [])
    for action in actions:
        if action.get("command") and action["command"] != "N/A":
            sim_result = await execute_command(action["command"], scenario)
            action["simulated_output"] = sim_result.get("output", "")

    output = {
        "remediation_actions": actions,
        "remediation_risk": result.get("overall_risk", "MEDIUM"),
        "current_stage": "remediation",
    }
    await emit_event(state, "remediation", {
        "action_count": len(actions),
        "overall_risk": output["remediation_risk"],
    })
    return output
