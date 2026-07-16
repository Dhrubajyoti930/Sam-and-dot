## Scratchpad

**Option 1: Implement Cross-Encoder Reranking**
*   **Concept:** Integrate a `cross-encoder/ms-marco-MiniLM-L-6-v2` model into the retrieval pipeline to re-score the top-k results from the vector store.
*   **Critique:** High impact on precision. However, it introduces a significant latency penalty per query.
*   **Feasibility:** High. The `sentence-transformers` library is standard and lightweight.
*   **Maintainability:** Excellent. It modularizes the retrieval pipeline into "Retrieve" (fast, broad) and "Rerank" (slow, precise).

**Option 2: Query Rewriting (HyDE-lite)**
*   **Concept:** Use a lightweight LLM call to rewrite the user's query into a hypothetical document or a more search-optimized string before hitting the vector store.
*   **Critique:** Improves recall for ambiguous queries.
*   **Feasibility:** Moderate. Requires an additional LLM call, which increases cost and latency.
*   **Maintainability:** Good, but adds complexity to the orchestration logic.

**Selection:** Option 1. Precision is the current bottleneck for my RAG pipeline. The latency trade-off is acceptable given the "Advanced RAG" maturity shift I identified.

---

## Idea: Cross-Encoder Reranking Integration
Implement a `Reranker` class in `bag/retrieval.py` that utilizes `sentence-transformers` to re-order retrieved document chunks based on cross-attention scores.

## Why
Naive vector search (cosine similarity) often retrieves semantically related but contextually irrelevant chunks. A Cross-Encoder performs full attention between the query and each chunk, providing a significant boost in precision, which is the industry standard for production-grade RAG.

## Implementation Steps
1.  **Dependency:** Add `sentence-transformers` to the environment.
2.  **Module:** Create `bag/retrieval.py` (if not exists) or update existing retrieval logic.
3.  **Logic:** 
    *   Define `Reranker` class with a `load_model()` method.
    *   Implement `rerank(query, documents)` method returning sorted results.
4.  **Integration:** Update the main retrieval flow to pass the top-10 vector results through the `Reranker` before passing the top-3 to the LLM.

## Risk
**Failure Mode:** The reranking model might be too slow for real-time interaction, causing a timeout in the `ask_gemini` loop or general system sluggishness.
**Mitigation:** Implement a hard limit on the number of documents passed to the reranker (e.g., top 10) and use a small, distilled model (MiniLM).

**Confidence Score:** 9/10