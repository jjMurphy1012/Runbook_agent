"""Cross-language fingerprint parity test.

Mirrors backend-java FingerprintUtilParityTest. The two implementations
must produce identical hashes for the same inputs — the fingerprint is
used as a Redis cache key and a join key against incident_history, so
drift silently breaks memory retrieval.
"""

from agents.fingerprint import compute_fingerprint


def test_empty_labels():
    assert (
        compute_fingerprint("mysql_pool_exhausted", {})
        == "4cf93c03078a33f24ebd3599eb10676f"
    )


def test_ordered_labels():
    fp = compute_fingerprint(
        "mysql_pool_exhausted",
        {"service": "payment-api", "host": "db-01"},
    )
    assert fp == "d596a9b8951d249f6a59167d61135183"


def test_label_order_does_not_matter():
    a = compute_fingerprint("rule", {"a": "1", "b": "2"})
    b = compute_fingerprint("rule", {"b": "2", "a": "1"})
    assert a == b


def test_none_labels_equivalent_to_empty():
    assert compute_fingerprint("r", None) == compute_fingerprint("r", {})
