async def query_metrics(alert_scenario: str) -> dict:
    return {"tool": "metrics_query", "scenario": alert_scenario, "series": []}
