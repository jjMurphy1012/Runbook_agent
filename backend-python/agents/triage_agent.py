async def run_triage(alert: dict) -> dict:
    return {
        "stage": "triage",
        "category": alert.get("category", "unknown"),
        "severity": alert.get("severity", "MEDIUM"),
        "cache_hit": False,
    }
