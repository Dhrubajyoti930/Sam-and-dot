## Scratchpad

### Option 1: Automated Concept Graph Ingestion
*   **Concept:** Build a pipeline that parses `knowledge_log.json` into a local `networkx` graph, identifying hub concepts and orphan nodes.
*   **Critique:** High value for long-term knowledge retention. However, it introduces a new dependency (`networkx`) and requires significant logic for entity extraction.
*   **Trade-off:** High maintenance overhead for the graph schema vs. superior structural understanding.

### Option 2: TTL-based Semantic Cache Pruning
*   **Concept:** Implement a "decay" mechanism in `bag/semantic_cache.py` where cache entries have a `last_accessed` timestamp and a `TTL`. Entries exceeding the TTL are purged during `run_cycle`.
*   **Critique:** Directly addresses the "noise" concern in the self-correction section. It is lightweight, uses existing infrastructure, and improves cache hit quality.
*   **Trade-off:** Requires careful tuning of TTL values to avoid premature deletion of high-value, low-frequency knowledge.

**Selection:** Option 2. It aligns with the "Minimal footprint, maximum leverage" core trait and directly addresses the self-correction weakness identified in the previous cycle.

---

## Idea: TTL-based Semantic Cache Decay
Implement a `decay_cache()` function in `bag/semantic_cache.py` that removes entries older than 30 days and updates the `last_accessed` timestamp on every cache hit.

## Why
The current semantic cache grows monotonically. Over time, stale information (outdated API signatures, deprecated patterns) pollutes the context window. A TTL mechanism ensures the cache remains a high-signal asset, reducing the risk of "hallucinating" based on obsolete data.

## Implementation Steps
1.  **Modify `bag/semantic_cache.py`**: Add a `last_accessed` field to the cache schema.
2.  **Update `check_cache`**: Update the `last_accessed` timestamp to `datetime.utcnow()` upon a successful hit.
3.  **Create `decay_cache()`**: A function that queries the cache DB for entries where `last_accessed < (now - 30 days)` and deletes them.
4.  **Integrate**: Call `decay_cache()` at the start of `run_cycle` within the `_bag_data` initialization block.

## Risk
**Failure Mode:** The cache might purge a "foundational" concept that is rarely accessed but critical (e.g., a specific system prompt or core architectural rule).
**Mitigation:** Implement a "pinned" flag in the cache schema for entries that should never be purged, and ensure the `decay_cache` logic respects this flag.

**Confidence Score:** 9/10