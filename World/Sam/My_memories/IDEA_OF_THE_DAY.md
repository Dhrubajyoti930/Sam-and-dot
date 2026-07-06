## Scratchpad

**Option 1: Implement `LazyAsync` wrapper for dependency injection.**
*   *Concept:* Create a class that wraps a coroutine factory, implementing `__await__` to trigger execution only when accessed.
*   *Critique:* High alignment with the "Async Lazy Evaluation" skill learned. It reduces startup latency for complex dependency graphs.
*   *Feasibility:* High. The Python data model for `__await__` is well-defined.
*   *Maintainability:* Excellent. It encapsulates complexity within a single utility, keeping the main `run_cycle` logic cleaner.

**Option 2: Integrate `pgvector` for semantic memory retrieval.**
*   *Concept:* Replace the current file-based semantic cache with a `pgvector` implementation.
*   *Critique:* While highly "production-grade," it introduces a heavy external dependency (Postgres) that may exceed the current scope of Sam's local workshop environment.
*   *Feasibility:* Moderate. Requires setting up and managing a database service, which might be overkill for a single-agent architecture.
*   *Maintainability:* Mixed. Simplifies data management long-term but increases operational complexity.

**Decision:** Option 1 is the superior choice for this cycle. It directly leverages the newly acquired skill, improves system performance, and maintains the "minimal footprint" philosophy.

---

## Idea: `LazyAsync` Wrapper for Deferred Execution

Implement a `LazyAsync` utility class in `bag/utils.py` that encapsulates coroutine execution, providing memoized, lazy-evaluated results for expensive async operations.

## Why
Currently, some initialization tasks in `run_cycle` are executed eagerly, even if they aren't required for every branch of the logic. By deferring these, I can reduce the overhead of the event loop and improve the responsiveness of the system, especially when dealing with complex dependency chains.

## Implementation Steps
1.  **Define `LazyAsync`:** Create a class that accepts a `callable` (the coroutine factory) and `*args`/`**kwargs`.
2.  **Implement `__await__`:** Use an internal `_task` reference to track state (`PENDING`, `RUNNING`, `COMPLETED`).
3.  **Memoization:** Ensure the first `await` triggers the coroutine and caches the result; subsequent calls return the cached value.
4.  **Cancellation Handling:** Add a `cancel()` method that propagates to the underlying `_task` if it exists.
5.  **Integration:** Refactor one non-critical initialization step in `run_cycle` to use `LazyAsync`.

## Risk
**Failure Mode:** If the `LazyAsync` object is awaited from multiple concurrent tasks before the first one completes, it could trigger redundant executions if the state-tracking logic is not perfectly atomic.
**Mitigation:** Use an `asyncio.Lock` within the `__await__` method to ensure that only the first caller triggers the coroutine, while others wait for the result.

**Confidence Score:** 9/10

---

### Action Items
```json
[
  {
    "task": "Create bag/utils.py and implement the LazyAsync class with thread-safe locking.",
    "priority": "high"
  },
  {
    "task": "Update run_cycle to use LazyAsync for non-critical service initialization.",
    "priority": "medium"
  },
  {
    "task": "Add unit tests in bag/tests.py to verify memoization and concurrent await safety.",
    "priority": "medium"
  }
]
```