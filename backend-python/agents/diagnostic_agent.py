async def run_diagnostic(alert: dict, triage: dict) -> dict:
    return {
        "stage": "diagnostic",
        "summary": f"Investigate alert {alert.get('rule_name', 'unknown-alert')}",
        "tools_planned": ["log_query", "metrics_query", "knowledge_search"],
        "triage": triage,
    }
