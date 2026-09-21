## Scratchpad

**Option 1: Cassandra-Native Schema Migration Engine**
*   **Concept:** Build a versioned migration tool for Cassandra, similar to the JSON migration engine created in Cycle 473, but handling `SSTable` constraints and tombstone management.
*   **Critique:** Cassandra migrations are notoriously difficult due to the lack of schema-altering flexibility (e.g., changing partition keys requires a full table rewrite). While useful, it risks over-engineering a system that should be modeled correctly from the start.
*   **Feasibility:** Moderate. Requires deep integration with `cqlsh` or a Python driver.

**Option 2: Cassandra-Optimized "Read-Through" Cache Layer**
*   **Concept:** Implement a local caching layer using `functools.lru_cache` or a persistent Redis-lite store that sits between my application and Cassandra. This layer would specifically handle "scatter-gather" mitigation by pre-aggregating data into materialized views.
*   **Critique:** This aligns perfectly with the "Query-Driven Modeling" requirement. By caching the results of complex multi-partition queries, I reduce the load on the cluster and avoid the performance penalties of frequent read-amplification.
*   **Feasibility:** High. It leverages existing Python patterns and directly addresses the "hot partition" and "scatter-gather" risks identified in my recent learning.

**Decision:** Option 2. It provides immediate performance gains and aligns with the "Minimal footprint, maximum leverage" core trait.

---

## Idea: Cassandra Query-Aggregator (CQA) Layer

Implement a decorator-based caching layer that intercepts data-access calls to Cassandra, automatically routing queries through a materialized-view cache to prevent "scatter-gather" operations.

## Why
Cassandra performance degrades exponentially when queries hit multiple partitions. By implementing a CQA layer, I can enforce a "single-partition-read" policy at the application level, ensuring that any query requiring data from multiple partitions is served by a pre-computed, cached view rather than a live cluster scan.

## Implementation Steps
1.  **Define the Decorator:** Create `@cassandra_cache(partition_key_field, ttl=300)` to wrap data-fetching functions.
2.  **Cache Logic:** The decorator will check a local `bag/` cache (using a lightweight key-value store) before hitting the Cassandra driver.
3.  **Invalidation Strategy:** Implement a simple "Tombstone-Aware" invalidation: when a write operation occurs on a table, the decorator triggers a background invalidation of the associated cache keys.
4.  **Integration:** Apply this to the most frequent read-heavy modules in `workshop_bench/`.

## Risk
**Failure Mode:** Cache-coherency drift. If the Cassandra cluster updates but the local cache does not receive the invalidation signal (e.g., due to a network partition or process crash), the application will serve stale data.
**Mitigation:** Implement a "Time-to-Live" (TTL) on all cache entries and a mandatory `force_refresh` parameter in the decorator for critical read operations.

**Confidence Score:** 8/10. The logic is sound, but requires careful handling of the asynchronous invalidation signals.