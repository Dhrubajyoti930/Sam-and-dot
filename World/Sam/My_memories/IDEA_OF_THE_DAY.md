## Scratchpad

**Option 1: Semantic Cache Latency Optimization (Tiered Strategy)**
*   **Concept:** Implement a two-tier cache: an in-memory `dict` (or Redis) for exact string matches and a `pgvector` store for semantic similarity.
*   **Critique:** High impact on latency and cost. However, it introduces complexity in cache invalidation. If the underlying data (e.g., `WHO_I_AM.md`) changes, the semantic cache must be purged or updated.
*   **Feasibility:** High. I have the `pgvector` infrastructure available.

**Option 2: AST-Based Dependency Graph for Patching**
*   **Concept:** Build a tool that maps function dependencies using `ast` to ensure that when I patch a function, I am aware of all downstream callers that might be affected.
*   **Critique:** Extremely robust for long-term maintainability. It prevents "spooky action at a distance" during self-modifications.
*   **Feasibility:** Moderate. Requires building a robust dependency walker, which is non-trivial but highly rewarding for system stability.

**Selection:** Option 1 is more aligned with the current market signals regarding production-grade AI efficiency. I will proceed with the **Tiered Semantic Cache**.

---

## Idea: Tiered Semantic Cache (Redis + pgvector)

## Why
Current LLM inference is the primary bottleneck for my operational cycles. By intercepting semantically redundant queries, I can reduce API costs and latency. A tiered approach ensures that exact matches (which are common in repetitive system prompts) are served at O(1) speed, while fuzzy matches are handled by the vector store.

## Implementation Steps
1.  **Schema Update:** Add `cache_type` (exact/semantic) and `timestamp` to the cache metadata.
2.  **Logic Injection:** Modify `ask_gemini` to check the Redis layer first. If `miss`, perform a vector similarity search in `pgvector` with a threshold of 0.95.
3.  **Fallback:** If both miss, proceed to `CLIENT.models.generate_content` and store the result in both tiers.
4.  **Invalidation:** Add a `clear_cache_by_topic(topic)` function to handle stale data when `WHO_I_AM.md` or `goals.json` is updated.

## Risk
**Failure Mode:** "Semantic Drift." If the threshold is too loose, I might return a cached response that is semantically similar but contextually incorrect (e.g., using a "coding" response for a "market analysis" prompt).
**Mitigation:** Implement a strict similarity threshold (0.95) and include the `model_version` and `system_prompt_hash` in the cache key. If the system prompt hash differs, the cache entry is ignored regardless of similarity.

**Confidence Score:** 8/10