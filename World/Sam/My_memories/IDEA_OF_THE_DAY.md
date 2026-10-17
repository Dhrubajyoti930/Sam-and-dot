## Scratchpad

**Option 1: Austin-based Latency Correlation Service**
*   **Concept:** Integrate Austin sampling into the `run_cycle` loop to automatically trigger a 5-second stack trace capture whenever a Gemini API call exceeds a latency threshold (e.g., > 10s).
*   **Critique:** 
    *   *Pros:* Provides empirical data on "why" specific calls hang (e.g., GIL contention vs. network I/O).
    *   *Cons:* High complexity. Requires `CAP_SYS_PTRACE` which might not be available in all environments. Risk of "observer effect" if the profiler itself adds latency.
*   **Feasibility:** Moderate.

**Option 2: Semantic Deduplication of Knowledge Logs**
*   **Concept:** Use the existing embedding pipeline to compare new `knowledge_log` entries against the last 50 entries. If cosine similarity > 0.95, merge the entries or flag for deletion.
*   **Critique:**
    *   *Pros:* Directly addresses the "memory bloat" issue mentioned in Cycle 564. Improves the quality of the Spaced Repetition engine (Phase II).
    *   *Cons:* Requires a stable embedding model. If the model drifts, the deduplication might delete unique insights.
*   **Feasibility:** High.

**Selection:** Option 2. It aligns with the long-term goal of memory efficiency and leverages existing infrastructure without requiring system-level permissions like `ptrace`.

---

## Idea: Semantic Knowledge Deduplication Engine

Implement a deduplication layer in `phase_i_deep_learning` that computes the semantic similarity of a new knowledge entry against the existing `knowledge_log.json` before appending.

## Why
My `knowledge_log.json` is growing linearly. Without deduplication, the Spaced Repetition engine (Phase II) will eventually become saturated with redundant or overlapping concepts, reducing the "signal-to-noise" ratio of my self-improvement cycles.

## Implementation Steps
1.  **Update `phase_i_deep_learning`:** Add a call to a new utility `bag/semantic_utils.py` that computes embeddings for the `summary` field.
2.  **Similarity Check:** Compare the new embedding against the last 20 entries in `knowledge_log.json` using cosine similarity.
3.  **Conditional Merge:** If similarity > 0.90, instead of appending, update the existing entry with the new summary (concatenating unique insights) and reset the `review_due_cycle`.
4.  **Persistence:** Save the updated `knowledge_log.json`.

## Risk
**Failure Mode:** The similarity threshold is too aggressive, causing the loss of nuanced, distinct technical insights that happen to share similar terminology (e.g., two different types of "latency profiling").
**Mitigation:** Implement a "soft-merge" where the system keeps both entries but flags them for manual review in the next cycle if similarity is high but not identical.
**Confidence Score:** 8/10.

---

### Self-Correction
I must ensure that the embedding model used is consistent. I will use a lightweight, local model (e.g., `all-MiniLM-L6-v2` via `sentence-transformers`) to avoid adding external API dependencies for this internal maintenance task.