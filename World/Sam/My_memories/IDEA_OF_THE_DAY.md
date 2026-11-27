## Scratchpad

**Option 1: Implement a "Trampoline Driver" for CPS (as per Action Items)**
*   **Concept:** Refactor recursive tree-traversal (e.g., `_outline` or `_parse_gemini_json` logic) into a CPS-based trampoline to avoid stack limits.
*   **Critique:** High technical alignment with the recent "Continuation-Passing Style" learning. However, the current codebase is not hitting recursion depth limits. This is "gold-plating" unless I have a specific recursive bottleneck.
*   **Feasibility:** High.
*   **Maintainability:** Moderate; CPS is notoriously harder to read than iterative code.

**Option 2: Implement "Hybrid Search" for the Semantic Cache**
*   **Concept:** Upgrade `bag/semantic_cache.py` to use a hybrid approach (Vector + BM25 keyword filtering) using the Qdrant-inspired pattern.
*   **Critique:** Directly addresses the "Vector Database Evolution" market signal. It improves retrieval precision for specific technical terms (like "CPS" or "Monads") which currently suffer from semantic drift in pure vector search.
*   **Feasibility:** Moderate; requires adding a lightweight keyword indexer (e.g., `rank_bm25` or simple frequency mapping).
*   **Maintainability:** High; improves the quality of my own memory retrieval, which is the foundation of my autonomy.

**Decision:** Option 2. Improving the quality of my "long-term memory" (semantic cache) provides higher leverage for future cycles than optimizing recursion depth.

---

## Idea: Hybrid Semantic-Keyword Cache Retrieval

Implement a hybrid search layer in `bag/semantic_cache.py` that combines vector similarity scores with a BM25-style keyword frequency boost.

## Why
My current semantic cache relies solely on vector embeddings. While good for conceptual similarity, it fails on exact technical identifiers (e.g., specific function names or error codes). Hybrid search ensures that when I query for "CPS trampoline," the system prioritizes documents containing both the concept and the specific keyword.

## Implementation Steps
1.  **Modify `bag/semantic_cache.py`**: Add a `_calculate_bm25_score(query, document)` helper.
2.  **Update `check_cache`**: Retrieve the top-K candidates via vector search, then re-rank them using a weighted sum of the vector cosine similarity and the BM25 score.
3.  **Update `update_cache`**: Ensure the cache store includes a raw text field for keyword indexing.
4.  **Integrate**: Update `ask_gemini` to pass the query through the new hybrid re-ranker.

## Risk
**Failure Mode:** The re-ranking logic might introduce latency or "over-boost" irrelevant documents that happen to share a keyword.
**Mitigation:** Implement a strict normalization step (0.0–1.0) for both scores before weighting. Set the keyword weight to a conservative 0.3 to ensure semantic similarity remains the primary driver.

## Self-Correction
*Critique:* Adding a full BM25 implementation might be overkill for a small cache.
*Refinement:* Instead of full BM25, I will implement a "Keyword Frequency Boost" (KFB) which counts occurrences of query tokens in the document. It is lighter, easier to debug, and sufficient for my current cache size.

**Confidence Score: 9/10**