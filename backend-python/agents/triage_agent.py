import json

from langchain_openai import ChatOpenAI

from agents.fingerprint import compute_fingerprint as _compute_fingerprint
from agents.state import AgentState
from agents.utils import emit_event, parse_llm_json
from cache.diagnosis_cache import read_cache
from config import settings

_llm = ChatOpenAI(model=settings.llm_model, temperature=settings.llm_temperature)

TRIAGE_PROMPT = """You are an SRE triage agent. Classify this alert and assess its severity.

Alert:
{alert_json}

Respond in JSON with these fields:
- category: one of [database, compute, storage, network, application]
- severity: one of [LOW, MEDIUM, HIGH, CRITICAL]
- ambiguity_score: float 0.0-1.0 (how ambiguous the root cause is; 1.0 = very unclear)
- summary: one-sentence triage summary
"""


def compute_fingerprint(alert: dict) -> str:
    return _compute_fingerprint(alert.get("rule_name", ""), alert.get("labels", {}))


async def triage_node(state: AgentState) -> dict:
    alert = state["alert"]
    fingerprint = compute_fingerprint(alert)
    scenario = alert.get("rule_name", "unknown").replace(" ", "_").lower()

    cached = await read_cache(fingerprint)
    if cached:
        result = {
            "fingerprint": fingerprint,
            "scenario": scenario,
            "category": cached.get("category", "unknown"),
            "severity": cached.get("severity", "MEDIUM"),
            "ambiguity_score": cached.get("ambiguity_score", 0.5),
            "cache_hit": True,
            "diagnosis": cached.get("diagnosis", ""),
            "root_cause": cached.get("root_cause", ""),
            "current_stage": "triage",
        }
        await emit_event(state, "triage", {"cache_hit": True, **result})
        return result

    prompt = TRIAGE_PROMPT.format(alert_json=json.dumps(alert, indent=2))
    response = await _llm.ainvoke(prompt)

    result = parse_llm_json(response.content, fallback={
        "category": alert.get("category", "unknown"),
        "severity": alert.get("severity", "MEDIUM"),
        "ambiguity_score": 0.5,
        "summary": "Triage classification failed, using alert defaults",
    })

    output = {
        "fingerprint": fingerprint,
        "scenario": scenario,
        "category": result.get("category", "unknown"),
        "severity": result.get("severity", "MEDIUM"),
        "ambiguity_score": result.get("ambiguity_score", 0.5),
        "cache_hit": False,
        "use_reflection": (
            result.get("severity") in ("HIGH", "CRITICAL")
            or result.get("ambiguity_score", 0) > 0.5
        ),
        "current_stage": "triage",
    }
    await emit_event(state, "triage", {
        "category": output["category"],
        "severity": output["severity"],
        "use_reflection": output["use_reflection"],
    })
    return output
