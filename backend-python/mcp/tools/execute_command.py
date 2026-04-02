async def execute_command(command: str) -> dict:
    return {
        "tool": "execute_command",
        "command": command,
        "success": True,
        "mode": "simulated",
    }
