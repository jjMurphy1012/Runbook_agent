"""Seed verified incident history for cold start.

These hand-written cases give Incident Memory non-trivial behavior from day one.
Usage: docker-compose exec backend-python python scripts/seed_incidents.py
"""

import asyncio
import json
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend-python"))

from agents.fingerprint import compute_fingerprint
from db.database import get_session
from db.models import IncidentHistory
from rag.embeddings import embed_texts

SEED_INCIDENTS = [
    {
        "rule_name": "mysql_pool_exhausted",
        "category": "database",
        "severity": "HIGH",
        "alert_payload": {
            "rule_name": "mysql_pool_exhausted",
            "category": "database",
            "severity": "HIGH",
            "message": "Connection pool usage at 96% (48/50) on service-a",
        },
        "diagnosis": "Connection pool exhaustion caused by slow queries holding connections. "
        "A missing index on orders.status led to full table scans taking 4+ seconds, "
        "preventing connection recycling under normal request load.",
        "root_cause": "Missing index on orders.status causing full table scans",
        "outcome": "resolved",
    },
    {
        "rule_name": "cpu_high_load",
        "category": "compute",
        "severity": "HIGH",
        "alert_payload": {
            "rule_name": "cpu_high_load",
            "category": "compute",
            "severity": "HIGH",
            "message": "CPU usage at 98% for 15 minutes on payment-service",
        },
        "diagnosis": "CPU spike caused by a thread contention issue in TransactionProcessor. "
        "A reentrant lock was being held across a database call, causing thread starvation "
        "and excessive context switching. GC pressure from heap exhaustion compounded the issue.",
        "root_cause": "Thread contention in TransactionProcessor holding locks across DB calls",
        "outcome": "resolved",
    },
    {
        "rule_name": "disk_space_critical",
        "category": "storage",
        "severity": "CRITICAL",
        "alert_payload": {
            "rule_name": "disk_space_critical",
            "category": "storage",
            "severity": "CRITICAL",
            "message": "Disk usage at 95% on /data volume, write failures occurring",
        },
        "diagnosis": "Disk space exhaustion from unbounded WAL growth. A stalled replication "
        "slot prevented WAL segment cleanup. Combined with aggressive application logging "
        "at DEBUG level (enabled by a recent config change), the /data volume filled in hours.",
        "root_cause": "Stalled replication slot preventing WAL cleanup + DEBUG logging enabled",
        "outcome": "resolved",
    },
    {
        "rule_name": "mysql_pool_exhausted",
        "category": "database",
        "severity": "HIGH",
        "alert_payload": {
            "rule_name": "mysql_pool_exhausted",
            "category": "database",
            "severity": "HIGH",
            "message": "Connection pool at 100%, all requests timing out on checkout-service",
        },
        "diagnosis": "Pool exhaustion caused by a connection leak. The checkout-service was "
        "acquiring connections in a try block but not releasing them in the finally block "
        "during exception paths. A spike in payment gateway timeouts triggered the leak.",
        "root_cause": "Connection leak in checkout-service exception handling path",
        "outcome": "resolved",
    },
]


async def main() -> None:
    payload_texts = [
        json.dumps(inc["alert_payload"], sort_keys=True) for inc in SEED_INCIDENTS
    ]
    try:
        embeddings = await embed_texts(payload_texts)
    except Exception as e:
        print(f"Embedding generation failed: {e}")
        print("Seeding incidents without embeddings.")
        embeddings = [None] * len(SEED_INCIDENTS)

    async with get_session() as session:
        for i, inc in enumerate(SEED_INCIDENTS):
            record = IncidentHistory(
                id=uuid.uuid4(),
                alert_fingerprint=compute_fingerprint(
                    inc["rule_name"], inc["alert_payload"].get("labels", {})
                ),
                rule_name=inc["rule_name"],
                category=inc["category"],
                severity=inc["severity"],
                alert_payload=inc["alert_payload"],
                diagnosis=inc["diagnosis"],
                root_cause=inc["root_cause"],
                outcome=inc["outcome"],
                human_verified=True,
                embedding=embeddings[i],
                created_at=datetime.now(timezone.utc),
            )
            session.add(record)

    print(f"Seeded {len(SEED_INCIDENTS)} verified incident history records.")


if __name__ == "__main__":
    asyncio.run(main())
