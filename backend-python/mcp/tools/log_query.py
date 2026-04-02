async def query_logs(alert_scenario: str) -> dict:
    return {"tool": "log_query", "scenario": alert_scenario, "entries": []}
