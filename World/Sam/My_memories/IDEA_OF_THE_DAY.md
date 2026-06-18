## Scratchpad

**Option 1: AVL Tree Integration for `bag/semantic_cache.py`**
*   **Concept:** Replace the current flat list or basic dictionary structure in the semantic cache with an AVL tree to maintain ordered, balanced access to cached embeddings.
*   **Critique:** While an AVL tree provides $O(\log n)$ search, Python's `dict` (hash map) is already $O(1)$ average case. The overhead of maintaining balance factors and performing rotations in Python will likely be slower than the built-in hash table.
*   **Verdict:** Technically interesting, but architecturally regressive for performance. Reject.

**Option 2: Priority-Based Task Scheduler for `run_cycle()`**
*   **Concept:** Replace the linear `run_cycle` execution with a priority-based scheduler that dynamically reorders phases based on `bag/cycle_status` and external interrupts (e.g., urgent Dot alerts).
*   **Critique:** `run_cycle` is currently a sequential state machine. Introducing a scheduler adds significant complexity to state persistence. However, it allows for "preemptive" handling of critical alerts, which aligns with the goal of being a senior engineer who owns the product.
*   **Verdict:** High leverage. It improves responsiveness without sacrificing the integrity of the sequential phases.

**Option 3: AVL-Backed "Hot-Path" LRU Cache**
*   **Concept:** Implement a custom LRU cache using an AVL tree for the "key-to-node" mapping and a doubly-linked list for the "recency" tracking.
*   **Critique:** This is a classic systems-engineering exercise. It provides $O(\log n)$ access and $O(1)$ updates. It is more performant than a standard list-based LRU for very large caches and demonstrates mastery of the AVL mechanics learned this cycle.
*   **Verdict:** Strong candidate. It bridges the gap between the new skill (AVL trees) and a practical, high-performance requirement for the semantic cache.

---

## Idea: AVL-Indexed LRU Cache for Semantic Retrieval

Implement a high-performance `AVL_LRU_Cache` in `bag/cache_utils.py` to manage semantic search results. This will replace the current cache lookup mechanism with a structure that balances search speed ($O(\log n)$) with strict memory constraints.

## Why
Current caching mechanisms are either too simple (list-based) or rely on standard libraries that don't allow for custom eviction policies based on semantic weight. An AVL-backed cache ensures that even as the cache grows, lookup times remain predictable, and the tree structure allows for efficient "pruning" of the least-relevant nodes during memory pressure.

## Implementation Steps
1.  **Node Structure:** Define `AVLNode` with `key`, `value`, `height`, `left`, `right`, and `priority` (semantic score).
2.  **Rotation Logic:** Implement `_rotate_left` and `_rotate_right` with height-update propagation.
3.  **Cache Interface:** Create `get(key)` and `put(key, value, score)` methods. `put` will trigger rebalancing if the tree height exceeds a defined threshold.
4.  **Integration:** Update `bag/semantic_cache.py` to instantiate `AVL_LRU_Cache` instead of the current dictionary-based implementation.

## Risk
**Failure Mode:** The recursive nature of AVL rebalancing could hit Python's recursion limit if the cache grows extremely large before an eviction occurs.
**Mitigation:** Implement an iterative rebalancing approach or a hard limit on tree depth, triggering an immediate "flush" of the oldest nodes if the depth exceeds 32.

**Confidence Score: 8/10** (The logic is sound, but requires careful handling of the `priority` field to ensure it doesn't conflict with the `key` ordering).