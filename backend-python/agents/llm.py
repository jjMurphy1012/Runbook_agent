"""Single chokepoint for LLM calls so the rate limiter actually gates traffic.

Every agent that talks to ChatOpenAI must go through `llm_invoke` instead of
calling `.ainvoke` directly — otherwise the sliding-window limiter in
`cache/rate_limiter.py` is bypassed and burst alerts can blow out the API
budget. When the limiter denies a call, we back off for one window second and
retry up to `MAX_WAIT_SECONDS`, then raise.
"""

import asyncio

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage

from cache.rate_limiter import allow_request

MAX_WAIT_SECONDS = 60
RETRY_INTERVAL_SECONDS = 1


class LLMRateLimitExceeded(RuntimeError):
    pass


async def llm_invoke(llm: BaseChatModel, prompt: str) -> BaseMessage:
    waited = 0
    while not await allow_request():
        if waited >= MAX_WAIT_SECONDS:
            raise LLMRateLimitExceeded(
                f"LLM rate limit not cleared after {waited}s"
            )
        await asyncio.sleep(RETRY_INTERVAL_SECONDS)
        waited += RETRY_INTERVAL_SECONDS
    return await llm.ainvoke(prompt)
