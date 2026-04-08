from typing import Any, TypedDict


class AgentState(TypedDict, total=False):
    # Input
    alert: dict
    alert_id: str
    scenario: str

    # Triage output
    fingerprint: str
    category: str
    severity: str
    ambiguity_score: float
    cache_hit: bool
    cached_diagnosis: dict | None

    # Evidence collected by diagnostic
    logs: list[dict]
    metrics: list[dict]
    runbook_matches: list[dict]

    # Diagnostic output
    diagnosis: str
    root_cause: str

    # Reflection rounds (when reflection mode is used)
    reflection_rounds: list[dict]
    use_reflection: bool

    # Incident memory
    similar_incidents: list[dict]

    # Remediation output
    remediation_actions: list[dict]
    remediation_risk: str

    # Postmortem output
    runbook_id: str
    runbook_title: str
    runbook_content: str

    # Streaming
    events: list[dict]
    current_stage: str

    # Error tracking
    error: str | None
