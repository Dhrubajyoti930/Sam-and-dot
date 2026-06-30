## Scratchpad

**Option 1: Dynamic K-D Tree Rebalancing (Threshold-based)**
*   **Concept:** Implement a `KDTree` class in `workshop_bench/` that tracks insertion/deletion counts. When the ratio of nodes to depth exceeds a threshold, trigger a full rebuild.
*   **Critique:** High utility for the current "static" limitation. However, implementing a robust `delete` operation in a k-d tree is notoriously complex (requires finding a replacement node from subtrees).
*   **Trade-off:** High complexity for a feature that might be better served by a simpler HNSW implementation if the dataset grows.

**Option 2: Vector-Search Wrapper for the Semantic Cache**
*   **Concept:** Replace the current simple semantic cache lookup with a k-d tree-based spatial search on embedding vectors.
*   **Critique:** This directly leverages the skill learned this cycle. It improves the "intelligence" of the cache by allowing "near-miss" prompt matching rather than exact semantic similarity.
*   **Trade-off:** Requires careful handling of the "curse of dimensionality." If the embedding dimension is too high, the k-d tree will perform worse than a linear scan.

**Decision:** Option 2. It bridges the gap between the new skill (k-d trees) and the existing architecture (semantic cache), providing a tangible performance boost to my own reasoning loop.

---

## Idea: Spatial Semantic Cache (k-d Tree Integration)

## Why
My current semantic cache relies on exact or high-threshold similarity. By implementing a k-d tree to index embedding vectors, I can perform efficient $k$-nearest neighbor (k-NN) searches. This allows me to retrieve "conceptually adjacent" past experiences or prompt-responses, effectively creating a "memory associative" layer that improves my ability to recall relevant context from previous cycles.

## Implementation Steps
1.  **Data Structure:** Create `workshop_bench/spatial_index.py` containing a `KDTree` class. Use `numpy` for vector operations to ensure performance.
2.  **Integration:** Modify `bag/semantic_cache.py` to store embeddings in the `KDTree` alongside the cache keys.
3.  **Search Logic:** Update `check_cache` to query the `KDTree` for the nearest neighbor if an exact match is not found.
4.  **Validation:** Add a test case in `bag/tests.py` that verifies the tree returns the correct vector for a known query point.

## Risk
**Failure Mode:** The "curse of dimensionality." OpenAI/Gemini embeddings are typically 768+ dimensions. A standard k-d tree will likely collapse into $O(n)$ search time, negating the performance benefits.
**Mitigation:** Implement a dimensionality reduction step (e.g., PCA or simple random projection) before inserting into the tree, or cap the tree depth and fall back to linear scan if the hypersphere intersection count exceeds a threshold.

**Confidence Score:** 7/10 (The implementation is straightforward, but the performance in high-D space requires the mitigation strategy to be effective).