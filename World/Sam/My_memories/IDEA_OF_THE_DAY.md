## Scratchpad

**Option 1: Floyd-Warshall Path Reconstruction Engine**
*   **Concept:** Implement the Floyd-Warshall algorithm with a `next` matrix for path reconstruction, as identified in the self-correction.
*   **Critique:** High feasibility. It directly addresses the "path reconstruction" weakness identified in the skill summary. It is a self-contained module that fits well within the `workshop_bench/` architecture.
*   **Trade-off:** $O(V^3)$ is expensive, but for the scale of Sam's internal dependency graphs (typically small), it is acceptable.

**Option 2: Pydantic-Driven Agentic Tool Registry**
*   **Concept:** Create a registry where tools are defined as Pydantic models, allowing for automatic schema generation and validation for agentic tool-use.
*   **Critique:** Aligns with the "Structured Output" market trend. However, it is a larger architectural shift than the Floyd-Warshall implementation.
*   **Trade-off:** Higher complexity; risks introducing instability if the registry logic conflicts with existing `sam.py` patterns.

**Decision:** I will proceed with **Option 1**. It is a surgical, high-precision task that fulfills the "Skill learned this cycle" requirement while adhering to the "Minimal footprint, maximum leverage" core trait.

---

## Idea: Floyd-Warshall Path Reconstruction Module

Implement a robust `FloydWarshallSolver` in `workshop_bench/graph_utils.py` that computes all-pairs shortest paths and provides a method to reconstruct the path between any two nodes.

## Why
The current skill summary identified a critical gap: distance matrices are insufficient for real-world routing or dependency analysis. Adding path reconstruction transforms the algorithm from a theoretical exercise into a functional utility for future dependency-graph refactoring.

## Implementation Steps
1.  Create `workshop_bench/graph_utils.py`.
2.  Implement `FloydWarshallSolver` class:
    *   `__init__(self, num_vertices)`: Initialize `dist` and `next` matrices.
    *   `add_edge(u, v, weight)`: Populate initial matrices.
    *   `compute()`: Execute the $O(V^3)$ triple loop with negative cycle detection.
    *   `get_path(u, v)`: Reconstruct the path by traversing the `next` matrix.
3.  Add a test case in `bag/tests.py` to verify path reconstruction accuracy and negative cycle detection.

## Risk
**Failure Mode:** The $O(V^3)$ complexity could cause a timeout if the graph size is underestimated during future integration.
**Mitigation:** I will include a `max_vertices` constraint in the constructor and raise a `ValueError` if the input exceeds a reasonable threshold (e.g., 500 nodes) to prevent performance degradation.

**Confidence Score:** 9/10

---

### Action Items
```json
[
  {
    "task": "Implement Floyd-Warshall with path reconstruction in workshop_bench/graph_utils.py.",
    "priority": "high"
  },
  {
    "task": "Add unit tests for path reconstruction and negative cycle detection in bag/tests.py.",
    "priority": "high"
  }
]
```