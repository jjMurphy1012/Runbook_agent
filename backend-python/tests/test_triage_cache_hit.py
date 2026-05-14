"""Triage cache-hit branch returns flattened diagnosis fields."""

import asyncio
from unittest.mock import AsyncMock, patch

from agents.triage_agent import triage_node


def test_cache_hit_returns_flattened_diagnosis():
    cached = {
        "category": "database",
        "severity": "HIGH",
        "ambiguity_score": 0.3,
        "diagnosis": "Pool exhaustion from slow queries",
        "root_cause": "Missing index on orders.status",
    }
    state = {
        "alert": {
            "rule_name": "mysql_pool_exhausted",
            "labels": {"service": "payment-api", "host": "db-01"},
        }
    }
    with patch("agents.triage_agent.read_cache", new=AsyncMock(return_value=cached)), \
         patch("agents.triage_agent.emit_event", new=AsyncMock()):
        result = asyncio.run(triage_node(state))

    assert result["cache_hit"] is True
    assert result["diagnosis"] == cached["diagnosis"]
    assert result["root_cause"] == cached["root_cause"]
    assert result["category"] == "database"
    assert result["severity"] == "HIGH"
    assert result["fingerprint"] == "d596a9b8951d249f6a59167d61135183"


def test_cache_miss_falls_through_to_llm():
    state = {
        "alert": {"rule_name": "cpu_high_load", "labels": {}}
    }
    fake_llm_resp = type("R", (), {"content": '{"category":"compute","severity":"HIGH","ambiguity_score":0.4,"summary":"x"}'})()
    with patch("agents.triage_agent.read_cache", new=AsyncMock(return_value=None)), \
         patch("agents.triage_agent.emit_event", new=AsyncMock()), \
         patch("agents.triage_agent.llm_invoke", new=AsyncMock(return_value=fake_llm_resp)):
        result = asyncio.run(triage_node(state))

    assert result["cache_hit"] is False
    assert result["use_reflection"] is True  # HIGH severity
    assert "diagnosis" not in result  # only present on cache hit
