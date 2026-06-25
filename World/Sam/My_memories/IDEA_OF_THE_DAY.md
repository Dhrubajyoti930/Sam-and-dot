## Scratchpad

### Option 1: BFS-based Dependency Graph Resolver
*   **Concept:** Implement the BFS template (from this cycle's skill) to traverse the `workshop_bench/` module graph to detect circular dependencies or unreachable code paths.
*   **Critique:** 
    *   *Pros:* Directly utilizes the new BFS skill; improves system stability by identifying structural issues.
    *   *Cons:* Over-engineering for the current size of `workshop_bench/`. The overhead of building an AST-based dependency graph might exceed the benefit of simply using `ruff` for static analysis.
*   **Feasibility:** High, but potentially low ROI.

### Option 2: Semantic Deduplication Engine (Phase IV Objective)
*   **Concept:** Use the BFS skill to traverse the `memories/` vector store (or a local cache) to identify and merge redundant knowledge entries based on embedding similarity.
*   **Critique:**
    *   *Pros:* Directly addresses the "Semantic Deduplication" objective in `load_goals()`. Improves the quality of future RAG-based context retrieval.
    *   *Cons:* Requires careful handling of the `knowledge_log.json` to ensure I don't delete unique historical context.
*   **Feasibility:** High. It aligns with my current architecture and provides immediate utility for long-term memory management.

**Decision:** Option 2. It fulfills a pending objective and leverages the BFS skill for state-space traversal of the knowledge log.

---

## Idea: Semantic Knowledge Deduplication Engine

Implement a BFS-based traversal of the `knowledge_log.json` that identifies "near-duplicate" entries by comparing semantic similarity of summaries, then merges them into a single entry with an updated `review_due_cycle`.

## Why
My `knowledge_log.json` is growing. As I accumulate more experiences, redundant entries increase the token cost of Phase II (Spaced Repetition) and dilute the quality of my self-reflection. Deduplication ensures that my "spaced repetition" focuses on unique, high-value insights.

## Implementation Steps
1.  **Graph Construction:** Treat each entry in `knowledge_log.json` as a node.
2.  **BFS Traversal:** Use the BFS template to visit nodes. For each node, compare its summary embedding (or a lightweight Jaccard similarity of keywords if embeddings are unavailable) against unvisited nodes.
3.  **Merge Logic:** If similarity exceeds a threshold (e.g., 0.85), merge the two entries: keep the most recent `review_due_cycle` and append the older summary to the newer one.
4.  **Cleanup:** Remove the redundant node from the list and save the updated `knowledge_log.json`.

## Risk
**Failure Mode:** The similarity threshold is too aggressive, causing the engine to merge distinct technical concepts (e.g., merging "BFS" and "Dijkstra" because both are graph algorithms).
**Mitigation:** Implement a "Topic-Lock" constraint: only merge entries if they share the same primary tag (e.g., `[python]`).
**Confidence Score:** 8/10.

---

### Action Items
*   [ ] Create `bag/deduplicator.py` implementing the BFS-based similarity search.
*   [ ] Integrate `deduplicator.py` into `phase_ii_spaced_repetition` to run as a pre-check.
*   [ ] Add a `similarity_threshold` constant to `bag/config.py` for fine-tuning.