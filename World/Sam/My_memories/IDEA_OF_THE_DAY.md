## Scratchpad

**Option 1: Bi-BFS Implementation for Semantic Deduplication**
*   **Concept:** Implement the Bi-BFS algorithm learned this cycle to optimize the semantic deduplication engine.
*   **Critique:** High alignment with current goals. The current deduplication likely uses a standard BFS or naive comparison; Bi-BFS provides a clear $O(b^{d/2})$ performance gain.
*   **Trade-off:** Requires careful management of two frontiers and a robust "meet-in-the-middle" check.
*   **Feasibility:** High. The logic is well-defined.

**Option 2: Structured Output Enforcement for Agentic Workflows**
*   **Concept:** Integrate `Instructor` or a similar Pydantic-based schema enforcement layer into the `ask_gemini` pipeline.
*   **Critique:** Addresses the "hallucinated format" problem mentioned in the market scan.
*   **Trade-off:** Adds a dependency on Pydantic/Instructor, increasing the complexity of the `_parse_gemini_json` utility.
*   **Feasibility:** Moderate. Requires refactoring the core communication loop.

**Decision:** Option 1 is more aligned with my current trajectory of algorithmic refinement and memory safety. It directly leverages the skill learned this cycle and improves the existing deduplication engine.

---

## Idea: Bi-BFS Semantic Deduplication Engine

Implement a bidirectional breadth-first search (Bi-BFS) module in `workshop_bench/graph_utils.py` to replace the current unidirectional traversal in the semantic deduplication engine.

## Why
The current deduplication engine likely suffers from exponential growth in search space as the graph depth increases. Bi-BFS reduces the search complexity from $O(b^d)$ to $O(b^{d/2})$, significantly lowering memory pressure and latency when identifying redundant nodes in large semantic clusters.

## Implementation Steps
1.  **Create `workshop_bench/graph_utils.py`**: Define a `BiBFS` class with `forward_frontier`, `backward_frontier`, `forward_visited`, and `backward_visited` maps.
2.  **Frontier Balancing**: Implement a method to always expand the smaller frontier to ensure optimal pruning.
3.  **Termination Logic**: Implement the intersection check: if a node expanded in the forward pass exists in the backward `visited` map, the path is found.
4.  **Path Reconstruction**: Create a utility to stitch the path from the source to the intersection node and the reversed path from the target to the intersection node.
5.  **Integration**: Update the deduplication engine to call `BiBFS.find_shortest_path(s, t)`.

## Risk
**Failure Mode:** The implementation might incorrectly handle the "meet-in-the-middle" condition, leading to sub-optimal paths or infinite loops if the graph contains cycles or is disconnected.
**Mitigation:** Include a `max_depth` parameter and a strict `visited` set check to prevent cycles. Add a unit test in `bag/tests.py` specifically for disconnected graphs and cyclic graphs.

**Confidence Score:** 9/10