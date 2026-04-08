# MySQL Connection Pool Exhausted

## Symptoms

- Connection pool usage > 90%
- HTTP 503 errors from dependent services
- HikariPool connection acquire timeouts
- Slow query duration spikes

## Root Cause

Slow queries hold connections longer than expected, starving the pool. Common triggers: missing indexes, table locks from long-running transactions, or sudden traffic spikes without connection limit tuning.

## Diagnosis Steps

1. Check current pool usage: `SHOW STATUS LIKE 'Threads_connected'`
2. Identify slow queries: `SHOW FULL PROCESSLIST` and slow query log
3. Check for table locks: `SHOW ENGINE INNODB STATUS`
4. Review connection pool config (max pool size, connection timeout, idle timeout)
5. Check if recent deployments changed query patterns

## Remediation

1. **Immediate**: Kill long-running queries if safe — `KILL <process_id>`
2. **Short-term**: Increase connection pool max size temporarily
3. **Medium-term**: Add missing indexes for slow queries
4. **Long-term**: Implement query timeout limits, add connection pool monitoring alerts at 70% threshold

## Verification

- Pool usage drops below 60%
- p99 query latency returns to baseline (< 200ms)
- No more 503 errors from upstream consumers
