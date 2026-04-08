"""Seed alerts into the database for the local demo.

Usage: docker-compose exec backend-python python scripts/seed_data.py
"""

import asyncio
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend-python"))

from db.database import get_session
from db.models import Alert

SEED_ALERTS = [
    {
        "rule_name": "mysql_pool_exhausted",
        "category": "database",
        "severity": "HIGH",
        "fingerprint": "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4",
        "status": "PENDING",
        "message": "Connection pool usage at 96% (48/50) on service-a",
    },
    {
        "rule_name": "cpu_high_load",
        "category": "compute",
        "severity": "HIGH",
        "fingerprint": "b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5",
        "status": "PENDING",
        "message": "CPU usage at 98% for 15 minutes on payment-service",
    },
    {
        "rule_name": "disk_space_critical",
        "category": "storage",
        "severity": "CRITICAL",
        "fingerprint": "c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6",
        "status": "PENDING",
        "message": "Disk usage at 95% on /data volume, write failures occurring",
    },
]


async def main() -> None:
    async with get_session() as session:
        for alert_data in SEED_ALERTS:
            alert = Alert(
                id=uuid.uuid4(),
                fingerprint=alert_data["fingerprint"],
                rule_name=alert_data["rule_name"],
                category=alert_data["category"],
                severity=alert_data["severity"],
                status=alert_data["status"],
                message=alert_data["message"],
                created_at=datetime.now(timezone.utc),
            )
            session.add(alert)
    print(f"Seeded {len(SEED_ALERTS)} alerts.")


if __name__ == "__main__":
    asyncio.run(main())
