## Scratchpad

**Option 1: Dynamic Rebalancing for Ball Trees**
*   **Concept:** Implement a `rebalance()` method for the Ball Tree that triggers when the tree's aspect ratio (max depth / min depth) exceeds a threshold.
*   **Critique:** High complexity. Requires tracking node statistics during insertions. While it solves the "static dataset" weakness, it risks over-engineering a structure that might be better replaced by HNSW if the data is truly dynamic.
*   **Feasibility:** Moderate.

**Option 2: HNSW (Hierarchical Navigable Small World) Integration**
*   **Concept:** Pivot from the exact search of Ball Trees to an approximate search using HNSW.
*   **Critique:** HNSW is the industry standard for high-dimensional vector search. Implementing it from scratch is a massive undertaking, but implementing a wrapper for a lightweight library (like `hnswlib`) would provide immediate, production-grade performance gains.
*   **Feasibility:** High (if using a library) / Low (if building from scratch).

**Option 3: Ball Tree Pruning Optimization (Selected)**
*   **Concept:** Refine the existing Ball Tree implementation to include a "Leaf-Size Adaptive" construction. Instead of a fixed leaf size, calculate the optimal leaf size based on the dataset's dimensionality and density.
*   **Critique:** This directly addresses the "curse of dimensionality" mentioned in my learning summary without the overhead of a full rebalancing engine or external dependencies. It is a surgical, high-leverage improvement.

---

## Idea: Adaptive Leaf-Size Ball Tree Construction

Implement an adaptive heuristic for Ball Tree construction that dynamically sets the `leaf_size` parameter based on the ratio of $N$ (number of points) to $D$ (dimensionality).

## Why
Fixed `leaf_size` parameters often lead to either excessive tree depth (too small) or inefficient linear scans (too large). By dynamically tuning this based on the dataset, I can optimize the "crossover point" between tree traversal and brute-force distance calculation, directly improving query latency in the `workshop_bench` library.

## Implementation Steps
1.  **Metric Calculation:** Add a helper function to estimate the "density" of the feature space: $\rho = N / 2^D$.
2.  **Heuristic Logic:** Define a mapping where $\rho$ determines the `leaf_size` (e.g., $\rho < 1 \rightarrow$ smaller leaves; $\rho > 10 \rightarrow$ larger leaves).
3.  **Refactor:** Update the `BallTree` constructor to accept an `auto_tune=True` flag that invokes this heuristic before building the tree.
4.  **Verification:** Add a test case in `bag/tests.py` that compares search latency on a high-dimensional vs. low-dimensional dataset to confirm the adaptive logic improves performance.

## Risk
**Failure Mode:** The heuristic might miscalculate for non-uniform data distributions (e.g., clusters), leading to a "lopsided" tree that performs worse than a fixed-size tree.
**Mitigation:** Implement a "sanity check" during construction: if the resulting tree depth exceeds a safety threshold, fall back to a default `leaf_size`.

**Confidence Score:** 8/10