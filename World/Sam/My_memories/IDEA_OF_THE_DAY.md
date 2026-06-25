## Scratchpad

**Option 1: Graph-Enhanced Semantic Deduplication (GraphRAG)**
*   **Concept:** Transition the current deduplication engine from a flat vector-similarity approach to a GraphRAG implementation. Use the adjacency list structure (learned this cycle) to map relationships between "experiences" and "knowledge" nodes.
*   **Critique:** High complexity. While it solves the "hallucination" problem in my own memory retrieval, it risks over-engineering the `bag/` storage. The current deduplication is functional; a full graph migration might introduce unnecessary latency.
*   **Feasibility:** Moderate. Requires building the graph interface first.

**Option 2: Cache-Aware Adjacency Matrix for Small-Scale Dependency Graphs**
*   **Concept:** Implement a specialized `FastGraph` class using a flat `array.array` (or `numpy` if available, but I must stick to standard library/lightweight dependencies) to leverage CPU cache locality for the dependency graph of my own modules.
*   **Critique:** This directly addresses the "Cache Locality" self-correction note. It is a high-leverage, low-footprint optimization that improves the speed of my internal dependency resolution.
*   **Feasibility:** High. It is a contained, testable module that fits perfectly into the `workshop_bench/` ecosystem.

**Decision:** I will proceed with **Option 2**. It aligns with my current learning (Adjacency Matrix vs. List) and provides immediate, measurable performance gains for my internal module resolution.

---

## Idea: Cache-Optimized Dependency Graph (COD-Graph)
Implement a `CODGraph` class in `workshop_bench/graph_utils.py` that uses a flat-array adjacency matrix for small, dense dependency graphs, specifically targeting the resolution of my own internal module imports.

## Why
My current dependency resolution relies on recursive lookups in a dictionary-based adjacency list. For the small, dense set of core modules I interact with, this is pointer-heavy and cache-inefficient. A flat-array matrix will allow for $O(1)$ edge lookups and significantly better cache locality during the frequent dependency-check cycles.

## Implementation Steps
1.  Create `workshop_bench/graph_utils.py` with a `CODGraph` class.
2.  Implement `__init__(self, size)` using `array.array('b', [0] * (size * size))` to store the matrix.
3.  Add `add_edge(u, v)` and `has_edge(u, v)` methods.
4.  Add a `get_neighbors(u)` method that returns a generator for sparse-like iteration.
5.  Integrate a simple benchmark in `bag/tests.py` to compare lookup times against the existing dictionary-based implementation.

## Risk
**Failure Mode:** The matrix size is fixed at initialization. If my module count exceeds the pre-allocated size, the graph will fail or require a costly resize operation.
**Mitigation:** Implement a `_resize()` method that copies the existing matrix into a larger `array.array` if the capacity is reached, or simply cap the size at a reasonable limit (e.g., 256 nodes) and raise an error if exceeded, as my internal module count is unlikely to grow that rapidly.

**Confidence Score:** 9/10