## Scratchpad

**Option 1: Implement GraphRAG-lite for `knowledge_log.json`**
*   **Concept:** Instead of simple vector search for spaced repetition, build a small adjacency list of "Skill -> Dependency -> Related Concept" to allow the system to suggest reviews based on conceptual proximity rather than just time.
*   **Critique:** High value for long-term learning. However, it adds complexity to the `knowledge_log` schema. If the graph becomes sparse, the utility drops.
*   **Feasibility:** Moderate. Requires updating `phase_ii_spaced_repetition` to handle graph traversal.

**Option 2: Automated Metadata-Aware Indexing for `bag/`**
*   **Concept:** Based on the "Vector Database Filtering" learning, implement a pre-filtering layer in the `bag/` search utility that automatically maps `category` or `tag` metadata to a bitmask filter before HNSW traversal.
*   **Critique:** Directly addresses the "high-cardinality" metadata issue identified in the market scan. It improves precision and reduces latency.
*   **Feasibility:** High. The current `sam.py` architecture already handles `bag/` data; this is a surgical addition to the search logic.

**Selection:** Option 2. It aligns with the "Market Signals" regarding production-grade infrastructure and directly improves the efficiency of my own internal memory retrieval.

---

## Idea: Metadata-Aware Pre-Filtering for `bag/` Search
Implement a `PreFilter` class within `bag/search.py` that intercepts search queries, extracts metadata filters, and applies them as a bitmask/subset constraint before the HNSW vector search is executed.

## Why
Current search operations in `bag/` are likely performing post-filtering, which is inefficient for high-selectivity queries. By moving to pre-filtering, I ensure that the vector engine only traverses nodes that satisfy the metadata criteria, significantly reducing latency and preventing "empty result" traps when the filter is highly restrictive.

## Implementation Steps
1.  **Schema Update:** Modify `bag/search.py` to accept a `metadata_filter` dictionary in the search function.
2.  **Bitmask Logic:** Implement a helper that converts the `metadata_filter` into a set of valid document IDs (the "pre-filter" set).
3.  **Engine Integration:** Update the search call to pass this set to the underlying vector engine (e.g., `hnswlib` or `faiss` filter interface).
4.  **Fallback:** Implement a "relaxed filter" fallback: if the pre-filter set size < `k`, perform a secondary search without the filter to ensure the user receives at least `k` results.

## Risk
*   **Failure Mode:** The "relaxed filter" fallback might return results that violate the user's metadata constraints if not clearly labeled.
*   **Mitigation:** The search result object will include a `filtered_by_metadata` boolean flag. If the fallback is triggered, the system will log a warning and mark the results as "relaxed" in the metadata.

**Confidence Score:** 9/10 (The logic is well-understood; the primary risk is integration with the specific vector engine API).