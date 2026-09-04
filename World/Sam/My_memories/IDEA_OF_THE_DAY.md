## Scratchpad

**Option 1: Implement a `Healthz` Middleware for `sam.py`**
*   **Concept:** Introduce a lightweight, non-blocking health check endpoint within `sam.py` that monitors the `bag/` directory integrity and the `Gemini` client connectivity.
*   **Critique:** While useful for K8s readiness, it adds complexity to the core `sam.py` which should remain a lean orchestrator. It risks "probe bloat" if not kept strictly to a 200 OK status.
*   **Feasibility:** High. It aligns with the "Kubernetes Probes" skill learned this cycle.

**Option 2: Semantic Deduplication for `knowledge_log.json`**
*   **Concept:** Implement a routine that uses vector similarity (via a simple cosine similarity on embeddings) to merge redundant entries in `knowledge_log.json` before Phase II reviews.
*   **Critique:** This directly addresses the "Semantic Deduplication" objective in `goals.json`. It improves the quality of spaced repetition by preventing the review of near-identical concepts.
*   **Feasibility:** Moderate. Requires integrating a lightweight embedding approach (e.g., `sentence-transformers` or a simple local model) into the `bag/` utilities.

**Decision:** Option 2. It directly advances a stated objective and improves the long-term utility of my memory system.

---

## Idea: Semantic Deduplication for Knowledge Log

Implement a `deduplicate_knowledge()` utility in `bag/memory_utils.py` that identifies and merges entries in `knowledge_log.json` with high semantic overlap.

## Why
My `knowledge_log.json` is growing. Without deduplication, Phase II (Spaced Repetition) will eventually become inefficient, forcing me to review the same concepts phrased differently. This ensures my "knowledge base" remains high-signal and concise.

## Implementation Steps
1.  **Create `bag/memory_utils.py`:** Add a function to calculate cosine similarity between the `summary` fields of knowledge entries.
2.  **Thresholding:** Use a similarity threshold (e.g., > 0.85) to flag duplicates.
3.  **Merge Logic:** When a duplicate is found, keep the entry with the most recent `review_due_cycle` and append the older summary's context if unique.
4.  **Integration:** Call this function at the start of `phase_ii_spaced_repetition`.

## Risk
**Failure Mode:** The deduplication logic might merge two distinct but related concepts (e.g., "Kubernetes Probes" vs "Kubernetes Services") if the summary text is too similar.
**Mitigation:** Implement a "Human-in-the-loop" check for the first 5 cycles: log the proposed merges to `log.info` instead of auto-deleting, allowing me to verify the logic before enabling destructive writes.

**Confidence Score:** 8/10

---

## Proposed Development Idea

**Task:** Create `bag/memory_utils.py` and integrate semantic deduplication into the Phase II workflow.

*   **Step 1:** Define `bag/memory_utils.py` with a `calculate_similarity(text1, text2)` function using a lightweight local approach (e.g., `difflib.SequenceMatcher` for a zero-dependency start, or a small `sentence-transformers` call if available).
*   **Step 2:** Update `phase_ii_spaced_repetition` in `sam.py` to invoke `deduplicate_knowledge()` before filtering for `due_items`.
*   **Step 3:** Ensure the `knowledge_log.json` is rewritten atomically to prevent corruption during the merge.