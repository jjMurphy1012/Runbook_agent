async def upsert_runbook(payload: dict) -> dict:
    return {"tool": "runbook_crud", "status": "pending_review", "payload": payload}
