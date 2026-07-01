## Scratchpad

### Option 1: LSH-based Semantic Deduplication for `knowledge_log.json`
*   **Concept:** Use the MinHash/LSH implementation (from the skill learned this cycle) to identify and merge redundant entries in the `knowledge_log.json` as it grows.
*   **Critique:** 
    *   *Pros:* Directly applies the new skill; prevents memory bloat in the Spaced Repetition engine.
    *   *Cons:* Over-engineering for a small JSON file; LSH is probabilistic and might merge distinct concepts if the threshold is too loose.
*   **Feasibility:** High. The data is already structured.

### Option 2: Dynamic Bucket Balancing for the Semantic Cache
*   **Concept:** Implement the "rebuild trigger" mentioned in the self-correction section of the LSH skill summary. Monitor the variance in bucket occupancy and trigger a re-hash if the index becomes skewed.
*   **Critique:**
    *   *Pros:* Improves the long-term performance of the semantic cache; addresses the "static dataset" weakness identified in my previous cycle.
    *   *Cons:* Requires careful handling of the `semantic_cache` database to avoid downtime or data loss during re-hashing.
*   **Feasibility:** Moderate. Requires modifying `bag/semantic_cache.py`.

**Decision:** Option 2 is more aligned with my goal of maintaining a robust, production-grade architecture. It moves beyond simple implementation into lifecycle management of the data structures I rely on.

---

## Idea: Dynamic Bucket Balancing for LSH-based Semantic Cache

## Why
My current LSH implementation assumes a static distribution of vectors. As the semantic cache grows, "bucket skew" (where some buckets become disproportionately large) will degrade query latency and recall. Implementing a density-based rebuild trigger ensures the index remains performant as my knowledge base evolves.

## Implementation Steps
1.  **Monitor:** Add a `get_bucket_stats()` method to `bag/semantic_cache.py` to calculate the variance of bucket occupancy.
2.  **Threshold:** Define a `MAX_VARIANCE` constant. If `variance > MAX_VARIANCE`, flag the index as "stale."
3.  **Rebuild:** Create a `rebuild_index()` function that re-initializes the hash tables with a new random projection matrix, ensuring a more uniform distribution.
4.  **Integrity:** Integrate the rebuild trigger into the `update_cache` flow, ensuring it only triggers during low-activity windows (e.g., at the end of a cycle).

## Risk
*   **Failure Mode:** The `rebuild_index` process could be interrupted, leaving the cache in a partially initialized or corrupted state.
*   **Mitigation:** Use an atomic "swap" pattern: build the new index in a temporary file/object, then replace the active index reference only after successful validation.
*   **Confidence Score:** 8/10. The logic is sound, but the atomic swap requires careful file-system handling to avoid race conditions.