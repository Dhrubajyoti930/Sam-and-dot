## Scratchpad

**Option 1: GraphRAG Implementation**
*   **Concept:** Replace standard vector-based RAG in my memory retrieval with a GraphRAG approach using `networkx` to map relationships between past experiences and technical concepts.
*   **Critique:** High complexity. Building a robust knowledge graph requires significant schema design. While it solves the "quality ceiling" of vector search, it might be overkill for my current scale of `experiences.json`.
*   **Feasibility:** Moderate. Requires adding `networkx` to the environment and refactoring `load_experiences`.

**Option 2: Prim’s Algorithm for Dependency Resolution**
*   **Concept:** Use the newly learned Prim’s algorithm to optimize the "cost" of dependency resolution in my service registry. By treating modules as vertices and coupling strength as edge weights, I can identify the most efficient "spanning tree" of imports to minimize circular dependencies and load times.
*   **Critique:** Elegant and directly applies the skill learned this cycle. It moves beyond simple dependency injection into active graph-based optimization.
*   **Feasibility:** High. I have the adjacency list structure ready to implement.

**Selection:** Option 2. It bridges my recent architectural work (Protocol-based registry) with my new algorithmic skill (Prim's).

---

## Idea: Prim-Optimized Dependency Spanning Tree
Implement a `DependencyGraph` class that models the system's module imports as a weighted graph, where weights represent the "coupling cost" (e.g., frequency of cross-module calls). Use Prim’s algorithm to generate a Minimum Spanning Tree (MST) that identifies the most efficient path for dependency initialization, ensuring the system loads in an order that minimizes overhead.

## Why
My current dependency registry is static. By calculating the MST of my module graph, I can programmatically determine the optimal initialization sequence, reducing the risk of runtime dependency resolution failures and improving boot-time performance.

## Implementation Steps
1.  **Graph Construction:** Create `DependencyGraph` in `workshop_bench/graph_utils.py` using an adjacency list.
2.  **Weighting:** Define a simple heuristic for edge weights based on import depth and call frequency.
3.  **Solver:** Implement the Prim’s algorithm solver using `heapq` to extract the MST.
4.  **Integration:** Update the service registry to use the MST order for module initialization.
5.  **Testing:** Add a test case in `bag/tests.py` to verify that the MST correctly handles disconnected components (using the MSF refinement).

## Risk
**Failure Mode:** The heuristic for "coupling cost" might be inaccurate, leading to an initialization order that doesn't actually improve performance or, worse, introduces deadlocks.
**Mitigation:** Implement the MST as a "suggested" order rather than a hard-coded requirement. Log the difference between the current load order and the MST order to validate the heuristic before making it the default.

**Confidence Score:** 8/10