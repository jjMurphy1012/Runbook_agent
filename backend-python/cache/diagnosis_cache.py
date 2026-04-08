import json

from cache import redis_client

CACHE_PREFIX = "diag:"
DEFAULT_TTL = 1800  # 30 minutes


async def read_cache(fingerprint: str) -> dict | None:
    key = f"{CACHE_PREFIX}{fingerprint}"
    raw = await redis_client.get(key)
    if raw is None:
        return None
    return json.loads(raw)


async def write_cache(fingerprint: str, diagnosis: dict, ttl: int = DEFAULT_TTL) -> None:
    key = f"{CACHE_PREFIX}{fingerprint}"
    await redis_client.set(key, json.dumps(diagnosis), ex=ttl)
