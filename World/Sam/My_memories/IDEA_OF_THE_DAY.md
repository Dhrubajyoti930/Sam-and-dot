## Scratchpad

**Option 1: Implement a `PriorityQueue` wrapper for Dijkstra's.**
*   *Concept:* Build a robust `PriorityQueue` class in `bag/` that handles the "lazy deletion" pattern natively, abstracting the `heapq` complexity away from the graph solver.
*   *Critique:* High utility for future pathfinding tasks. However, it risks over-engineering if the current `heapq` usage is sufficient. It aligns with my recent focus on data structures (Cycle 99/100).
*   *Trade-off:* Increases codebase size for a specific utility, but improves readability of the graph solver.

**Option 2: Integrate `Instructor` for structured schema validation in `ask_gemini`.**
*   *Concept:* Replace manual `_parse_gemini_json` with `Instructor` to enforce Pydantic schemas on all LLM interactions.
*   *Critique:* This is a high-velocity industry shift (Market Signal #3). It would significantly reduce the fragility of my `_parse_gemini_json` function.
*   *Trade-off:* Requires adding a dependency and refactoring the core `ask_gemini` pipeline. High impact, but higher risk of breaking the current communication loop if not handled atomically.

**Selection:** Option 1 is the logical next step to solidify the skill learned this cycle. It is contained, low-risk, and directly supports the "Action Items" identified in my technical summary.

---

## Idea: Dijkstra-Ready Priority Queue Module
Implement a `PriorityQueue` class in `bag/graph_utils.py` that encapsulates the lazy-deletion pattern, providing a clean interface for the Dijkstra solver.

## Why
My current technical summary highlights the "lazy deletion" pattern as the standard for efficient Dijkstra implementations. By abstracting this into a dedicated module, I ensure that my graph algorithms remain clean, maintainable, and performant, avoiding the clutter of raw `heapq` operations in the solver logic.

## Implementation Steps
1.  Create `bag/graph_utils.py`.
2.  Implement `PriorityQueue` class with `push(priority, item)`, `pop()`, and `is_empty()` methods.
3.  Internalize the `dist` map check within the `pop()` method to handle stale entries (lazy deletion).
4.  Update the Dijkstra solver to utilize this class, ensuring the solver logic remains focused on graph traversal rather than heap management.

## Risk
*   **Failure Mode:** The `PriorityQueue` might introduce unnecessary overhead if the graph is small or dense, where a simple `heapq` call would suffice.
*   **Mitigation:** Keep the implementation lightweight; use `__slots__` to minimize memory footprint and ensure the interface is strictly typed.
*   **Confidence Score:** 9/10. The logic is well-understood and the scope is narrow enough to test thoroughly.