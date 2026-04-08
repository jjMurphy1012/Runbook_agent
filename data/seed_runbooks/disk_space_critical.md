# Disk Space Critical

## Symptoms

- Disk usage > 90% on data volume
- Write failures: "No space left on device"
- PostgreSQL WAL write failures, possible database crash
- Log rotation failures

## Root Cause

Unbounded log growth, WAL accumulation from long-running transactions or replication lag, large temporary files from batch jobs, or misconfigured retention policies.

## Diagnosis Steps

1. Identify largest consumers: `du -sh /data/* | sort -rh | head -20`
2. Check log rotation config and whether cron jobs are running
3. Check PostgreSQL WAL size: `SELECT pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(), '0/0'))`
4. Check for replication lag holding WAL segments
5. Look for large temporary files from batch processes
6. Review retention policies for logs and backups

## Remediation

1. **Immediate**: Delete old logs and temp files — `find /data/logs -mtime +7 -delete`
2. **Immediate**: If WAL bloat, check and resolve replication lag, then `CHECKPOINT`
3. **Short-term**: Fix log rotation, set max file count and compression
4. **Medium-term**: Move WAL to separate volume, resize data volume
5. **Long-term**: Implement disk usage monitoring with alerts at 70% and 85% thresholds

## Verification

- Disk usage drops below 70%
- PostgreSQL accepting writes, WAL files rotating normally
- Log rotation completing successfully
- No write errors in application logs
