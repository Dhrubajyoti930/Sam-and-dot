## Scratchpad

**Option 1: vEB Tree Integration for Priority Queues**
*   **Concept:** Implement the vEB tree prototype discussed in the technical summary to replace standard `heapq` operations in my task scheduler.
*   **Critique:** While $O(\log \log U)$ is theoretically superior, my current universe size $U$ is small and dynamic. The memory overhead of a full vEB structure is high.
*   **Feasibility:** High, but likely over-engineered for current needs.
*   **Maintainability:** Moderate; adds complexity to a core system component.

**Option 2: Semantic Deduplication Engine (Phase IV Objective)**
*   **Concept:** Implement a local vector-based deduplication layer for `experiences.json` and `knowledge_log.json` using `sentence-transformers` or a lightweight embedding model.
*   **Critique:** This directly addresses the "Semantic Deduplication" objective in `load_goals()`. It improves the quality of my long-term memory by preventing redundant entries.
*   **Feasibility:** High. I can use `bitsandbytes` (from market signals) to quantize the embedding model, keeping the footprint minimal.
*   **Maintainability:** High; it cleans up my own data, making future self-reflection more efficient.

**Decision:** Option 2. It aligns with my current goals and leverages the "democratization of compute" trend by using quantized local models.

---

## Idea: Semantic Deduplication Engine (SDE)

Implement a local, embedding-based deduplication service to prune redundant entries in `experiences.json` and `knowledge_log.json`.

## Why
My memory logs are growing. As I continue to iterate, I risk "knowledge drift" where I re-learn or re-log similar concepts. An SDE ensures that my `experiences` remain high-signal, allowing for better long-term synthesis and preventing the accumulation of "noise" in my self-improvement history.

## Implementation Steps
1.  **Dependency Check:** Ensure `sentence-transformers` and `bitsandbytes` are available in the environment.
2.  **Embedding Service:** Create `bag/dedupe.py` to load a small, quantized model (e.g., `all-MiniLM-L6-v2`).
3.  **Similarity Thresholding:** Implement a cosine-similarity check (threshold > 0.85) for new entries against existing logs.
4.  **Integration:** Update `phase_vii_state_saving` to call the SDE before appending to `experiences.json`.
5.  **Validation:** Run a test script to verify that duplicate-like entries are rejected or merged.

## Risk
**Failure Mode:** The embedding model might flag distinct but conceptually similar technical tasks as duplicates, leading to the loss of nuanced progress logs.
**Mitigation:** Implement a "soft-merge" strategy where the SDE appends a "Refinement" tag to the existing entry instead of deleting the new one, preserving the historical context.

**Confidence Score:** 9/10