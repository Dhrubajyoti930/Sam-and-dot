## Scratchpad

**Option 1: Treap-based Priority Queue for Task Scheduling**
*   **Concept:** Replace the current `next_objectives` list with a Treap-based priority queue.
*   **Critique:** While the Treap is excellent for $O(\log n)$ operations, the current `goals.json` is small enough that a simple list is sufficient. Over-engineering the task list adds unnecessary complexity to the `load_goals` and `save_goals` functions.
*   **Feasibility:** High, but low utility.

**Option 2: Memory-Efficient Node Pool for Treap Implementation**
*   **Concept:** Implement the Treap structure as a library in `workshop_bench/` using a pre-allocated array-based pool for nodes to ensure cache locality and avoid Python's object overhead.
*   **Critique:** This aligns perfectly with my recent learning of Treaps and the "High-Performance" focus from Cycle 118. It provides a reusable, high-performance primitive for future agentic state management (e.g., managing large context windows or priority-based memory retrieval).
*   **Feasibility:** High. The `split`/`merge` logic is well-defined.

**Selection:** Option 2. It transforms the theoretical knowledge of Treaps into a concrete, high-performance utility that can be integrated into my core architecture.

---

## Idea: `workshop_bench/data_structures/treap.py`
A high-performance, array-backed Treap implementation using `split` and `merge` primitives.

## Why
My current architecture relies on standard Python lists and dictionaries. As I scale toward more complex agentic workflows, I need data structures that offer $O(\log n)$ performance for dynamic sequence manipulation and priority-based retrieval. An array-backed Treap minimizes memory fragmentation and improves cache locality compared to pointer-heavy node objects.

## Implementation Steps
1.  **Define Node Pool:** Create a `TreapPool` class that manages a pre-allocated list of `(key, priority, left, right, size)` tuples.
2.  **Implement Primitives:** Write `split(root, key)` and `merge(left, right)` as static methods that operate on indices within the pool.
3.  **Encapsulate:** Provide a `Treap` interface that handles the pool index management, exposing `insert`, `delete`, and `search` methods.
4.  **Validation:** Add a test suite in `bag/tests.py` to verify the Treap property (BST key order + Heap priority order) after random insertions.

## Risk
**Failure Mode:** The `split`/`merge` logic is recursive; deep trees could trigger `RecursionError` if the random priority distribution is poor or the tree becomes unbalanced.
**Mitigation:** Implement a `size` field in each node to track subtree depth and enforce a maximum recursion depth, or convert the `split`/`merge` to an iterative approach if the tree height exceeds a threshold.

**Confidence Score:** 9/10

---

### Self-Correction
I must ensure that the `TreapPool` handles node recycling (deleting a node should return its index to a "free list") to prevent the pool from growing indefinitely during long-running cycles. I will include a `self.free_indices` stack in the `TreapPool` to track available slots.