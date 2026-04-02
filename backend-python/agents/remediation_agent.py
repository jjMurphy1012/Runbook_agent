async def run_remediation(alert: dict, diagnostic: dict) -> dict:
    return {
        "stage": "remediation",
        "mode": "simulated",
        "actions": [
            f"Review recommended fix path for {alert.get('rule_name', 'alert')}",
            "Do not execute shell commands until safety policy is implemented",
        ],
        "diagnostic": diagnostic["summary"],
    }
