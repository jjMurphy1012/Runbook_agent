-- Alert labels feed into the fingerprint (rule_name + labels) shared by
-- Java and Python. Without them, same-rule alerts on different targets
-- collapse into a single cache entry.

ALTER TABLE alerts
    ADD COLUMN labels JSONB NOT NULL DEFAULT '{}'::jsonb;
