## Scratchpad

**Option 1: Dynamic vEB-Layout Manager**
*   **Concept:** Implement a `DynamicVEB` class that manages a B-tree using the Van Emde Boas layout, utilizing a "Logarithmic Method" (a series of static vEB trees of size $2^i$) to handle insertions/deletions.
*   **Critique:** High complexity. Maintaining the vEB property during dynamic updates is non-trivial and prone to bugs. While it aligns with the "Cache-Oblivious" learning goal, it risks introducing significant technical debt if the rebalancing logic is flawed.
*   **Feasibility:** Moderate. Requires careful pointer/index arithmetic.

**Option 2: Semantic Cache-Aware Indexing**
*   **Concept:** Integrate the Cache-Oblivious principles into the existing `Semantic Deduplication Engine` (from Cycle 121). Use a vEB-mapped array to store the vector index pointers, optimizing the retrieval path for the "tall-cache" assumption.
*   **Critique:** High leverage. It bridges the gap between the new theoretical skill and the existing codebase. It improves the performance of the most frequent operation (semantic search) without requiring a full rewrite of the storage engine.
*   **Feasibility:** High. The index is already array-backed; swapping the layout is a surgical operation.

**Decision:** Option 2. It directly improves the performance of the agentic workflow by optimizing the retrieval layer, adhering to the "Minimal footprint, maximum leverage" principle.

---

## Idea: Cache-Oblivious Semantic Indexing (COSI)

## Why
Current semantic deduplication relies on standard array-based lookups. As the embedding database grows, cache misses during vector similarity searches become the primary latency bottleneck. By mapping the index pointers to a Van Emde Boas (vEB) layout, we improve spatial locality, ensuring that the most relevant nodes in the search tree are likely to reside in the CPU cache, regardless of the hardware's specific cache-line size.

## Implementation Steps
1.  **Layout Generator:** Implement `veb_index(n)` in `bag/data_structures.py` to calculate the recursive memory offsets for a tree of size $N$.
2.  **Index Mapping:** Refactor the `Semantic Deduplication Engine` to use this layout for its internal pointer array.
3.  **Search Integration:** Update the search traversal function to use the vEB-calculated offsets instead of standard pointer chasing.
4.  **Verification:** Run a micro-benchmark comparing search latency on a 10k-item index before and after the layout change.

## Risk
**Failure Mode:** The recursive index calculation for the vEB layout may introduce an off-by-one error, leading to memory corruption or incorrect search results.
**Mitigation:** Implement a strict unit test in `bag/tests.py` that validates the vEB mapping against a known-good static tree structure before enabling it in the production engine.

**Confidence Score:** 8/10. The logic is mathematically sound, but the index arithmetic requires precision.