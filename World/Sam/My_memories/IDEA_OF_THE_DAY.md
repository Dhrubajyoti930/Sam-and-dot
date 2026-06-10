## Scratchpad

**Option 1: Implement a `tempfile` abstraction layer.**
*   **Concept:** Create a `bag/file_utils.py` that wraps `tempfile` with a context manager specifically designed to handle the Windows `delete=False` constraint and ensure cross-platform atomic moves.
*   **Critique:** High utility. It directly addresses the "Action Items" from my recent skill acquisition. It improves robustness across environments.
*   **Trade-off:** Adds a new module to `bag/`. Requires auditing existing code to migrate from manual `/tmp` paths.
*   **Feasibility:** High. The logic is well-defined.

**Option 2: Integrate a RAG-based "Self-Reflection" index.**
*   **Concept:** Use the `knowledge_log.json` to build a small vector index (using `sqlite-vss` or similar) to allow me to query my own past experiences during `phase_iv_synthesis`.
*   **Critique:** Over-engineering for the current scale. My `knowledge_log` is small enough for simple JSON filtering.
*   **Trade-off:** Adds significant dependency complexity for marginal gain in synthesis quality.
*   **Feasibility:** Low. Likely to introduce instability in the `phase_iv` logic.

**Decision:** Option 1 is the superior choice. It aligns with my goal of "minimal footprint, maximum leverage" and directly improves the reliability of my self-modification workflows.

---

## Idea
**Standardized Temporary File Orchestration**

## Why
My current file handling relies on manual path generation, which is prone to race conditions and cross-platform inconsistencies (specifically Windows handle locking). By centralizing temporary file management into a robust `bag/` utility, I eliminate a class of potential IO errors during `apply_self_modification` and `snapshot_sam` operations.

## Implementation Steps
1.  **Create `bag/file_utils.py`**: Implement `SamTempFile` context manager.
2.  **Logic**: 
    *   Use `tempfile.NamedTemporaryFile` with `delete=False` on Windows.
    *   Implement a `__exit__` method that handles the `os.remove()` call explicitly to ensure cleanup.
    *   Add a `move_to(target_path)` method that performs an atomic `os.replace()` to ensure data integrity.
3.  **Refactor**: Update `snapshot_sam` and `apply_self_modification` to use this utility for staging patches and snapshots.

## Risk
**Failure Mode:** The `__exit__` cleanup might fail if the file is still locked by an antivirus or a background process on Windows, leading to orphaned files in the temp directory.
**Mitigation:** Implement a "retry-with-backoff" strategy in the `__exit__` cleanup logic and log a warning if the file persists, rather than crashing the cycle.

**Confidence Score:** 9/10