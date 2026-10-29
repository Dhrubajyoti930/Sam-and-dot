## Scratchpad

**Option 1: Implement a Topic Dependency Graph (TDG) for Knowledge Management.**
*   **Concept:** Replace the current linear `knowledge_log.json` with a DAG-based structure. Nodes represent atomic concepts; edges represent prerequisites.
*   **Critique:** High architectural value. It solves the "knowledge decay" problem by allowing the system to identify missing foundational nodes when a review fails.
*   **Trade-off:** Requires a non-trivial refactor of `phase_ii_spaced_repetition` and a new data schema.
*   **Feasibility:** High. The logic is well-defined (topological sort).

**Option 2: Automated "Confidence Score" Feedback Loop.**
*   **Concept:** Add a `confidence_score` (0.0–1.0) to every node in the TDG. If a review fails, the score drops, triggering a "re-learn" path through the graph.
*   **Critique:** Adds significant complexity to the state management. Might lead to "thrashing" if the model is too sensitive to minor review failures.
*   **Trade-off:** High maintenance overhead for the state-saving logic.
*   **Feasibility:** Moderate.

**Selection:** Option 1 is the superior foundation. It aligns with the "Skill learned this cycle" and provides a structural upgrade to my memory system. I will proceed with the TDG implementation.

---

## Idea: Topological Knowledge Dependency Graph (TKDG)

Implement a Directed Acyclic Graph (DAG) structure for `knowledge_log.json` to manage learning dependencies, replacing the current flat list.

## Why
The current linear log treats all knowledge as independent. In reality, advanced concepts (e.g., Graph-RAG) depend on foundational ones (e.g., Vector Embeddings). A DAG allows me to identify "blocking" prerequisites, ensuring I don't attempt to master high-level abstractions without the necessary foundational context.

## Implementation Steps
1.  **Schema Update:** Define a `TopicNode` JSON schema: `{"id": str, "prerequisites": list[str], "difficulty": float, "mastery": float}`.
2.  **Graph Validation:** Implement `validate_dag()` using Kahn’s algorithm to detect cycles in `bag/graph_ops.py`.
3.  **Traversal Logic:** Update `phase_ii_spaced_repetition` to query the graph for "ready" nodes (prerequisites met) rather than just chronological due dates.
4.  **Transitive Reduction:** Add a utility to prune redundant edges, keeping the graph lean.

## Risk
**Failure Mode:** The graph becomes disconnected or contains circular dependencies due to imprecise node definitions, causing the review engine to stall.
**Mitigation:** Implement a "fallback to linear" mode if the graph validation fails, and enforce strict atomic node granularity.

**Confidence Score:** 8/10

---

### Self-Correction
I initially considered using a graph database, but that introduces an external dependency. I will stick to a JSON-based adjacency list stored in `bag/knowledge_graph.json` to maintain the "minimal footprint" requirement. I must ensure the `phase_ii` logic handles the transition from the old flat list to the new graph structure gracefully.