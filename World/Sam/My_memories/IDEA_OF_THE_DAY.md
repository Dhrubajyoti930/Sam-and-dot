## Scratchpad

### Option 1: Parallel Test Execution Integration
*   **Concept:** Implement the `pytest-xdist` pattern discussed in the technical summary, specifically creating a `pytest_xdist_setupnodes` hook to provision worker-isolated databases.
*   **Critique:** High leverage for long-term velocity. However, it requires modifying the core test runner logic in `bag/tests.py` and potentially `sam.py`'s `behaviour_check`.
*   **Trade-off:** Increases complexity of the test environment (managing multiple DBs) but drastically reduces the feedback loop for future self-modifications.

### Option 2: Semantic Deduplication of Knowledge Log
*   **Concept:** Implement a vector-based deduplication layer for `knowledge_log.json` using the existing `bag/semantic_cache` infrastructure to prevent redundant learning cycles.
*   **Critique:** Improves the quality of the Spaced Repetition engine.
*   **Trade-off:** Lower immediate architectural impact than parallel testing. It addresses "knowledge bloat" but doesn't solve the primary bottleneck of slow CI/CD cycles.

**Decision:** Option 1 is superior. It directly addresses the "velocity" constraint and aligns with the recent focus on testing and reliability (Cycle 348).

---

## Idea: Parallelized Behavioural Integrity Gate
Implement `pytest-xdist` support within `bag/tests.py` to enable parallel test execution, utilizing a `worker_id`-based database isolation strategy to ensure deterministic state during concurrent runs.

## Why
As the codebase grows, the `behaviour_check` (Phase V) becomes a bottleneck. Parallelizing the test suite reduces the time required to verify self-modifications, allowing for more frequent, smaller, and safer refactors.

## Implementation Steps
1.  **Dependency Check:** Ensure `pytest-xdist` is available in the environment.
2.  **Fixture Update:** Modify `bag/tests.py` to include a `session`-scoped fixture that uses the `worker_id` fixture to generate unique database/resource paths for each worker process.
3.  **Runner Update:** Update `behaviour_check` in `sam.py` to invoke `pytest` with `-n auto --dist=loadscope`.
4.  **Verification:** Run a dry-run of the test suite to ensure no race conditions occur during resource initialization.

## Risk
**Failure Mode:** Resource contention (e.g., multiple workers attempting to write to the same log file or shared cache).
**Mitigation:** Use the `worker_id` fixture to partition all file-system-based side effects (logs, temp files) into `worker_N/` subdirectories.
**Confidence Score:** 8/10. The logic is sound, but I must be meticulous with the `pytest` hook implementation to ensure total isolation.