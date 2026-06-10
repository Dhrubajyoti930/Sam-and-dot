## Scratchpad

**Option 1: `pathlib` Migration & Performance Audit**
*   **Concept:** Systematically replace all `os.path` and `open()` calls with `pathlib.Path` objects across the entire codebase, while benchmarking against `os.scandir` for high-frequency operations.
*   **Critique:** High maintainability and readability gain. However, it touches many files, increasing the risk of breaking path resolution if not handled with care.
*   **Feasibility:** High. The `pathlib` API is robust and standard.

**Option 2: Agentic Workflow for `bag/` Maintenance**
*   **Concept:** Implement a "Janitor Agent" that uses `pathlib` to scan `workshop_bench/` for orphaned files or stale artifacts and automatically archives them based on a TTL (Time-To-Live) policy.
*   **Critique:** Increases autonomy, but adds complexity to the `bag/` system. Requires careful implementation to avoid deleting files that are still in use.
*   **Feasibility:** Moderate. Requires building a metadata tracking system for file lifecycles.

**Selection:** Option 1 is the superior choice for this cycle. It aligns perfectly with the "Skill learned this cycle" and directly addresses the technical debt identified in the action items. It is a foundational refactor that improves the codebase's long-term health.

---

## Idea: `pathlib` Standardisation & Performance-Aware Refactoring

## Why
The current codebase relies on a mix of `os.path` and `pathlib`. Standardising on `pathlib` improves readability and cross-platform reliability. By explicitly separating "general logic" (using `pathlib`) from "performance-critical loops" (using `os.scandir`), I ensure the system remains both maintainable and performant.

## Implementation Steps
1.  **Audit:** Use `grep` or `rg` to identify all `os.path` and `open()` calls in `sam.py` and `workshop_bench/`.
2.  **Refactor:** Replace `os.path.join` with the `/` operator and `open()` with `Path.read_text()`/`write_text()`.
3.  **Performance Gate:** Identify high-frequency file traversal points (e.g., `archive_mail`, `snapshot_sam`). Ensure these continue to use `os.scandir` or `os.walk` if benchmarks indicate `pathlib.Path.glob` overhead is non-negligible.
4.  **Verification:** Run `self_check()` and `behaviour_check()` to ensure no regressions in file I/O.

## Risk
**Failure Mode:** Incorrect path resolution during the transition (e.g., relative vs. absolute path mismatches).
**Mitigation:** Use `.resolve()` on all base directories at the start of the execution cycle to ensure all subsequent operations are anchored to the correct canonical path.

**Confidence Score:** 9/10