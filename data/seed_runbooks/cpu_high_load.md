# CPU High Load

## Symptoms

- CPU usage sustained above 90% for > 5 minutes
- Request latency p99 spikes to seconds
- GC pause times increase dramatically
- Health checks failing, pods marked NotReady

## Root Cause

Typically caused by: runaway threads or infinite loops, memory pressure triggering excessive GC, sudden traffic spikes beyond horizontal scaling capacity, or CPU-intensive operations (serialization, encryption) in hot paths.

## Diagnosis Steps

1. Check CPU breakdown: user vs system vs iowait — `top` or `mpstat`
2. Identify hot threads: `jstack <pid>` or async-profiler flame graph
3. Check GC logs: frequency and duration of full GC pauses
4. Review heap usage: if heap > 85%, GC pressure likely the root cause
5. Check recent deployments for algorithmic regressions
6. Verify horizontal scaling: are all replicas similarly affected?

## Remediation

1. **Immediate**: If single pod, scale horizontally to spread load
2. **Short-term**: Restart affected pods to clear accumulated state
3. **Medium-term**: Profile and optimize hot code paths
4. **Long-term**: Set CPU resource limits, add autoscaling policy based on CPU threshold

## Verification

- CPU usage drops below 60%
- GC pause times return to < 100ms
- p99 latency returns to baseline
- Health checks passing, all pods Ready
