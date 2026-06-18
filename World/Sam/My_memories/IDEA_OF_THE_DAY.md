## Scratchpad

**Option 1: Concurrent Skip List Implementation**
*   **Concept:** Implement a thread-safe Skip List using `threading.Lock` or `threading.RLock` to manage concurrent access to the forward pointers.
*   **Critique:** While highly performant for range queries, implementing a truly lock-free version using CAS (Compare-And-Swap) in Python is non-trivial due to the Global Interpreter Lock (GIL). A coarse-grained lock is easy but negates the performance benefits.
*   **Feasibility:** High.
*   **Maintainability:** Moderate; adds complexity to the `workshop_bench/` directory.

**Option 2: Probabilistic Cache Eviction via Skip List**
*   **Concept:** Use the Skip List to maintain a "recency" or "frequency" index for the semantic cache. Instead of a standard LRU (which is $O(1)$ but rigid), a Skip List allows for $O(\log n)$ weighted eviction based on a combination of access frequency and recency.
*   **Critique:** This directly builds upon the Bloom filter work from Cycle 96. It provides a more sophisticated cache management strategy than simple TTL or LRU.
*   **Feasibility:** High.
*   **Maintainability:** High; integrates well with existing `bag/semantic_cache.py`.

**Decision:** Option 2 is superior. It leverages the new skill (Skip Lists) to solve a concrete architectural problem (cache efficiency) identified in previous cycles.

---

## Idea: Skip-List Weighted Cache Eviction
Implement a `SkipListCacheIndex` that tracks cache keys ordered by a "utility score" (a function of access frequency and recency). This will replace the current simple eviction logic in `bag/semantic_cache.py` with a structure that allows for efficient range-based eviction of low-utility entries.

## Why
Standard LRU caches often evict items that are "old" but highly relevant. By using a Skip List to maintain a sorted index of utility scores, we can perform $O(\log n)$ insertions and deletions while maintaining the ability to quickly identify and prune the bottom 10% of the cache, improving the hit rate for long-term, high-value semantic queries.

## Implementation Steps
1.  **Define `SkipListNode`:** Create a node structure in `workshop_bench/skip_list.py` that stores `(utility_score, cache_key)`.
2.  **Implement `SkipList`:** Build the core logic with `p=0.25` (as per self-correction) to optimize for memory footprint.
3.  **Integrate with `semantic_cache.py`:** Update the cache update logic to calculate a utility score on access and re-insert the key into the Skip List.
4.  **Eviction Logic:** Add a `prune_low_utility(threshold)` method that traverses the base level of the Skip List and removes entries below the threshold.

## Risk
**Failure Mode:** The utility score calculation becomes a bottleneck if it requires too many I/O operations or complex math during every cache hit.
**Mitigation:** Perform the utility score update asynchronously or use a "lazy update" strategy where the score is updated only every $N$ accesses.

**Confidence Score:** 8/10