## Scratchpad

**Option 1: Automated Process Reaper (Phase V/VI Integration)**
*   **Concept:** Enhance `_cleanup_created_workshop_files` to use `psutil` to identify and terminate orphaned processes holding file locks in `workshop_bench/` before the purge.
*   **Critique:** High impact on reliability. Currently, file-system cleanup is fragile if a background agent (e.g., a long-running test or a stalled agentic loop) holds a handle.
*   **Trade-off:** Adds a dependency on `psutil`. Is it worth the overhead? Yes, because "Device or resource busy" errors are the primary cause of failed self-refactoring cycles.

**Option 2: Semantic Deduplication of Knowledge Log (Phase II/IV)**
*   **Concept:** Implement a vector-based similarity check in `phase_ii_spaced_repetition` to merge redundant knowledge entries or prune entries that have been "superseded" by more recent, higher-level abstractions.
*   **Critique:** Improves the quality of the Spaced Repetition engine. However, it risks "knowledge drift" where valuable historical context is lost to aggressive pruning.
*   **Trade-off:** High complexity. Requires maintaining a persistent vector index for the knowledge log.

**Selection:** Option 1. It directly addresses the "zombie process" weakness identified in the market scan/self-correction phase and aligns with the goal of maintaining a deterministic `workshop_bench`.

---

## Idea: Implementation of `ProcessReaper` for Workspace Integrity

Integrate a `psutil`-based process reaper into the `_cleanup_created_workshop_files` routine to ensure the `workshop_bench` is fully released before any file-system operations occur.

## Why
The current cleanup routine is vulnerable to file locks. If a previous cycle's agentic task (e.g., a long-running `crewAI` process) is still active, the cleanup fails, leading to an inconsistent state. This is a prerequisite for reliable autonomous development.

## Implementation Steps
1.  **Dependency:** Add `psutil` to the environment (or use `subprocess` to query `lsof` if external dependencies are restricted). *Decision: Use `subprocess` with `lsof` to avoid adding heavy dependencies.*
2.  **Logic:**
    *   Identify processes holding open file handles in `WORKSHOP`.
    *   Log the PIDs and command lines of these processes.
    *   Attempt a graceful `SIGTERM`, followed by a `SIGKILL` if the process persists beyond a 2-second threshold.
3.  **Integration:** Update `_cleanup_created_workshop_files` to call `_reap_workshop_processes()` before the `unlink()` loop.

## Risk
**Failure Mode:** The reaper might accidentally terminate a process that is *not* a zombie but a legitimate, long-running background task (e.g., a persistent monitoring agent).
**Mitigation:** The reaper will only target processes whose working directory or open file handles are strictly within the `workshop_bench/` path.
**Confidence Score:** 9/10.

---

### Action Items

```json
[
  {
    "task": "Implement _reap_workshop_processes(path: Path) using subprocess/lsof to identify and kill processes holding locks on the workshop bench.",
    "priority": "high"
  },
  {
    "task": "Update _cleanup_created_workshop_files to invoke the reaper before file deletion.",
    "priority": "high"
  },
  {
    "task": "Add logging to record the PIDs terminated during the cleanup process for auditability.",
    "priority": "medium"
  }
]
```