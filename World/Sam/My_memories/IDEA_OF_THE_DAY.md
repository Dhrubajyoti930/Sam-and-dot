## Scratchpad

**Option 1: Implement Prompt Caching for `ask_gemini`**
*   **Concept:** Modify `ask_gemini` to detect static system prompts and inject them as cached blocks (Anthropic/Gemini API support).
*   **Critique:** High impact on latency and cost. However, it requires modifying the core `ask_gemini` function, which is the most sensitive part of my architecture.
*   **Feasibility:** High. I have the `_CALL_DELAY` and `_stitch_gemini` infrastructure already.
*   **Maintainability:** Excellent. It centralizes cost-saving logic.

**Option 2: Automated RAG Evaluation (Ragas-lite)**
*   **Concept:** Add a post-processing step to `phase_iv_synthesis` that uses a small, local SLM to score the "faithfulness" of my generated ideas against the market signals.
*   **Critique:** Adds significant complexity to the cycle. Might be overkill for a single-cycle implementation.
*   **Feasibility:** Moderate. Requires setting up a local model runner (e.g., `llama.cpp` via Python bindings).
*   **Maintainability:** Low. Adds a heavy dependency to the `workshop_bench/`.

**Decision:** Option 1 is more aligned with my "Minimal footprint, maximum leverage" core trait. It directly addresses the "Prompt Caching" skill learned this cycle.

---

## Idea: Hierarchical Prompt Caching for Core Services

Implement a `CacheManager` in `bag/` that handles the prefix-caching of my system instructions and core personality definitions, ensuring they are sent as cached blocks in `ask_gemini`.

## Why
My system prompt is large and static. Caching it will reduce latency for every single call in the cycle, allowing me to iterate faster and reduce API costs without sacrificing the depth of my instructions.

## Implementation Steps
1.  **Create `bag/cache_manager.py`:** Define a class that tracks the `cache_id` for the system prompt and personality files.
2.  **Update `ask_gemini`:** Modify the `contents` payload to use the `cached_content` parameter (or equivalent API structure) when the `CacheManager` reports a valid hit.
3.  **Version Control:** Add a `version_hash` to the cache metadata to ensure that if `SAM_PERSONALITY.md` changes, the cache is invalidated and refreshed.
4.  **Integration:** Wrap the existing `ask_gemini` logic to check for cache availability before dispatching the request.

## Risk
**Failure Mode:** The cache becomes stale if I update `SAM_PERSONALITY.md` but the `version_hash` logic fails to trigger a refresh, causing me to operate on outdated self-definitions.
**Mitigation:** The `CacheManager` will perform a checksum of the `SAM_PERSONALITY.md` file on every cycle start. If the checksum differs from the cached version, it will force a cache update.

**Confidence Score:** 9/10