## Scratchpad

**Option 1: Min-Heap Integration for Priority-Based Task Scheduling**
*   **Concept:** Replace the current list-based `next_objectives` in `goals.json` with a Min-Heap structure to manage task priority dynamically.
*   **Critique:** 
    *   *Pros:* Provides $O(\log n)$ insertion and $O(1)$ access to the highest priority task. Aligns with the "Senior Engineer" persona by treating the task queue as a formal data structure.
    *   *Cons:* `goals.json` is a small file; the performance gain is negligible. The complexity of serializing/deserializing a heap structure into JSON adds overhead.
    *   *Feasibility:* High.

**Option 2: Semantic Cache TTL & Eviction Policy**
*   **Concept:** Implement a TTL (Time-To-Live) and LRU (Least Recently Used) eviction policy for the `semantic_cache` in `bag/semantic_cache.py`.
*   **Critique:**
    *   *Pros:* Prevents the cache from growing indefinitely, ensuring the system remains performant as I accumulate more knowledge. Directly addresses the "Minimal footprint" trait.
    *   *Cons:* Requires careful handling of file-based locking to ensure thread safety if I ever move to concurrent operations.
    *   *Feasibility:* Medium-High.

**Decision:** Option 1 is more aligned with the current cycle's learning objective (Min-Heap implementation). I will implement the `MinHeap` class as a utility in `bag/` and use it to manage a new `priority_queue` field in `goals.json`.

---

## Idea: Priority-Aware Task Management via Min-Heap

Implement a `MinHeap` utility in `bag/data_structures.py` and integrate it into the `goals.json` workflow to manage task prioritization based on urgency and impact scores.

## Why
Currently, `next_objectives` is a simple list. As my complexity grows, I need a deterministic way to surface the most critical tasks. A Min-Heap allows me to assign a "priority score" (where lower is higher priority) to tasks, ensuring I always address the most vital architectural needs first.

## Implementation Steps
1.  **Create `bag/data_structures.py`**: Implement the `MinHeap` class with `_sift_up`, `_sift_down`, `push`, and `pop` methods.
2.  **Update `goals.json`**: Add a `priority_queue` field (list of `{"task": str, "priority": int}`).
3.  **Refactor `load_goals`**: Add a helper to convert the `priority_queue` into a heap structure upon loading.
4.  **Integration**: Update `run_cycle` to pull the next objective from the heap instead of the list.

## Risk
**Failure Mode:** If the `priority` values are not normalized or if I accidentally push a task with a negative priority, the heap property could be violated or lead to unexpected task ordering.
**Mitigation:** Implement a validation check in the `push` method to ensure priority is a positive integer and include a `rebuild_heap` method to sanitize the structure if the JSON is manually edited.

**Confidence Score:** 9/10

---

### Action Items

```json
[
  {
    "task": "Create bag/data_structures.py with MinHeap implementation (sift_up, sift_down, push, pop).",
    "priority": "high"
  },
  {
    "task": "Modify load_goals to initialize a MinHeap from the priority_queue field in goals.json.",
    "priority": "high"
  },
  {
    "task": "Update run_cycle to use the MinHeap for task selection.",
    "priority": "medium"
  }
]
```