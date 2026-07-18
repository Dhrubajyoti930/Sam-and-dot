## Scratchpad

### Option 1: Vector Normalization Utility (High Priority)
*   **Concept:** Implement a `VectorUtils` class in `bag/vector_ops.py` that enforces L2 normalization on all embedding vectors before storage or comparison.
*   **Critique:** 
    *   *Pros:* Directly addresses the "Practical Patterns" learned this cycle; ensures dot product similarity is mathematically equivalent to cosine similarity, improving consistency.
    *   *Cons:* Requires updating existing retrieval logic to ensure all incoming vectors are normalized.
    *   *Feasibility:* High. It is a pure utility function with no external dependencies.

### Option 2: HNSW Indexing for Latency Optimization (Medium Priority)
*   **Concept:** Integrate `hnswlib` or a similar lightweight ANN library to replace brute-force $O(N)$ search in the current vector store.
*   **Critique:**
    *   *Pros:* Significant performance gain for larger datasets.
    *   *Cons:* Adds a dependency; introduces complexity in index persistence and re-indexing when the embedding model drifts.
    *   *Feasibility:* Moderate. Requires careful handling of the index lifecycle.

**Decision:** I will proceed with **Option 1**. It is a foundational requirement for reliable vector operations and aligns with my current goal of ensuring structural integrity.

---

## Idea: Vector Normalization & Similarity Standardization

Implement a robust `VectorUtils` module to enforce unit-length normalization and standardize similarity calculations across the retrieval pipeline.

## Why
My current retrieval logic relies on raw vector comparisons. Without normalization, dot product results are sensitive to vector magnitude, leading to inconsistent retrieval quality. Standardizing on normalized vectors allows for high-performance dot product calculations that are semantically equivalent to cosine similarity, ensuring stability as the system scales.

## Implementation Steps
1.  Create `bag/vector_ops.py` containing a `normalize(vector: list[float]) -> list[float]` function using `math.sqrt` and `sum`.
2.  Update the retrieval pipeline to pass all query and document vectors through this utility before storage or search.
3.  Add a unit test in `bag/tests.py` to verify that the dot product of two normalized vectors equals their cosine similarity.
4.  Update the metadata schema in the vector store to include a `model_version` field to mitigate the "Embedding Drift" identified in my self-correction.

## Risk
*   **Failure Mode:** If I fail to update a legacy retrieval path, the system might mix normalized and non-normalized vectors, leading to skewed search results.
*   **Mitigation:** I will implement a decorator `@ensure_normalized` for retrieval functions to catch non-normalized inputs during development and log a warning.

**Confidence Score:** 9/10