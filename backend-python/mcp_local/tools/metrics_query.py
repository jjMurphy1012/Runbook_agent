import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[3] / "data" / "simulated_metrics"


async def query_metrics(scenario: str) -> dict:
    """Read simulated metrics for a given alert scenario."""
    metrics_file = DATA_DIR / f"{scenario}.json"
    if not metrics_file.exists():
        return {
            "tool": "metrics_query",
            "scenario": scenario,
            "series": [],
            "error": f"No simulated metrics found for scenario: {scenario}",
        }
    with open(metrics_file) as f:
        series = json.load(f)
    return {"tool": "metrics_query", "scenario": scenario, "series": series}
