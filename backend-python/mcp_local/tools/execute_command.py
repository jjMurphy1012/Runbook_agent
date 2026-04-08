import json
from functools import lru_cache
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[3] / "data" / "commands"


@lru_cache(maxsize=1)
def _load_responses() -> tuple[dict, ...]:
    responses_file = DATA_DIR / "command_responses.json"
    if not responses_file.exists():
        return ()
    with open(responses_file) as f:
        return tuple(json.load(f))


async def execute_command(command: str, scenario: str = "") -> dict:
    """Simulate command execution. Never runs real shell commands."""
    for entry in _load_responses():
        if entry["command_pattern"] in command:
            if scenario and entry.get("scenario") and entry["scenario"] != scenario:
                continue
            return {
                "tool": "execute_command",
                "command": command,
                "success": entry["success"],
                "output": entry["response_message"],
                "mode": "simulated",
            }
    return {
        "tool": "execute_command",
        "command": command,
        "success": True,
        "output": f"Simulated: Command '{command}' executed successfully (no specific mock).",
        "mode": "simulated",
    }
