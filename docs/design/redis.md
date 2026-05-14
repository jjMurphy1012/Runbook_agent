# Redis Strategy

Redis serves three roles. All should be wired in step 1 because they underpin cross-service communication and agent performance.

## 1. Diagnosis Cache

Cache LLM diagnostic results keyed by alert fingerprint (rule_name + labels hash). Same alert within TTL returns cached diagnosis instead of re-running the pipeline.

- Module: `backend-python/cache/diagnosis_cache.py`
- Key: `diag:{alert_fingerprint}`
- TTL: default 30 minutes

## 2. Rate Limiter

Sliding-window limiter on LLM API calls to prevent cost blowout during burst alerts.

- Module: `backend-python/cache/rate_limiter.py`
- Key: `ratelimit:llm:{window}`

## 3. Redis Streams (Event Bus)

Python agent publishes per-step events to a Redis Stream. Java consumes and proxies to frontend via SSE. This decouples agent execution from the API layer.

Flow: `LangGraph node → Redis Stream → Java StreamController → SSE → Frontend`

- Publishers: `backend-java/RedisStreamPublisher.java`, `backend-python/workers/stream_consumer.py`
- Stream key: `alerts:{alert_id}:events`
- Consumer group: `runbook-api-group`
