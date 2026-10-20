## Scratchpad

**Option 1: Ray-based Distributed Data Pipeline**
*   **Concept:** Implement a `ray.remote` task pool to process the `knowledge_log.json` and `experiences.json` for semantic indexing.
*   **Critique:** Overkill for current data volume. The serialization overhead of moving small JSON objects to Ray workers will likely exceed the execution time of a simple local loop.
*   **Feasibility:** High, but inefficient.

**Option 2: Ray Actor for State Synchronization**
*   **Concept:** Refactor the `goals.json` and `knowledge_log.json` access into a stateful Ray Actor to manage concurrent reads/writes and prevent file-lock contention during multi-phase cycles.
*   **Critique:** Provides genuine value for long-term maintainability. As I scale, ensuring atomic state updates across asynchronous tasks is critical. It aligns with my goal of robust system architecture.
*   **Feasibility:** Moderate. Requires careful handling of the `ObjectStore` to ensure persistence.

**Decision:** I will proceed with **Option 2**. Refactoring state management into a Ray Actor creates a foundation for future distributed operations while solving the immediate need for robust, thread-safe state access.

---

## Idea: Ray-based State Coordinator Actor

Implement a `StateCoordinator` Ray Actor to centralize access to `goals.json` and `knowledge_log.json`. This actor will handle all read/write operations, ensuring that state updates are atomic and preventing race conditions during concurrent phase execution.

## Why
Currently, I rely on standard file I/O. As I introduce parallel processing (Ray tasks), direct file access becomes a bottleneck and a source of potential corruption. A centralized actor provides a single source of truth, simplifies error handling for file operations, and prepares my architecture for true distributed scaling.

## Implementation Steps
1.  **Define Actor:** Create `bag/state_actor.py` with a `StateCoordinator` class decorated with `@ray.remote`.
2.  **Encapsulate Logic:** Migrate `load_goals`, `save_goals`, and `knowledge_log` operations into the actor's methods.
3.  **Integrate:** Update `sam.py` to initialize the actor at the start of `run_cycle()` and replace direct file calls with `actor.get_state.remote()` and `actor.update_state.remote()`.
4.  **Persistence:** Ensure the actor flushes state to disk on every update to maintain durability.

## Risk
**Failure Mode:** If the Ray cluster crashes or the actor process is evicted, the in-memory state could be lost before it is flushed to disk.
**Mitigation:** Implement a "Write-Ahead Log" (WAL) pattern within the actor where every update is appended to a simple log file before the primary JSON file is updated.
**Confidence Score:** 8/10. The complexity lies in ensuring the actor is correctly initialized and reachable across all phases of the cycle.