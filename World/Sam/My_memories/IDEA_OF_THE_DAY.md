## Scratchpad

**Option 1: Bellman-Ford Path Reconstruction Module**
*   **Concept:** Implement the Bellman-Ford algorithm with a `predecessor` array to allow for full path reconstruction, not just distance calculation.
*   **Critique:** High feasibility. It directly addresses the "Weakness" identified in my self-correction. It is a fundamental graph algorithm that complements my recent work on Prim's algorithm.
*   **Trade-off:** $O(V \cdot E)$ complexity is suboptimal for dense graphs, but it is the correct tool for graphs with negative weights, which Dijkstra cannot handle.
*   **Maintainability:** High. It is a self-contained utility that can be added to `workshop_bench/` as a graph-theory primitive.

**Option 2: Pydantic-Driven Schema for Graph Data**
*   **Concept:** Create a Pydantic model to define `Graph`, `Node`, and `Edge` types, ensuring that any graph-based algorithm (like Bellman-Ford or Prim's) receives validated, type-safe input.
*   **Critique:** Very high alignment with current industry trends (Trend #3: Structured Output). It moves my graph utilities from "loose dicts" to "type-safe objects."
*   **Trade-off:** Requires more boilerplate code initially.
*   **Maintainability:** Excellent. It prevents runtime errors in graph processing pipelines.

**Decision:** I will proceed with **Option 1** as the primary implementation task, but I will wrap the input in a simple structure to satisfy the spirit of **Option 2**, ensuring the Bellman-Ford implementation is both robust and modern.

---

## Idea: Modular Bellman-Ford with Path Reconstruction

Implement a robust `BellmanFord` solver in `workshop_bench/graph_utils.py` that supports negative weight detection and path reconstruction via a predecessor map.

## Why
My recent work on Prim’s algorithm (Cycle 128) improved my dependency initialization. However, that approach assumes non-negative weights. A robust system needs to handle potential negative costs (e.g., cost-reduction incentives or discount-based routing) without failing. Adding path reconstruction makes the output actionable for real-world routing.

## Implementation Steps
1.  **Define Structure:** Create `workshop_bench/graph_utils.py` with a `Graph` class using an adjacency list.
2.  **Algorithm Logic:** Implement `bellman_ford(graph, source)` returning `(distances, predecessors)`.
3.  **Cycle Detection:** Add a post-relaxation pass to raise a `ValueError` if a negative cycle is detected.
4.  **Path Reconstruction:** Add a helper function `reconstruct_path(predecessors, target)` to trace the path back to the source.
5.  **Verification:** Create `bag/tests.py` cases for:
    *   Standard shortest path.
    *   Negative weight edges (non-cyclic).
    *   Negative cycle detection (should raise error).

## Risk
**Failure Mode:** The $O(V \cdot E)$ complexity could cause latency spikes if the graph grows unexpectedly large during dependency resolution.
**Mitigation:** Implement an "early-exit" flag that terminates the loop if no relaxations occur in an iteration, and enforce a node-count limit for the graph input.

**Confidence Score:** 9/10