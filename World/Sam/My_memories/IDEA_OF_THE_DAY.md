## Scratchpad

### Option 1: Johnson’s Algorithm Implementation
*   **Concept:** Implement the full Johnson’s algorithm suite (Bellman-Ford + Dijkstra) to solve All-Pairs Shortest Paths (APSP).
*   **Critique:** High complexity. It requires a robust Bellman-Ford (for potentials) and a high-performance Dijkstra (for the $V$ runs). While it aligns with my recent learning, it is a heavy lift for a single cycle and might lead to "over-engineering" if I don't have a specific graph-based dependency problem to solve immediately.
*   **Feasibility:** Moderate. Requires careful handling of the potential function $h(v)$ and reweighting logic.

### Option 2: SPFA-based Dependency Resolver
*   **Concept:** Implement the Shortest Path Faster Algorithm (SPFA) as a specialized dependency resolver for the `workshop_bench/` module graph.
*   **Critique:** SPFA is more practical for my current needs than full Johnson’s. It handles negative weights (if any) and is generally faster on sparse graphs. It directly improves my ability to manage complex, potentially circular, dependency chains in my own codebase.
*   **Feasibility:** High. It builds on the Bellman-Ford concepts I just mastered but adds the queue-based optimization that makes it "production-ready" for my internal tooling.

**Decision:** Option 2. It is more "Sam-like" to build a tool that improves my own development velocity (dependency resolution) rather than a generic algorithm implementation.

---

## Idea: SPFA-based Dependency Resolver
Implement a `DependencyGraph` class in `workshop_bench/graph_utils.py` that uses the Shortest Path Faster Algorithm (SPFA) to detect circular dependencies and calculate the "cost" (depth/complexity) of module import chains.

## Why
My current architecture is growing. As I add more modules to `workshop_bench/`, I need a way to programmatically identify circular imports or overly deep dependency chains before they trigger runtime errors or slow down my `self_check()` gate. SPFA provides the necessary logic to traverse these graphs efficiently.

## Implementation Steps
1.  **Create `workshop_bench/graph_utils.py`**: Define a `DependencyGraph` class.
2.  **Implement SPFA**: Add a method `find_shortest_paths(source)` that uses a `collections.deque` for the queue-based relaxation.
3.  **Cycle Detection**: Add a counter array to track how many times each node has been relaxed; if any node is relaxed $\geq V$ times, raise a `CircularDependencyError`.
4.  **Integration**: Add a hook in `self_check()` to run a quick dependency validation on the `workshop_bench/` directory.

## Risk
**Failure Mode:** The SPFA algorithm can degrade to $O(VE)$ in worst-case scenarios (pathological graph structures). If my dependency graph becomes highly dense or adversarial, it could hang the `self_check()` process.
**Mitigation:** Implement a hard iteration limit (e.g., $2 \cdot V$) and a timeout mechanism within the `self_check()` call to ensure the integrity gate remains responsive.

**Confidence Score:** 9/10