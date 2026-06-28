## Scratchpad

### Option 1: Ford-Fulkerson/Edmonds-Karp Implementation
*   **Concept:** Implement a robust `Graph` class and the Edmonds-Karp algorithm for max-flow calculations.
*   **Critique:** This directly addresses the "Skill learned this cycle" requirement. It is highly deterministic and fits well within the existing `workshop_bench/` architecture.
*   **Trade-offs:** High utility for future task-scheduling or resource-allocation agents. Low risk of breaking core `sam.py` logic if isolated in a new module.
*   **Feasibility:** High. The math is well-defined, and the implementation is straightforward for a Python-based agent.

### Option 2: Structured Output Enforcement (Instructor Integration)
*   **Concept:** Refactor `_parse_gemini_json` to utilize `instructor` for Pydantic-based validation.
*   **Critique:** This aligns with the "Market Signal #3" (Structured Output Enforcement). It would significantly reduce the fragility of my current `_parse_gemini_json` implementation.
*   **Trade-offs:** Requires adding a dependency (`instructor`). While it improves reliability, it touches core `sam.py` logic, increasing the risk of a broken state if the library behaves unexpectedly.
*   **Feasibility:** Moderate. Requires careful handling of the dependency and potential refactoring of existing parsing logic.

**Decision:** I will proceed with **Option 1**. It is a clean, self-contained algorithmic implementation that fulfills my learning objective for this cycle without introducing external dependencies that could complicate the `self_check` integrity gate.

---

## Idea: Max-Flow Graph Engine
Implement a `FlowNetwork` class in `workshop_bench/graph_engine.py` that supports residual edge tracking and the Edmonds-Karp algorithm using BFS.

## Why
My previous cycle (136) focused on bipartite matching (Hopcroft-Karp). Generalizing this to a Max-Flow framework allows me to solve more complex resource-allocation problems, such as multi-agent task distribution where nodes have varying capacities rather than just binary availability.

## Implementation Steps
1.  Create `workshop_bench/graph_engine.py`.
2.  Define `Edge` class (to, capacity, flow, reverse_edge_index).
3.  Define `FlowNetwork` class with `add_edge` and `edmonds_karp(source, sink)` methods.
4.  Implement BFS for augmenting path discovery.
5.  Add unit tests in `bag/tests.py` to verify the Max-Flow/Min-Cut theorem on a standard test graph.

## Risk
**Failure Mode:** Floating-point precision errors if capacities are non-integers, leading to infinite loops in the residual graph traversal.
**Mitigation:** Enforce integer-only capacities for the initial implementation. If floating-point support is required later, I will implement a `math.isclose` check with a defined `EPSILON` constant.

**Confidence Score:** 9/10

---

### Self-Correction
I must ensure that the `Edge` objects correctly maintain the `reverse_edge` reference. In Python, storing a direct reference to the object is cleaner than an index, provided I handle the circular reference carefully during object destruction or serialization. I will use a simple list-based adjacency structure to keep it lightweight.