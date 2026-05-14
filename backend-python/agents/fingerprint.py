"""Canonical alert fingerprint.

Mirrors com.runbookagent.util.FingerprintUtil on the Java side. Any change
here MUST be mirrored there — the string is used as a Redis cache key and
as the join key against incident_history, so drift silently breaks memory
retrieval and cache hits.

Canonical form:
    rule_name + "|" + json.dumps(labels, sort_keys=True, separators=(",", ":"))
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping


def compute_fingerprint(rule_name: str, labels: Mapping[str, str] | None) -> str:
    canonical_labels = json.dumps(
        dict(labels or {}), sort_keys=True, separators=(",", ":")
    )
    canonical = f"{rule_name or ''}|{canonical_labels}"
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:32]
