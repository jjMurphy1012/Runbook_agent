import json

from langchain_openai import ChatOpenAI

from agents.llm import llm_invoke
from agents.state import AgentState
from agents.utils import emit_event, parse_llm_json
from config import settings

_llm = ChatOpenAI(model=settings.llm_model, temperature=settings.llm_temperature)

MAX_ROUNDS = 3

ANALYZER_PROMPT = """You are an SRE diagnostic Analyzer. Provide a thorough diagnosis based on the evidence.

Alert: {alert_json}
Category: {category} | Severity: {severity}

=== Evidence ===
Logs: {logs}
Metrics: {metrics}
Runbook matches: {runbooks}

{memory_context}
{critic_feedback}

Analyze the evidence and provide:
- analysis: your detailed diagnosis (be specific, cite evidence)
- root_cause: single sentence root cause
- confidence: float 0.0-1.0
- response_to_critic: if critic feedback was provided, explain which points you accept/reject and why

Respond in JSON.
"""

CRITIC_PROMPT = """You are an SRE diagnostic Critic. Review the Analyzer's diagnosis against the raw evidence.

Alert: {alert_json}

=== Raw Evidence ===
Logs: {logs}
Metrics: {metrics}

=== Analyzer's Diagnosis ===
{analysis}

Review critically. For each issue found:
- Cite specific evidence the Analyzer missed or misinterpreted
- Propose alternative hypotheses with supporting evidence
- Flag correlation-vs-causation errors

Respond in JSON:
- issues: list of objects with "severity" (critical/major/minor), "description", "evidence"
- has_major_issues: boolean (true if any critical or major issues)
- summary: one paragraph overall assessment
"""

FINALIZER_PROMPT = """You are an SRE diagnostic Finalizer. Synthesize the final diagnosis from all reflection rounds.

Alert: {alert_json}

=== Reflection History ===
{rounds_json}

Produce a final, authoritative diagnosis:
- diagnosis: comprehensive analysis incorporating all valid insights from the debate
- root_cause: single definitive root cause statement
- confidence: float 0.0-1.0

Respond in JSON.
"""


def _format_memory(incidents: list[dict]) -> str:
    if not incidents:
        return ""
    lines = ["=== Historical Incidents (reference only) ==="]
    lines.append("These are past incidents with similar alert patterns.")
    lines.append("Use as context but diagnose the current situation independently.")
    lines.append("If your diagnosis diverges from history, state why.\n")
    for inc in incidents:
        lines.append(
            f"- [{inc.get('rule_name')}] Root cause: {inc.get('root_cause')} "
            f"(outcome: {inc.get('outcome')})"
        )
    return "\n".join(lines)


async def reflection_node(state: AgentState) -> dict:
    alert = state["alert"]
    logs = json.dumps(state.get("logs", []), indent=2)[:3000]
    metrics = json.dumps(state.get("metrics", []), indent=2)[:2000]
    runbooks = "\n".join(
        m.get("chunk_text", "") for m in state.get("runbook_matches", [])
    )[:2000]
    memory_context = _format_memory(state.get("similar_incidents", []))

    rounds: list[dict] = []
    critic_feedback = ""
    previous_analysis = ""

    for round_num in range(1, MAX_ROUNDS + 1):
        # --- Analyzer ---
        analyzer_prompt = ANALYZER_PROMPT.format(
            alert_json=json.dumps(alert, indent=2),
            category=state.get("category", "unknown"),
            severity=state.get("severity", "MEDIUM"),
            logs=logs,
            metrics=metrics,
            runbooks=runbooks,
            memory_context=memory_context if round_num == 1 else "",
            critic_feedback=(
                f"\n=== Critic Feedback from Round {round_num - 1} ===\n{critic_feedback}"
                if critic_feedback
                else ""
            ),
        )
        analyzer_resp = await llm_invoke(_llm, analyzer_prompt)
        analysis = parse_llm_json(analyzer_resp.content, fallback={
            "analysis": analyzer_resp.content,
            "root_cause": "Parse error",
            "confidence": 0.3,
        })

        await emit_event(state, "diagnostic_reflection", {
            "round": round_num,
            "role": "analyzer",
            "root_cause": analysis.get("root_cause", ""),
            "confidence": analysis.get("confidence", 0),
        })

        # Check for convergence: identical to previous round
        current_analysis_text = analysis.get("analysis", "")
        if round_num > 1 and current_analysis_text == previous_analysis:
            rounds.append({"round": round_num, "analyzer": analysis, "converged": True})
            break
        previous_analysis = current_analysis_text

        # --- Critic ---
        critic_prompt = CRITIC_PROMPT.format(
            alert_json=json.dumps(alert, indent=2),
            logs=logs,
            metrics=metrics,
            analysis=json.dumps(analysis, indent=2),
        )
        critic_resp = await llm_invoke(_llm, critic_prompt)
        critique = parse_llm_json(critic_resp.content, fallback={
            "issues": [],
            "has_major_issues": False,
            "summary": critic_resp.content,
        })

        await emit_event(state, "diagnostic_reflection", {
            "round": round_num,
            "role": "critic",
            "has_major_issues": critique.get("has_major_issues", False),
            "issue_count": len(critique.get("issues", [])),
        })

        rounds.append({
            "round": round_num,
            "analyzer": analysis,
            "critic": critique,
        })

        if not critique.get("has_major_issues", False):
            break

        critic_feedback = json.dumps(critique, indent=2)

    # --- Finalizer ---
    finalizer_prompt = FINALIZER_PROMPT.format(
        alert_json=json.dumps(alert, indent=2),
        rounds_json=json.dumps(rounds, indent=2)[:4000],
    )
    finalizer_resp = await llm_invoke(_llm, finalizer_prompt)
    final = parse_llm_json(finalizer_resp.content, fallback={
        "diagnosis": finalizer_resp.content,
        "root_cause": rounds[-1]["analyzer"].get("root_cause", "")
        if rounds
        else "",
        "confidence": 0.5,
    })

    await emit_event(state, "diagnostic_reflection", {
        "role": "finalizer",
        "total_rounds": len(rounds),
        "root_cause": final.get("root_cause", ""),
    })

    return {
        "diagnosis": final.get("diagnosis", ""),
        "root_cause": final.get("root_cause", ""),
        "reflection_rounds": rounds,
        "current_stage": "diagnostic_reflection",
    }
