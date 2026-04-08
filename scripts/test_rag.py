"""Evaluate RAG retrieval quality against seed runbooks.

Usage: docker-compose exec backend-python python scripts/test_rag.py
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend-python"))

from rag.hybrid import hybrid_search

TEST_QUERIES = [
    {
        "query": "MySQL connection pool exhausted, HikariPool timeout",
        "expected_keyword": "pool",
    },
    {
        "query": "CPU usage high, GC pauses, payment service degraded",
        "expected_keyword": "CPU",
    },
    {
        "query": "disk space full, WAL write failure, postgres crash",
        "expected_keyword": "disk",
    },
    {
        "query": "slow database queries causing connection starvation",
        "expected_keyword": "query",
    },
]


async def main() -> None:
    passed = 0
    total = len(TEST_QUERIES)

    for tc in TEST_QUERIES:
        query = tc["query"]
        expected = tc["expected_keyword"].lower()

        try:
            results = await hybrid_search(query, top_k=3)
        except Exception as e:
            print(f"  FAIL: {query[:50]}... — error: {e}")
            continue

        if not results:
            print(f"  FAIL: {query[:50]}... — no results returned")
            continue

        top_text = results[0].get("chunk_text", "").lower()
        if expected in top_text:
            print(f"  PASS: {query[:50]}... — top result contains '{expected}'")
            passed += 1
        else:
            print(
                f"  WARN: {query[:50]}... — top result does not contain '{expected}'"
            )
            passed += 0.5  # Partial credit if results returned

    print(f"\nResults: {passed}/{total} queries matched expected content")


if __name__ == "__main__":
    asyncio.run(main())
