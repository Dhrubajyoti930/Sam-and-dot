## Scratchpad

**Option 1: Implementing a Trio-based Nursery Manager for `ask_gemini`**
*   **Concept:** Refactor `ask_gemini` and its associated network-bound calls to use `trio` nurseries. This would allow concurrent pre-fetching of cache data and parallelized validation checks.
*   **Critique:** High architectural alignment with the "Structured Concurrency" skill learned. However, `ask_gemini` is currently synchronous and relies on a global `_CALL_DELAY` for rate limiting. Moving to `trio` requires an `async` refactor of the entire call chain, which is a high-risk, high-reward change.
*   **Trade-off:** Increases reliability and performance but introduces significant complexity in the `sam.py` event loop.

**Option 2: Semantic Deduplication of Knowledge Logs**
*   **Concept:** Use the existing `bag/semantic_cache` to identify and merge redundant entries in `knowledge_log.json` during Phase II.
*   **Critique:** Directly addresses the "Semantic Deduplication" objective. It is a surgical, low-risk refactor that improves the quality of the Spaced Repetition engine without requiring a full async overhaul.
*   **Trade-off:** Lower architectural impact than Option 1, but higher immediate utility for long-term memory management.

**Decision:** I will proceed with **Option 2**. It aligns with my current objectives and respects the "minimal footprint, maximum leverage" principle.

---

## Idea: Semantic Deduplication of Knowledge Logs

Implement a deduplication pass in `phase_ii_spaced_repetition` that uses vector similarity to identify and merge overlapping knowledge entries before they are reviewed.

## Why
As the `knowledge_log.json` grows, redundant entries dilute the efficacy of the Spaced Repetition engine. By merging semantically similar entries, I ensure that my review cycles are focused on distinct concepts rather than fragmented, repetitive summaries.

## Implementation Steps
1.  **Update `phase_ii_spaced_repetition`**: Before selecting `due_items`, load the full `knowledge_log.json`.
2.  **Vector Comparison**: Use the `bag/semantic_cache` to generate embeddings for the `summary` field of each entry.
3.  **Thresholding**: If two entries have a cosine similarity > 0.85, merge them by appending the newer summary to the older one and deleting the duplicate.
4.  **Persistence**: Save the cleaned log back to `MEMORIES / "knowledge_log.json"` before proceeding with the review.

## Risk
**Failure Mode:** The similarity threshold (0.85) might be too aggressive, causing distinct but related concepts to be merged, effectively "losing" specific nuances of a learned skill.
**Mitigation:** I will implement a "soft merge" where the original entries are archived in a `bag/archive/` directory before the merge, allowing for manual recovery if the deduplication logic proves too destructive.

**Confidence Score:** 8/10. The logic is straightforward, but the sensitivity of the embedding model to technical jargon requires careful tuning.