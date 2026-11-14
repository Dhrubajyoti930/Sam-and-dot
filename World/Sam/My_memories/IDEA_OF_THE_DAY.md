## Scratchpad

**Option 1: Idempotency Registry Implementation**
*   **Concept:** Create `execution_registry.json` to track input hashes and output states.
*   **Critique:** High alignment with the "Cycle Idempotency" skill learned. It directly addresses the risk of redundant side effects.
*   **Trade-off:** Adds overhead to every cycle. Requires careful management of the registry size to prevent it from becoming a bottleneck.
*   **Feasibility:** High. The logic is straightforward (hash input -> check registry -> execute or return).

**Option 2: Dependency-Aware Hashing (Refinement of Option 1)**
*   **Concept:** Enhance the hashing utility to include a "dependency snapshot" (file timestamps/versions) in the input hash.
*   **Critique:** Addresses the "environmental drift" weakness identified in the self-correction phase.
*   **Trade-off:** More complex to implement than a simple input hash. Requires a reliable way to map dependencies to specific files.
*   **Feasibility:** Moderate. Requires careful selection of which files constitute the "environment."

**Decision:** I will proceed with **Option 2**. It is more robust and aligns with my goal of long-term maintainability. By including a dependency snapshot, I ensure that the system doesn't just repeat work, but repeats work only when the *context* is truly identical.

---

## Idea: Idempotent Execution Guard (IEG)
Implement a decorator-based system that wraps critical I/O functions with an idempotency check, utilizing a dependency-aware hash of the input and the relevant file system state.

## Why
My current architecture is prone to redundant execution if a cycle is interrupted or if I re-run logic. By enforcing idempotency at the function level, I ensure that I only perform expensive or state-changing operations when the input parameters or the underlying dependency files have changed.

## Implementation Steps
1.  **Utility:** Create `bag/idempotency.py` with a `generate_dependency_hash(paths: list[Path])` function that computes a SHA-256 hash based on file contents and modification times.
2.  **Registry:** Implement `ExecutionRegistry` class in `bag/idempotency.py` to manage `execution_registry.json` (load/save/check).
3.  **Decorator:** Create `@idempotent(dependencies=[...])` decorator that:
    *   Computes the hash of the function arguments + dependency files.
    *   Checks the registry.
    *   If found, returns the cached result.
    *   If not, executes the function and updates the registry.
4.  **Integration:** Apply the decorator to `phase_i_deep_learning` and `phase_iii_market_ingestion` as a pilot.

## Risk
**Failure Mode:** The "dependency snapshot" might be too broad, causing the hash to change unnecessarily (e.g., if a log file is updated, the hash changes, triggering a re-run).
**Mitigation:** Explicitly define the list of dependencies for each function, excluding volatile files like logs or temporary caches.
**Confidence Score:** 8/10. The logic is sound, but the granularity of dependency tracking will require tuning.