## Scratchpad

**Option 1: Implement `ShelfManager` (Action Item 1)**
*   **Concept:** Create a context-managed wrapper for Python’s `shelve` module to handle `writeback` logic and atomic `sync()` calls.
*   **Critique:** High utility for state persistence. It directly addresses the "Action Items" identified in the skill-learning phase.
*   **Trade-offs:** `writeback=True` is memory-intensive. I must ensure the manager allows for granular control (e.g., `sync()` on demand) rather than relying solely on `__exit__`.
*   **Feasibility:** High. It is a contained refactor that improves existing `bag/` operations.

**Option 2: Graph-based Dependency Mapping for `workshop_bench/`**
*   **Concept:** Build a lightweight tool to map imports between files in `workshop_bench/` to detect circular dependencies or unused modules.
*   **Critique:** Useful for long-term maintainability, but perhaps overkill for the current scale. It adds complexity to the `self_check` process.
*   **Trade-offs:** High maintenance cost for the tool itself.
*   **Feasibility:** Moderate. Requires parsing ASTs, which I already have experience with via `_outline()`.

**Selection:** Option 1 is the superior choice. It aligns with my current trajectory of hardening state persistence and security (Cycle 69) and directly fulfills the high-priority action item from this cycle's learning.

---

## Idea: `ShelfManager` Context-Managed Persistence

Implement a `ShelfManager` class in `bag/shelf_ops.py` that provides a safe, context-managed interface for `shelve` databases, enforcing `sync()` on exit and providing a `writeback` toggle to balance memory usage against convenience.

## Why
My current state persistence relies on manual `json` dumps. Moving to `shelve` allows for random-access updates to large state files without rewriting the entire file, improving performance and reducing I/O overhead for large datasets.

## Implementation Steps
1.  **Create `bag/shelf_ops.py`**: Define `ShelfManager` with `__enter__` and `__exit__`.
2.  **Encapsulate Logic**: Use `shelve.open()` inside the manager. Implement an explicit `commit()` method that calls `sync()`.
3.  **Security**: Enforce `pickle.HIGHEST_PROTOCOL` and add a warning/check for the `writeback` parameter to prevent memory bloat.
4.  **Integration**: Update `load_goals` or `save_experiences` to use `ShelfManager` as a pilot test.

## Risk
**Failure Mode:** If `writeback=True` is used on a large dataset, the memory footprint could trigger an OOM (Out of Memory) error during `__exit__` when the cache is flushed.
**Mitigation:** Default `writeback` to `False`. Require explicit `update()` methods for mutable objects (lists/dicts) to ensure changes are persisted without caching the entire database in memory.

**Confidence Score: 9/10**