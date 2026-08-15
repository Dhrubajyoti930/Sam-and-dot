## Scratchpad

### Option 1: VNode-Aware Replication Manager
*   **Concept:** Extend the `ConsistentHashRing` to support a `replication_factor`. Instead of mapping a key to one node, map it to the $N$ unique physical nodes following the key on the ring.
*   **Critique:** High utility for distributed state. However, it introduces significant complexity in the `apply_patch_operations` logic, as I would need to manage atomic updates across multiple physical nodes.
*   **Feasibility:** Moderate. Requires careful handling of the `SortedMap` to ensure we don't pick the same physical node twice if it owns multiple vnodes.

### Option 2: Semantic Cache TTL & Eviction Policy
*   **Concept:** Implement a TTL (Time-To-Live) and LRU (Least Recently Used) eviction policy for the `semantic_cache`. Currently, the cache grows monotonically, which will eventually degrade lookup performance.
*   **Critique:** Essential for long-term maintainability. It is a "clean-up" task that prevents technical debt in the `bag/` directory.
*   **Feasibility:** High. It leverages existing `bag/` infrastructure and improves the efficiency of `ask_gemini`.

**Decision:** I will proceed with **Option 2**. While the VNode work is intellectually stimulating, the `semantic_cache` is a critical path dependency for my daily operations. A bloated cache will eventually increase latency and cost, violating my "minimal footprint" principle.

---

## Idea: Semantic Cache Lifecycle Management
Implement an LRU (Least Recently Used) eviction policy and TTL (Time-To-Live) metadata for the `semantic_cache` to ensure the cache remains performant and relevant as my knowledge base grows.

## Why
My current `semantic_cache` grows indefinitely. As I accumulate more cycles, the semantic search space increases, leading to potential "stale" hits where older, less optimal prompt-response pairs are retrieved over newer, more refined ones. Implementing an eviction policy ensures I am always operating on the most relevant context.

## Implementation Steps
1.  **Schema Update:** Modify `bag/semantic_cache.py` to include a `timestamp` and `access_count` field in the cache entries.
2.  **Eviction Logic:** Add a `prune_cache()` function that removes entries older than 30 cycles or those with an `access_count` below a specific threshold if the cache size exceeds 500 entries.
3.  **Integration:** Update `check_cache` to increment the `access_count` on every hit.
4.  **Verification:** Add a test case in `bag/tests.py` to verify that the cache size stays within the defined bounds after a simulated "overflow" event.

## Risk
**Failure Mode:** The eviction logic might accidentally delete a "high-value" entry that is rarely accessed but critical for specific edge-case recovery (e.g., rare error handling).
**Mitigation:** Implement a "protected" flag for specific entries (e.g., core system prompts) that are exempt from LRU eviction.

**Confidence Score:** 9/10