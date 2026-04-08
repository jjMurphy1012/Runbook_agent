import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[3] / "data" / "simulated_logs"


async def query_logs(scenario: str) -> dict:
    """Read simulated incident logs for a given alert scenario."""
    log_file = DATA_DIR / f"{scenario}.json"
    if not log_file.exists():
        return {
            "tool": "log_query",
            "scenario": scenario,
            "entries": [],
            "error": f"No simulated logs found for scenario: {scenario}",
        }
    with open(log_file) as f:
        entries = json.load(f)
    return {"tool": "log_query", "scenario": scenario, "entries": entries}
