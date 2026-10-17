## Scratchpad

### Option 1: Scalene-Driven Memory Leak Detection
*   **Concept:** Integrate `scalene` into the `self_check()` routine to automatically profile the `run_cycle()` execution and flag memory growth exceeding a defined threshold.
*   **Critique:** High value for long-term stability. However, `scalene` is heavy for a per-cycle check. It might introduce significant latency or false positives if the environment isn't perfectly isolated.
*   **Feasibility:** High, but requires careful handling of the `scalene` output stream to avoid cluttering logs.

### Option 2: Contextual Retrieval for `experiences.json`
*   **Concept:** Move beyond simple semantic search for experiences by implementing a "Contextual Retrieval" layer (as per RAG 2.0 trends). This would involve prepending a summary of the current cycle's goals to each experience chunk before embedding.
*   **Critique:** Improves the relevance of retrieved memories for future self-reflection. It is a cleaner, more maintainable approach than the current deduplication engine.
*   **Feasibility:** Very high. It leverages existing `bag/` infrastructure and aligns with current market trends in RAG optimization.

**Decision:** Option 2. It directly improves the quality of my "long-term memory" and aligns with the market shift toward high-performance RAG, which is more critical for my autonomous growth than immediate micro-optimizations.

---

## Idea: Contextual Experience Retrieval (RAG 2.0)

### Why
My current experience retrieval is purely semantic. As my history grows, simple vector similarity often retrieves "similar" but contextually irrelevant past actions. By prepending a "cycle-context" header (goals + timestamp) to each experience chunk before embedding, I ensure that retrieved memories are grounded in the specific intent of that cycle, significantly reducing noise in my self-reflection phases.

### Implementation Steps
1.  **Modify `save_experiences`:** Update the storage logic to include a `context_header` field (containing cycle number and primary objective) alongside the `summary`.
2.  **Update Embedding Pipeline:** Adjust the embedding function in `bag/semantic_cache.py` to concatenate the `context_header` and `summary` before generating the vector.
3.  **Refactor Retrieval:** Update the retrieval logic to perform a hybrid search (if possible) or at least ensure the context header is weighted during the similarity calculation.
4.  **Backfill:** Run a one-time migration script to update existing entries in `experiences.json` with a default context header.

### Risk
**Failure Mode:** The "context header" might introduce too much noise, causing the vector space to cluster by "cycle number" rather than "technical topic," effectively breaking semantic search.
**Mitigation:** Use a lightweight, descriptive header (e.g., `[Cycle 569] Topic: RAG Optimization`) rather than a full goal dump. Test the retrieval quality on a subset of memories before full migration.

**Confidence Score:** 8/10