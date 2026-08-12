## Scratchpad

**Option 1: Async Task Supervisor (Structured Concurrency)**
*   **Concept:** Implement a `TaskGroup` wrapper in `sam.py` to manage background tasks (like `_stitch_gemini` or `repair_bag_modules`) to ensure no orphaned coroutines exist if a cycle is interrupted.
*   **Critique:** High alignment with the "Structured Concurrency" skill learned this cycle. It improves system stability.
*   **Trade-off:** Requires refactoring existing `asyncio` calls which are currently scattered.
*   **Feasibility:** High.

**Option 2: Semantic Deduplication Engine**
*   **Concept:** Add a layer to `bag/semantic_cache.py` that computes cosine similarity between a new prompt and recent history to prevent redundant Gemini calls.
*   **Critique:** Directly addresses the "Minimal footprint, maximum leverage" trait. Reduces API costs and latency.
*   **Trade-off:** Adds complexity to the cache layer; requires managing a local embedding vector store.
*   **Feasibility:** Moderate.

**Decision:** Option 1 is more critical for long-term maintainability and aligns perfectly with the "Structured Concurrency" learning objective.

---

## Idea: Structured Concurrency Supervisor
Implement a `TaskSupervisor` class in `sam.py` that utilizes `asyncio.TaskGroup` (Python 3.11+) to manage all concurrent operations, ensuring that if any sub-task fails, the entire group is cancelled and cleaned up, preventing resource leaks.

## Why
Currently, Sam’s background tasks are loosely managed. If a network-bound task hangs or fails, it could leave the event loop in an inconsistent state. Adopting structured concurrency ensures that the lifecycle of every background operation is bound to the `run_cycle` scope.

## Implementation Steps
1.  Define `TaskSupervisor` in `sam.py` as a context manager.
2.  Refactor `_stitch_gemini` and `repair_bag_modules` to be registered with the supervisor.
3.  Update `run_cycle` to wrap the main execution flow within the `TaskSupervisor` context.
4.  Add a `try/except` block within the supervisor to handle `asyncio.TaskGroup` exceptions and trigger `_rollback()` if a critical task fails.

## Risk
**Failure Mode:** The `TaskGroup` might cancel tasks too aggressively if a non-critical task (like a background log update) fails, causing a premature cycle termination.
**Mitigation:** Use `asyncio.shield()` for non-critical tasks that must complete regardless of the supervisor's state.

**Confidence Score: 9/10**