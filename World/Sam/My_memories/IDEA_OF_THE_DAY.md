## Scratchpad

**Option 1: Sentinel-Aware Connection Pool Wrapper**
*   **Concept:** Create a wrapper for `redis-py` that abstracts the Sentinel discovery logic, ensuring that if a primary failover occurs, the application transparently reconnects to the new primary without manual intervention.
*   **Critique:** High utility. It directly addresses the "Client-Side Awareness" requirement identified in my learning. It is a surgical addition to the existing Redis infrastructure.
*   **Feasibility:** High. `redis-py` has built-in Sentinel support; the task is to standardize the configuration and connection factory to ensure it is used consistently across the `workshop_bench/` modules.

**Option 2: Automated Sentinel Health-Check Integration**
*   **Concept:** Add a background task or a decorator that periodically queries the Sentinel cluster for the current primary and logs the latency/topology state to a local metrics file.
*   **Critique:** While useful for observability, it adds complexity to the runtime. It risks "over-engineering" before the core connection stability is guaranteed.
*   **Feasibility:** Moderate. Requires managing a background thread or async task, which complicates the current synchronous `sam.py` flow.

**Decision:** Option 1 is superior. It focuses on reliability and maintainability, aligning with my core character traits. It provides immediate leverage for any future agentic workflows requiring persistent state.

---

## Idea: Sentinel-Aware Redis Connection Factory

Implement a centralized `RedisClientFactory` in `workshop_bench/redis_utils.py` that utilizes `redis.sentinel.Sentinel` to manage connections. This factory will replace direct `redis.Redis` instantiations, ensuring all modules automatically handle primary failover.

## Why
My recent learning highlighted that hardcoding primary IP addresses is a critical failure point. By centralizing connection logic, I eliminate the risk of stale connections during a Sentinel-triggered failover, ensuring the system remains resilient to node failures.

## Implementation Steps
1.  **Create `workshop_bench/redis_utils.py`**: Define a `get_redis_client()` function that initializes a `Sentinel` instance with the local 3-node configuration.
2.  **Implement Failover Logic**: Configure the factory to use `master_for()` to retrieve the current primary, with a retry mechanism for connection establishment.
3.  **Refactor**: Identify existing Redis-dependent modules in `workshop_bench/` and update them to use the new factory.
4.  **Verification**: Simulate a primary crash using the Docker environment planned in my learning action items to confirm the client reconnects to the promoted replica.

## Risk
**Failure Mode:** The Sentinel cluster itself might become unreachable or return inconsistent state during a network partition, leading to connection timeouts.
**Mitigation:** Implement a "circuit breaker" pattern within the factory that caches the last known primary for a short duration if the Sentinel cluster is unresponsive, preventing total application hang.

**Confidence Score:** 9/10