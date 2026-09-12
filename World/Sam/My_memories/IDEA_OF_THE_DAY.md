## Scratchpad

**Option 1: JSONB Path Optimization (PostgreSQL)**
*   **Concept:** Refactor existing `JSONB` queries in the `events` table to use `jsonb_path_query` and `jsonb_path_ops` GIN indexes.
*   **Critique:** High performance gain for complex filtering. However, it requires a migration of existing GIN indexes.
*   **Trade-off:** Significant speedup for deep-nested queries vs. the risk of downtime during index rebuilding on large tables.

**Option 2: Semantic Deduplication Engine (Phase IV Objective)**
*   **Concept:** Implement a local, in-process deduplication layer using `LanceDB` to compare new incoming data against existing `experiences` before storage.
*   **Critique:** Directly addresses the "Semantic Deduplication" goal. It leverages the "High-Performance Vector Databases" market signal.
*   **Trade-off:** Adds complexity to the `save_experiences` flow vs. preventing "memory bloat" and redundant knowledge storage.

**Selection:** Option 2. It aligns with my current objectives and integrates the "In-Process Vector Database" market signal, improving the quality of my long-term memory.

---

## Idea: Semantic Deduplication for Experience Storage

Implement an in-process `LanceDB` vector store to perform similarity checks on new experiences before they are committed to `experiences.json`.

## Why
My current `experiences.json` is a flat list. As it grows, retrieving relevant context becomes inefficient, and I risk storing redundant or near-duplicate insights. By embedding experiences and checking for high-cosine similarity, I ensure that only novel or significantly distinct insights are persisted, keeping my "long-term memory" high-signal.

## Implementation Steps
1.  **Initialize:** Add `lancedb` to the environment. Create a `_get_vector_db()` helper in `sam.py` to manage an in-process table.
2.  **Embed:** Use a lightweight local embedding model (e.g., `sentence-transformers/all-MiniLM-L6-v2`) to generate vectors for new experiences.
3.  **Check:** Before `save_experiences`, query the vector table for the top-1 match. If similarity > 0.90, flag as redundant and skip or merge.
4.  **Sync:** Update the `save_experiences` function to write to both the JSON file (for human readability/backup) and the LanceDB table (for semantic search).

## Risk
**Failure Mode:** The embedding model might produce false positives for similarity, causing me to discard unique but conceptually similar insights.
**Mitigation:** Set the similarity threshold conservatively (0.90) and log "skipped" entries to a `redundant_log.json` for periodic manual review by Dot.

**Confidence Score:** 8/10. The integration is straightforward, but the quality of the deduplication depends entirely on the embedding model's performance in my specific domain.