## Scratchpad

**Option 1: Implement a Vector-Native Cache Layer**
*   **Concept:** Integrate a local Qdrant-lite or simple FAISS index into `bag/semantic_cache.py` to replace the current string-matching cache.
*   **Critique:** High impact on retrieval speed and relevance. However, it introduces a heavy dependency (FAISS/Qdrant) into the core `bag/` directory, which might complicate the `self_check` integrity gate if dependencies break.
*   **Feasibility:** Moderate. Requires careful handling of embedding generation within the existing `ask_gemini` flow.

**Option 2: Product Quantization (PQ) for Memory-Efficient Embeddings**
*   **Concept:** Implement the PQ encoder learned this cycle to compress the `semantic_cache` vectors.
*   **Critique:** Directly addresses the "memory footprint" bottleneck identified in the market scan. It is a pure algorithmic implementation, keeping dependencies low (standard `numpy`/`scipy`). It aligns perfectly with the "system-centric" shift.
*   **Feasibility:** High. The logic is self-contained and can be tested in isolation via `bag/tests.py`.

**Decision:** Option 2. It leverages the new skill, improves system performance, and maintains the "minimal footprint" requirement.

---

## Idea: PQ-Compressed Semantic Cache
Implement a `ProductQuantizer` class in `bag/vector_utils.py` to compress embedding vectors used by the semantic cache, enabling larger context windows without increasing RAM usage.

## Why
As the `semantic_cache` grows, storing full `float32` vectors for every interaction becomes inefficient. PQ allows for a 4x-8x reduction in memory usage while maintaining sufficient recall for cache hits, ensuring the system remains performant as the history of interactions expands.

## Implementation Steps
1.  **Create `bag/vector_utils.py`:** Implement `ProductQuantizer` with `fit` (k-means) and `transform` (quantization) methods.
2.  **Update `bag/semantic_cache.py`:** Integrate the quantizer into the cache storage flow.
3.  **Validation:** Add a test case in `bag/tests.py` to verify that the distance approximation error remains below a 5% threshold for a sample set of 1k vectors.
4.  **Integration:** Modify `check_cache` to perform Asymmetric Distance Computation (ADC) against the compressed codebook.

## Risk
**Failure Mode:** The quantization error might lead to "false negatives" where the cache fails to retrieve a relevant previous interaction because the distance approximation is too coarse.
**Mitigation:** Implement a "residual check" or a hybrid search where the top-K candidates from the PQ search are re-ranked using the original uncompressed vectors if the cache hit confidence is borderline.

**Confidence Score:** 8/10