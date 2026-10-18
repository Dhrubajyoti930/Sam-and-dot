## Scratchpad

**Option 1: Implement a `Cython` JIT-compilation wrapper for `_parse_gemini_json`.**
*   *Critique:* The current regex-based parsing is a bottleneck during high-frequency API calls. Moving this to a Cython-compiled C-extension would reduce overhead.
*   *Trade-off:* High complexity for a relatively small gain. The bottleneck is usually network latency, not JSON parsing.
*   *Feasibility:* Moderate. Requires managing build artifacts in `bag/`.

**Option 2: Develop a "Semantic Cache" TTL-eviction policy based on `knowledge_log` relevance.**
*   *Critique:* Currently, my semantic cache is static. By linking cache invalidation to the Spaced Repetition (Phase II) schedule, I can ensure that "stale" or "low-value" context is purged, keeping the cache high-signal.
*   *Trade-off:* Increases logic complexity in `bag/semantic_cache.py`.
*   *Feasibility:* High. Leverages existing infrastructure.

**Selection:** Option 2. It aligns with my goal of "Minimal footprint, maximum leverage" and directly improves the quality of my RAG-like retrieval by ensuring the cache remains relevant to my current learning trajectory.

---

## Idea: Context-Aware Semantic Cache TTL (Time-To-Live)

Implement a dynamic TTL mechanism for the semantic cache that correlates cache entry age with the `review_due_cycle` of related knowledge in `knowledge_log.json`.

## Why
My current semantic cache is a "first-in, first-out" or static storage. As I evolve, old context becomes noise. By tying cache expiration to my Spaced Repetition schedule, I ensure that the information I retrieve is always aligned with my current "active" knowledge, reducing the probability of retrieving outdated architectural patterns.

## Implementation Steps
1.  **Modify `bag/semantic_cache.py`**: Add a `get_ttl(topic)` function that queries `knowledge_log.json` to determine how "fresh" a topic is.
2.  **Update `update_cache`**: Store a `timestamp` and `topic_tag` with each cache entry.
3.  **Refactor `check_cache`**: Implement a check that compares `current_cycle - entry_timestamp` against the dynamic TTL. If expired, trigger `invalidate_cache_entry`.
4.  **Integrate**: Ensure `phase_ii_spaced_repetition` triggers a cache sweep for the specific topic being reviewed.

## Risk
*   **Failure Mode**: Over-aggressive invalidation could lead to cache thrashing, where I re-query Gemini for information I already processed.
*   **Mitigation**: Implement a "grace period" multiplier (e.g., `TTL * 1.5`) for high-confidence entries to prevent premature eviction.

**Confidence Score: 8/10**

---

### Action Items
```json
[
  {
    "task": "Analyze bag/semantic_cache.py to identify where to inject the TTL logic.",
    "priority": "high"
  },
  {
    "task": "Create a helper function in bag/semantic_cache.py to calculate TTL based on knowledge_log.json.",
    "priority": "high"
  },
  {
    "task": "Update check_cache to perform the TTL validation before returning a hit.",
    "priority": "medium"
  }
]
```