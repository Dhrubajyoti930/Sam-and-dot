## Scratchpad

**Option 1: Semantic Similarity Thresholding for RAG**
*   **Concept:** Implement a cosine similarity check between the query and the retrieved parent chunk. If the score is below a threshold (e.g., 0.7), the system falls back to the child chunk or a smaller sub-segment.
*   **Critique:** High precision, but introduces a "magic number" (the threshold) that may vary by domain. Requires tuning.
*   **Feasibility:** High. Fits perfectly into the existing parent-child retrieval logic.

**Option 2: Dynamic Windowing for Contextual Enrichment**
*   **Concept:** Instead of a fixed parent chunk, dynamically construct a context window based on the query's semantic density.
*   **Critique:** More robust than static parent-child, but significantly more complex to implement and test. Risk of "context bloat" if the window is too large.
*   **Feasibility:** Medium. Requires a more sophisticated retrieval orchestrator.

**Decision:** Option 1 is more aligned with my "minimal footprint, maximum leverage" philosophy. It provides immediate, measurable improvements to retrieval quality without over-engineering the architecture.

---

## Idea: Semantic Thresholding for Parent-Child Retrieval

Implement a `similarity_gate` in the retrieval pipeline that validates the relevance of the retrieved parent chunk against the user query before passing it to the LLM.

## Why
Parent-child chunking risks "semantic drift" if the parent chunk is large and contains multiple topics. A similarity gate ensures that the context provided to the LLM is not just "nearby" in the document, but actually relevant to the specific query, reducing hallucinations and noise.

## Implementation Steps
1.  **Update Retrieval Logic:** Modify the retrieval function to calculate the cosine similarity between the query embedding and the parent chunk embedding.
2.  **Define Threshold:** Set a configurable `SIMILARITY_THRESHOLD` (default 0.75).
3.  **Conditional Logic:** 
    *   If `similarity >= threshold`: Return parent chunk.
    *   If `similarity < threshold`: Return the child chunk (the original search hit) as the primary context, as it is guaranteed to be semantically closer to the query.
4.  **Logging:** Log the similarity scores for all retrievals to `bag/retrieval_metrics.json` to allow for future threshold tuning.

## Risk
**Failure Mode:** The threshold might be too aggressive, causing the system to discard useful parent context in favor of fragmented child chunks.
**Mitigation:** Implement a "soft-fail" mode where the system returns the parent chunk but adds a metadata flag `is_low_confidence: true`, allowing the LLM to treat that context with higher skepticism.

**Confidence Score:** 9/10