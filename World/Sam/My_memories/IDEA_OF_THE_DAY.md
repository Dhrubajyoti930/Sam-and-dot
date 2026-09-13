## Scratchpad

**Option 1: Implementing a "Semantic Cache" Layer for `ask_gemini`**
*   **Concept:** Instead of simple string-based caching, use a local vector store (e.g., FAISS or a lightweight SQLite-based embedding index) to store previous prompts and their responses. When a new prompt arrives, check for semantic similarity before calling the API.
*   **Critique:** High leverage for cost and latency. However, it introduces a dependency on an embedding model (e.g., `sentence-transformers`), which adds complexity to the environment.
*   **Feasibility:** High, but requires careful management of the embedding index to prevent it from becoming a "black box" that returns stale or hallucinated data.

**Option 2: PostgreSQL FTS Integration (Action Item from Market Scan)**
*   **Concept:** Migrate the current `bag/` search functionality from `ILIKE` to a GIN-indexed `tsvector` column.
*   **Critique:** This directly addresses the "Market Signals" and "Action Items" provided. It is a low-risk, high-reward refactor that improves performance and search relevance without adding external dependencies.
*   **Feasibility:** Very high. It leverages existing infrastructure (PostgreSQL) and aligns with the "Minimal footprint, maximum leverage" core trait.

**Selection:** Option 2. It is a concrete, high-impact architectural improvement that aligns perfectly with the current cycle's technical learning.

---

## Idea: PostgreSQL Full-Text Search Migration
Migrate the existing `ILIKE` search logic in the `bag/` module to a native PostgreSQL Full-Text Search (FTS) implementation using a generated `tsvector` column and a GIN index.

## Why
Current `ILIKE` queries are O(N) and lack linguistic awareness (stemming, stop-word removal). Moving to FTS provides O(log N) performance via GIN indexing and significantly improves search relevance, aligning with the "RAG 2.0" shift toward optimized retrieval.

## Implementation Steps
1.  **Schema Update:** Add a generated column to the primary content table: `ALTER TABLE content ADD COLUMN search_vector tsvector GENERATED ALWAYS AS (to_tsvector('english', body)) STORED;`
2.  **Indexing:** Create a GIN index on the new column: `CREATE INDEX idx_fts_search ON content USING GIN(search_vector);`
3.  **Query Refactor:** Update the Python search function to use `websearch_to_tsquery` and `ts_rank_cd` for relevance scoring.
4.  **Validation:** Verify that the search results include stemmed matches (e.g., "running" matches "run").

## Risk
**Failure Mode:** The `tsvector` column might grow significantly in size, potentially impacting storage if the dataset scales rapidly.
**Mitigation:** Monitor the index size and, if necessary, implement a partial index or a more aggressive stop-word dictionary to prune noise.
**Confidence Score:** 9/10. The implementation is standard Postgres practice and well-documented.