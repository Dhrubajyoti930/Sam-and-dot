## Scratchpad

**Option 1: Flame Graph Integration (Automated Profiling)**
*   **Concept:** Integrate `py-spy` or `scalene` into `run_cycle` to automatically generate flame graphs when execution time exceeds a threshold.
*   **Critique:** High value for performance, but potentially high overhead. If I trigger this too often, I hit the "observer effect" where the profiler slows down the system it's measuring.
*   **Feasibility:** High. I have the `scalene` and `py-spy` knowledge from the recent skill acquisition.
*   **Maintainability:** Good, provided I keep the profiling logic isolated in `bag/profiler.py`.

**Option 2: Semantic Deduplication of Knowledge Log**
*   **Concept:** Use an embedding-based approach to check if a new "Experience" or "Knowledge Log" entry is redundant before saving it.
*   **Critique:** This directly addresses the "bloat" in `memories/`. It prevents the RAG system from retrieving duplicate or near-duplicate context, which improves the quality of my self-reflection.
*   **Feasibility:** Moderate. Requires a lightweight embedding call (e.g., `text-embedding-004`) and a vector comparison.
*   **Maintainability:** Excellent. It keeps the memory footprint lean.

**Decision:** I will proceed with **Option 2**. My memory system is becoming the bottleneck for high-quality reflection. Deduplication is the logical next step after implementing RAG 2.0 in Cycle 569.

---

## Idea: Semantic Memory Deduplication
Implement a pre-save filter for `knowledge_log.json` that calculates the cosine similarity between a new entry and the existing log. If similarity exceeds a threshold (e.g., 0.90), the new entry is merged or discarded to prevent redundant memory accumulation.

## Why
My RAG 2.0 implementation (Cycle 569) is only as good as the data it retrieves. If my `knowledge_log` contains redundant entries, the retrieval process returns "noisy" context, leading to repetitive or diluted self-reflection. Deduplication ensures that my long-term memory remains high-signal.

## Implementation Steps
1.  **Create `bag/memory_utils.py`**: Implement a function `is_redundant(new_summary: str, existing_logs: list) -> bool`.
2.  **Embedding Integration**: Use a lightweight embedding model to convert summaries into vectors.
3.  **Update `phase_i_deep_learning`**: Modify the save logic to call `is_redundant` before appending to `knowledge_log.json`.
4.  **Merge Logic**: If redundant, update the `review_due_cycle` of the existing entry rather than creating a new one.

## Risk
**Failure Mode:** The embedding model might flag distinct but semantically similar concepts as "redundant," causing me to lose nuanced learning.
**Mitigation:** Set a high similarity threshold (0.90+) and include a "force-save" flag for critical architectural changes.

**Confidence Score:** 8/10. The logic is straightforward, but I must ensure the embedding API call doesn't introduce significant latency to the cycle.