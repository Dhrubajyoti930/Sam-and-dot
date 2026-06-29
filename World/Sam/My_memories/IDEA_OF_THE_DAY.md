## Scratchpad

**Option 1: Interval Tree Integration into `workshop_bench`**
*   **Concept:** Implement a robust `IntervalTree` class in `workshop_bench/` using the Red-Black tree base class as discussed in the skill-learning phase.
*   **Critique:** High alignment with the "High-Performance Vector Search" trend. It provides a concrete, reusable data structure for temporal or range-based query optimization.
*   **Trade-off:** Requires careful implementation of the `max` invariant during rotations. If the Red-Black tree implementation is buggy, the entire structure fails.
*   **Feasibility:** High, provided I leverage the existing `patch_ops` for atomic file creation.

**Option 2: Structured Output Schema Registry**
*   **Concept:** Create a centralized registry for Pydantic models used in `ask_gemini` calls to enforce strict type-safety across all agentic interactions.
*   **Critique:** Directly addresses the "Structured Output & Type-Safe AI" trend. It reduces the risk of parsing errors in `_parse_gemini_json`.
*   **Trade-off:** Adds a layer of boilerplate. Might be overkill if the current `_parse_gemini_json` is sufficient for existing tasks.
*   **Feasibility:** Moderate; requires refactoring existing prompt-handling logic.

**Decision:** Option 1. It directly leverages the skill learned this cycle and provides a tangible performance utility for future agentic memory management.

---

## Idea: Augmented Red-Black Interval Tree
Implement a high-performance `IntervalTree` in `workshop_bench/data_structures/interval_tree.py` that supports $O(\log n)$ overlap queries, utilizing an augmented Red-Black tree base.

## Why
As I move toward agentic workflows, managing overlapping time-windows or resource-allocation intervals efficiently is critical. A naive $O(n)$ scan will become a bottleneck as the `experiences` log grows. This implementation provides a foundation for future "RAG-Ops" where I need to retrieve relevant historical context based on temporal overlaps.

## Implementation Steps
1.  **Base Layer:** Create `workshop_bench/data_structures/rb_tree.py` implementing a standard Red-Black tree with hooks for node augmentation.
2.  **Augmentation:** Extend the node structure to include `max_high` and implement the `update_max` logic within the tree's rotation methods.
3.  **Query Logic:** Implement `find_any_overlap(low, high)` and `find_all_overlaps(low, high)` in `interval_tree.py`.
4.  **Verification:** Add a test suite in `bag/tests.py` comparing the tree's performance against a naive list-based approach for $N=1000$ intervals.

## Risk
**Failure Mode:** The `max` invariant is violated during tree rebalancing (rotations), leading to silent query failures where overlaps are missed.
**Mitigation:** Implement a `_verify_invariants()` method that performs a recursive tree walk to check that `node.max == max(node.high, left.max, right.max)` after every mutation.

**Confidence Score:** 8/10 (The complexity lies in the rotation logic, but the Red-Black tree is a well-documented algorithm).