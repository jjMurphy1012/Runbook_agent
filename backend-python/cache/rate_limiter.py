import time

from cache import redis_client

RATE_LIMIT_PREFIX = "ratelimit:llm:"
DEFAULT_WINDOW = 60  # seconds
DEFAULT_MAX_REQUESTS = 30


async def allow_request(
    window: int = DEFAULT_WINDOW,
    max_requests: int = DEFAULT_MAX_REQUESTS,
) -> bool:
    """Sliding-window rate limiter for LLM API calls."""
    now = time.time()
    key = f"{RATE_LIMIT_PREFIX}{window}"

    pipe = redis_client.pipeline()
    pipe.zremrangebyscore(key, 0, now - window)
    pipe.zcard(key)
    pipe.zadd(key, {str(now): now})
    pipe.expire(key, window)
    results = await pipe.execute()

    current_count = results[1]
    return current_count < max_requests
