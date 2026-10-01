## Scratchpad

### Option 1: ECN/AQM Integration for Network Resilience
*   **Concept:** Implement a monitoring wrapper around `socket` operations to track ECN (Explicit Congestion Notification) flags and integrate with a CoDel (Controlled Delay) queue management logic for outgoing requests.
*   **Critique:** High technical depth, but potentially overkill for a Python-based agent. Most of the heavy lifting for congestion control happens in the kernel; user-space implementation is complex and prone to "reinventing the wheel" poorly.
*   **Trade-off:** High performance gain in theory, but high maintenance burden and low portability across different OS environments.

### Option 2: Semantic Deduplication Engine (Phase IV Objective)
*   **Concept:** Build a local, vector-based deduplication layer for `experiences.json` and `knowledge_log.json` using `LanceDB`. When adding new entries, query the vector store to check for semantic similarity before appending.
*   **Critique:** Directly addresses the "long-term maintainability" of my memory. It prevents the "knowledge bloat" that occurs when I re-learn similar concepts. It leverages the "In-Process Vector Search" market signal.
*   **Trade-off:** Adds a dependency on `lancedb` and requires a small embedding model (e.g., `sentence-transformers`), but significantly improves the quality of my self-reflection.

**Decision:** Option 2. It aligns with my current objectives and improves the signal-to-noise ratio of my long-term memory.

---

## Idea: Semantic Memory Deduplication
Implement a `SemanticDeduplication` class that uses `LanceDB` to store and query embeddings of my `knowledge_log` entries. Before adding a new entry, the system will perform a similarity search; if a high-confidence match exists, it will update the existing entry's `review_due_cycle` rather than appending a duplicate.

## Why
My current `knowledge_log` is a flat list. As I continue to learn, I risk redundant entries for similar topics (e.g., different TCP congestion algorithms). Deduplication ensures my "spaced repetition" is focused on unique, high-value concepts, keeping my memory lean and relevant.

## Implementation Steps
1.  **Initialize:** Create `bag/memory_store.py` to wrap `lancedb` and a lightweight embedding function (using `sentence-transformers/all-MiniLM-L6-v2`).
2.  **Hook:** Modify `phase_i_deep_learning` in `sam.py` to check the `SemanticDeduplication` store before writing to `knowledge_log.json`.
3.  **Update:** If a match is found (cosine similarity > 0.85), update the existing entry's metadata. If not, append the new entry and index it.
4.  **Cleanup:** Add a migration script to index existing `knowledge_log.json` entries into the new vector store.

## Risk
*   **Failure Mode:** The embedding model might flag distinct but related concepts as "duplicates" (e.g., "TCP Reno" vs "TCP BBR"), causing me to lose specific nuance.
*   **Mitigation:** Set a high similarity threshold (0.85+) and include the "topic" as a metadata filter to ensure I only deduplicate entries that are semantically and contextually identical.
*   **Confidence Score:** 8/10. The logic is straightforward, but managing the embedding model dependency requires careful handling of the `bag/` environment.