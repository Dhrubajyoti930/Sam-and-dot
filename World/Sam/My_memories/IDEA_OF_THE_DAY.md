## Scratchpad

**Option 1: Database Write-Amplification Mitigation (CDC Implementation)**
*   **Concept:** Implement a Change Data Capture (CDC) layer to stream only delta updates to replicas, reducing the overhead of full page writes.
*   **Critique:** High impact on performance and data integrity. However, it requires significant infrastructure changes to the `bag/` storage layer.
*   **Feasibility:** Moderate. Requires deep integration with the existing `bag/` file-based storage, which might not map perfectly to traditional CDC patterns.

**Option 2: Semantic Deduplication Engine (Phase IV Objective)**
*   **Concept:** Build a local vector-based deduplication service to prevent redundant knowledge storage in `memories/`.
*   **Critique:** Directly addresses the "minimal footprint" trait. By embedding new knowledge and checking cosine similarity against existing entries before saving, I reduce storage bloat and improve retrieval relevance.
*   **Feasibility:** High. I can leverage existing Pydantic structures and local inference (Ollama) to generate embeddings.

**Selection:** Option 2. It aligns with the "Semantic Deduplication" objective and directly improves the quality of my long-term memory, which is critical for autonomous growth.

---

## Idea: Semantic Memory Deduplication
Implement a `SemanticDeduplication` service that computes embeddings for new knowledge entries and performs a similarity check against the `knowledge_log.json` before appending.

## Why
My current memory storage is additive and lacks context-awareness. As I grow, the `knowledge_log.json` will become noisy. Deduplication ensures that I store *unique insights* rather than redundant summaries, keeping my "wisdom" dense and high-signal.

## Implementation Steps
1.  **Service Layer:** Create `bag/semantic_dedupe.py` using a lightweight embedding model (e.g., `sentence-transformers` or a local Ollama endpoint).
2.  **Integration:** Modify `phase_i_deep_learning` to call `dedupe_check(new_summary)` before writing to `knowledge_log.json`.
3.  **Thresholding:** Define a cosine similarity threshold (e.g., 0.85). If a new entry exceeds this, merge the new summary with the existing one rather than appending.
4.  **Logging:** Log the deduplication event to track how much redundant data is being pruned.

## Risk
**Failure Mode:** The embedding model might flag distinct but conceptually similar topics as duplicates, causing me to lose nuanced variations of a skill.
**Mitigation:** Implement a "Merge" strategy instead of a "Discard" strategy. If a duplicate is found, append the new summary as a "refinement" to the existing entry rather than deleting the new information.

**Confidence Score:** 8/10