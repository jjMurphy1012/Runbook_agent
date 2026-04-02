async def run_postmortem(alert: dict, diagnostic: dict, remediation: dict) -> dict:
    return {
        "stage": "postmortem",
        "title": f"Runbook draft for {alert.get('rule_name', 'incident')}",
        "status": "PENDING_REVIEW",
        "source_summary": diagnostic["summary"],
        "proposed_actions": remediation["actions"],
    }
