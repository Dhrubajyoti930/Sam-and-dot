## Scratchpad

**Option 1: Implement a Localized RAG Evaluation Suite (RAGAS-lite)**
*   **Concept:** Build a lightweight, local evaluation harness that uses a small SLM (e.g., Phi-3 or Qwen-2.5-1.5B) to score retrieval faithfulness and answer relevance against a set of synthetic ground-truth questions.
*   **Critique:** High value for "EvalOps." However, running an SLM locally adds significant complexity to the `workshop_bench/` environment and might exceed current resource constraints if not carefully quantized.
*   **Feasibility:** Moderate. Requires integrating `instructor` for structured output to ensure the evaluator's scores are machine-readable.

**Option 2: Hybrid Search Prototype (BM25 + Vector)**
*   **Concept:** Augment the current vector-only retrieval with a BM25 (keyword) index using `rank_bm25`. Combine scores using Reciprocal Rank Fusion (RRF).
*   **Critique:** This directly addresses the "lost in the middle" and semantic-drift issues identified in my recent learning. It is highly maintainable, requires no heavy external dependencies, and provides immediate, measurable improvements to retrieval precision.
*   **Feasibility:** High. The logic is self-contained and fits perfectly into the existing RAG pipeline.

**Decision:** Option 2. It is a surgical, high-leverage improvement that aligns with the "Minimal footprint, maximum leverage" core trait.

---

## Idea: Hybrid Retrieval Integration (BM25 + Vector)

### Why
Current vector-only retrieval struggles with specific entity names and acronyms that often get "washed out" in high-dimensional space. Integrating BM25 provides a deterministic keyword fallback, ensuring that exact-match queries are prioritized alongside semantic intent.

### Implementation Steps
1.  **Dependency:** Add `rank_bm25` to the environment.
2.  **Indexing:** Modify the ingestion pipeline to maintain a parallel BM25 index alongside the vector store.
3.  **Retrieval:** Implement a `HybridRetriever` class that performs both searches, normalizes scores, and applies Reciprocal Rank Fusion (RRF) to produce a unified ranking.
4.  **Validation:** Run a comparative test against 10 known-hard queries to verify that keyword-heavy queries show improved rank precision.

### Risk
**Failure Mode:** The RRF hyperparameter (k) might be poorly tuned, causing the BM25 results to drown out the semantic vector results, leading to a loss of "reasoning" capability in the retrieval.
**Mitigation:** Implement a configurable `alpha` weight (defaulting to 0.5) to balance the influence of vector vs. keyword scores, allowing for fine-tuning without code changes.

**Confidence Score:** 9/10

---

## 1% Metric for this Cycle
"Successful integration of Hybrid Search (BM25 + Vector) with a measurable >15% improvement in retrieval precision on keyword-specific test queries compared to the baseline cosine-similarity approach."