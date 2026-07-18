## Scratchpad

**Option 1: Implement SPLADE-based Sparse Expansion**
*   **Concept:** Integrate a lightweight SPLADE model to generate sparse expansion vectors for the existing RAG pipeline.
*   **Critique:** High impact on recall, especially for domain-specific terminology. However, it introduces a dependency on a transformer model for index-time expansion, increasing latency during ingestion.
*   **Feasibility:** High, given existing infrastructure for vector operations.
*   **Maintainability:** Moderate; requires managing an additional model artifact.

**Option 2: Reciprocal Rank Fusion (RRF) Module**
*   **Concept:** Build a dedicated RRF utility to merge results from the current dense vector search and a new BM25 sparse search.
*   **Critique:** This is a "clean" architectural win. It doesn't require heavy model inference at query time (unlike SPLADE) and directly addresses the "vocabulary mismatch" problem identified in the market scan.
*   **Feasibility:** Very high. It is purely algorithmic and fits perfectly into the existing retrieval flow.
*   **Maintainability:** High; the logic is deterministic and easy to unit test.

**Decision:** I will proceed with **Option 2 (RRF Module)**. It provides the most immediate, high-leverage improvement to retrieval quality without the overhead of maintaining a secondary transformer model for expansion.

---

## Idea: Hybrid Retrieval via Reciprocal Rank Fusion (RRF)

## Why
My current retrieval relies heavily on dense embeddings, which struggle with exact keyword matching (e.g., specific error codes or unique identifiers). Integrating a BM25 sparse index and merging it with dense results via RRF will significantly improve precision for technical queries while maintaining semantic depth.

## Implementation Steps
1.  **Index Setup:** Add a BM25 index (using `rank_bm25` or similar lightweight library) to the existing `workshop_bench/retrieval.py`.
2.  **RRF Logic:** Implement the RRF formula: $RRF(d) = \sum_{r \in R} \frac{1}{k + rank(d, r)}$, where $k=60$ is the standard constant.
3.  **Integration:** Update the retrieval entry point to query both indices, normalize ranks, and return the fused result set.
4.  **Verification:** Add a test case in `bag/tests.py` to ensure that a query containing a rare keyword ranks higher after fusion than with dense search alone.

## Risk
**Failure Mode:** The BM25 index might return empty results for queries with no overlapping tokens, potentially skewing the RRF calculation if not handled.
**Mitigation:** Implement a fallback mechanism where if the sparse index returns zero results, the system defaults to the dense search score, or vice-versa, ensuring the pipeline never returns an empty set.

**Confidence Score:** 9/10