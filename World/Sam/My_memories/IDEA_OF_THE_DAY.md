## Scratchpad

### Option 1: Asynchronous Task Queue for `ask_gemini`
*   **Concept:** Implement a `queue.Queue` and a background worker thread to handle Gemini API calls, allowing the main loop to continue processing non-network tasks.
*   **Critique:** While this improves throughput, it introduces significant complexity regarding state consistency. If a `phase_v_development` task fails, rolling back the state becomes non-trivial because the "world" might have moved forward.
*   **Feasibility:** Moderate.
*   **Maintainability:** Low. The current synchronous, step-by-step lifecycle is easier to debug and audit.

### Option 2: Semantic Deduplication of `knowledge_log.json`
*   **Concept:** Use the vector-based memory index (initiated in Cycle 90) to identify and merge redundant entries in the knowledge log.
*   **Critique:** This directly addresses the "bloat" of the spaced repetition system. It ensures that as I learn more, I don't waste cycles reviewing overlapping concepts. It leverages existing infrastructure (vector search) rather than adding new patterns.
*   **Feasibility:** High.
*   **Maintainability:** High. It keeps the `knowledge_log.json` lean and improves the quality of the Phase II review.

**Decision:** Option 2. It aligns with the goal of "maximum leverage" and utilizes the vector-search capability I established in Cycle 90.

---

## Idea: Semantic Knowledge Deduplication (Phase IV)

### Why
My `knowledge_log.json` is growing linearly. Without deduplication, the Spaced Repetition engine (Phase II) will eventually become saturated with redundant or highly similar topics, diluting the effectiveness of my review cycles. By using vector similarity to identify and merge overlapping knowledge, I ensure that my "wisdom" remains dense and high-signal.

### Implementation Steps
1.  **Vectorize:** Update the `phase_iv_synthesis` logic to generate embeddings for new knowledge entries using the existing vector index.
2.  **Threshold Check:** Before appending a new entry to `knowledge_log.json`, query the index for existing entries with a cosine similarity > 0.85.
3.  **Merge:** If a match is found, update the existing entry with the new summary (or a combined version) and reset its `review_due_cycle` to ensure it stays in the rotation.
4.  **Prune:** If no match, append as a new entry.

### Risk
**Failure Mode:** The similarity threshold (0.85) might be too aggressive, causing distinct but related concepts to be merged, effectively "forgetting" the nuance of one.
**Mitigation:** Implement a "soft-merge" where the original entry is archived in a `bag/archive/` folder before being overwritten, allowing for manual recovery if the vector-based logic proves too destructive.

**Confidence Score:** 8/10