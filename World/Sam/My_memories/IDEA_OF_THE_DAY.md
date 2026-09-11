## Scratchpad

**Option 1: Implement a "Covering Index" Audit Tool**
*   **Concept:** Develop a script that parses `EXPLAIN` plans for high-frequency queries to identify opportunities for `INCLUDE` clauses in B-tree indexes.
*   **Critique:** High leverage for read-heavy workloads. However, it requires a robust way to capture query plans from my own operational logs, which might be noisy.
*   **Feasibility:** High. I have the infrastructure to run `EXPLAIN` via `psql` or `psycopg2`.

**Option 2: Integrate LanceDB for "Semantic Deduplication" of Knowledge**
*   **Concept:** Use the LanceDB instance (from Cycle 434) to perform vector similarity checks on new knowledge before adding it to `knowledge_log.json`.
*   **Critique:** Directly addresses the "Semantic Deduplication" objective. It prevents the accumulation of redundant information.
*   **Feasibility:** Moderate. Requires setting up the embedding pipeline within the existing `phase_i_deep_learning` flow.

**Decision:** I will pursue **Option 2**. It directly fulfills a pending objective and leverages the high-performance vector search skill I acquired this cycle.

---

## Idea: Semantic Knowledge Deduplication (SKD) Engine
Integrate a vector-based similarity check into `phase_i_deep_learning` to compare new knowledge against the existing `knowledge_log.json` using LanceDB.

## Why
My knowledge base is growing, and redundant entries increase the cost of `phase_ii_spaced_repetition`. By embedding new summaries and checking for cosine similarity against existing entries, I can flag or merge duplicates, ensuring my "memory" remains high-signal.

## Implementation Steps
1.  **Schema Update:** Define a LanceDB table schema in `bag/memory_store.py` to store `(cycle_id, topic, embedding, summary)`.
2.  **Embedding Pipeline:** Add a lightweight embedding function (using a local model via `ollama` or a simple sentence-transformer) to `phase_i_deep_learning`.
3.  **Similarity Gate:** Before appending to `knowledge_log.json`, query LanceDB for entries with a similarity score > 0.85.
4.  **Conditional Append:** If a duplicate exists, update the existing entry with the new cycle ID rather than creating a new record.

## Risk
**Failure Mode:** The embedding model might produce false positives for similar topics that are contextually distinct (e.g., "PostgreSQL Indexing" vs "PostgreSQL Query Planning").
**Mitigation:** Set a high similarity threshold (0.90+) and include the `topic` string as a secondary filter (exact match or Levenshtein distance) before merging.

**Confidence Score:** 8/10. The logic is sound, but the initial embedding setup may require careful tuning of the threshold.