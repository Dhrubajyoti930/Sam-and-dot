## Scratchpad

**Option 1: Implement an Iterative DFS Graph Traversal Utility**
*   **Concept:** Replace recursive graph traversals in the codebase with an explicit stack-based iterative approach to prevent `RecursionError` on deep structures.
*   **Critique:** High feasibility. Directly addresses the "Technical Summary" learned this cycle. It improves robustness for large-scale graph operations (like dependency resolution or semantic mapping).
*   **Trade-off:** Increases code verbosity compared to recursion. Requires careful management of the `visited` set to avoid memory bloat.

**Option 2: Introduce a "Schema-First" Validation Layer for Agentic Loops**
*   **Concept:** Integrate `Instructor` or similar Pydantic-based validation into the `ask_gemini` pipeline to enforce structured output for all agentic tasks.
*   **Critique:** High impact on reliability. Aligns with the "Structured Output Enforcement" market trend.
*   **Trade-off:** Significant refactoring of existing prompt-handling logic. Might introduce latency overhead due to schema validation.

**Decision:** I will proceed with **Option 1**. It is a surgical, high-leverage refactor that directly applies my newly acquired skill and addresses a known production risk (stack overflow).

---

## Idea
**Refactor Recursive Graph Traversal to Iterative DFS with Path Reconstruction.**

## Why
Recursive DFS is a liability in production-grade systems where graph depth is non-deterministic. By moving to an explicit stack (LIFO) and maintaining a `parentMap`, I ensure memory safety (heap-based) and gain the ability to reconstruct paths, which is essential for debugging agentic decision chains.

## Implementation Steps
1.  **Define Utility:** Create `bag/graph_utils.py` containing an `iterative_dfs(start_node, target_node, graph_provider)` function.
2.  **Stack Management:** Use `collections.deque` as the stack.
3.  **State Tracking:** Implement a `visited` set and a `parent_map` (dictionary) to store the traversal path.
4.  **Integration:** Identify one existing recursive function in `sam.py` or `workshop_bench/` and replace it with the new utility.
5.  **Validation:** Add a unit test in `bag/tests.py` that traverses a linear chain of 15,000 nodes to verify stack safety.

## Risk
**Failure Mode:** The `parent_map` could grow linearly with the number of nodes, potentially causing memory pressure if the graph is massive.
**Mitigation:** Implement a `max_depth` or `max_nodes` constraint in the traversal function to prevent unbounded memory consumption.

**Confidence Score:** 9/10 (The pattern is well-understood; the primary risk is integration friction).