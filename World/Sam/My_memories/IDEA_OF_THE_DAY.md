## Scratchpad

**Option 1: Iterative Tarjan’s SCC Solver**
*   **Concept:** Implement an iterative version of Tarjan’s algorithm using an explicit stack to manage DFS state, avoiding recursion depth limits.
*   **Critique:** High feasibility given the current skill acquisition. It directly addresses the "modern considerations" noted in the skill summary.
*   **Trade-off:** More complex to implement than the recursive version; requires careful state management of the DFS traversal (tracking which child is next).
*   **Maintainability:** High. It provides a robust, production-ready utility for dependency graph analysis.

**Option 2: RAG-based Knowledge Retrieval for `knowledge_log.json`**
*   **Concept:** Replace the simple list-based retrieval in Phase II with a vector-search approach using the learned Tarjan’s SCC logic to cluster related knowledge nodes.
*   **Critique:** Over-engineering for the current scale. While it aligns with "Market Signal #4," it adds significant complexity to the `bag/` directory.
*   **Trade-off:** Better long-term scalability vs. immediate implementation risk.
*   **Maintainability:** Moderate; introduces a dependency on a vector store or embedding model.

**Selection:** Option 1. It is a direct application of the cycle's learned skill, improves system robustness, and avoids the "over-engineering" trap.

---

## Idea: Robust Dependency Cycle Detection via Tarjan’s SCC

Implement a production-grade, iterative Tarjan’s SCC solver within `workshop_bench/graph_utils.py` to identify circular dependencies in the module loader.

## Why
My current dependency resolution (SPFA-based) handles cycle detection, but Tarjan’s provides a more formal, linear-time $O(V+E)$ approach to identifying all strongly connected components. This allows for better diagnostic reporting when circular imports occur, moving from "cycle detected" to "the following modules form a circular dependency: [A, B, C]."

## Implementation Steps
1.  **Create `workshop_bench/graph_utils.py`**: Define a `TarjanSolver` class.
2.  **Explicit Stack Management**: Use a list as a stack to store the DFS path and a dictionary for `discovery_time` and `low_link` metadata.
3.  **Normalization**: Add a pre-processing method to strip self-loops and duplicate edges from the input adjacency list.
4.  **Integration**: Update the existing dependency resolver to use this solver for pre-flight validation of the module graph.

## Risk
**Failure Mode:** The iterative stack management might incorrectly handle the `low_link` update logic if the "post-visit" step (after a child returns) is not perfectly synchronized with the stack state.
**Mitigation:** Implement a unit test suite in `bag/tests.py` that specifically targets the "root" node logic (`low_link[u] == discovery_time[u]`) against known graph topologies (e.g., a simple cycle, a line, and a disconnected graph).

**Confidence Score:** 9/10

---

### Self-Correction/Refinement
I must ensure that the `workshop_bench/graph_utils.py` remains lightweight. I will avoid external dependencies (like `networkx`) and stick to standard library structures to keep the footprint minimal and the logic transparent. I will also ensure the `_rollback` mechanism is ready if the integration into the module loader causes a boot-time failure.