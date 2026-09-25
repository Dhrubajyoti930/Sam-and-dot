## Scratchpad

**Option 1: GraphQL DataLoader Implementation**
*   **Concept:** Implement a `DataLoader` class in `bag/` to batch database queries for nested relationships, specifically targeting the `experiences.json` and `knowledge_log.json` retrieval patterns.
*   **Critique:** High feasibility. It directly addresses the N+1 problem identified in the skill acquisition phase. It improves performance for recursive queries.
*   **Trade-off:** Adds complexity to the data access layer. Requires careful management of the request-scoped cache to avoid stale data.

**Option 2: Schema-Enforced Pydantic Models for `goals.json`**
*   **Concept:** Replace the loose dictionary manipulation in `load_goals()` and `save_goals()` with a strict Pydantic model.
*   **Critique:** High maintainability. It prevents the "corruption" issues mentioned in the `load_goals` docstring by enforcing types at the boundary.
*   **Trade-off:** Requires a migration step for existing `goals.json` files.

**Decision:** Option 1 is more aligned with the "High-Performance" market signal and the specific action items generated this cycle. I will proceed with a `DataLoader` implementation.

---

## Idea: Request-Scoped DataLoader for `bag/` Data Access

Implement a `DataLoader` pattern to batch and cache data lookups, specifically for the `experiences` and `knowledge_log` modules, preventing redundant I/O during recursive synthesis or analysis phases.

## Why
Currently, Sam’s data access is synchronous and file-based. As the `experiences.json` grows, repeated reads during synthesis cycles create unnecessary I/O overhead. By implementing a `DataLoader` that batches requests within a single cycle's execution, I reduce disk contention and prepare the architecture for future migration to a more robust database backend.

## Implementation Steps
1.  **Create `bag/dataloader.py`**: Define a generic `DataLoader` class that accepts a `batch_load_fn` and maintains an internal `cache` dictionary.
2.  **Implement Batching**: Add a `load(key)` method that collects keys and a `load_many(keys)` method that executes the batch operation.
3.  **Integrate with `sam.py`**: Update `load_experiences()` and `load_goals()` to utilize the `DataLoader` instance, ensuring that multiple calls within a single `run_cycle()` hit the cache rather than the disk.
4.  **Lifecycle Management**: Ensure the cache is cleared at the end of `run_cycle()` to maintain data freshness for the next cycle.

## Risk
**Failure Mode:** The cache might persist across cycles if not cleared correctly, leading to "stale" data if `experiences.json` is modified by an external process (though unlikely in this environment).
**Mitigation:** Explicitly clear the `DataLoader` cache at the start of every `run_cycle()` and ensure the `DataLoader` is instantiated within the scope of the cycle.

**Confidence Score: 9/10**