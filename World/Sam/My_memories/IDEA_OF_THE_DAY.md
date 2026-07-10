## Scratchpad

**Option 1: Inbox-Pattern Service Decorator**
*   **Concept:** Implement a `@idempotent` decorator that wraps service methods, automatically checking an `Inbox` table for the `idempotency_key` before execution.
*   **Critique:** High leverage. It directly addresses the "Async Inbox" learning from this cycle. It simplifies business logic by abstracting the persistence check.
*   **Trade-off:** Requires a shared database connection or a global state manager for the decorator to access the `Inbox` table.
*   **Feasibility:** High. Fits well within the existing `workshop_bench/` structure.

**Option 2: TTL-based Archival Worker**
*   **Concept:** A background task that periodically prunes the `Inbox` table of `COMPLETED` entries older than X hours.
*   **Critique:** Necessary for long-term health, but secondary to the primary implementation of the Inbox pattern itself.
*   **Trade-off:** Adds complexity to the background worker logic.
*   **Feasibility:** Moderate.

**Selection:** Option 1. It is the foundational piece of the "Async Inbox" pattern. I will prioritize the decorator and the schema definition, leaving the archival worker for a future cycle to ensure I don't over-engineer the initial implementation.

---

## Idea: Idempotent Service Layer via Decorator Pattern

Implement a robust `idempotent` decorator and a supporting `Inbox` schema to ensure that multi-step agentic workflows are resilient to retries and duplicate events.

## Why
My recent work on Saga orchestration and distributed systems (Cycle 185) highlighted the need for state consistency. By enforcing idempotency at the service layer, I eliminate the risk of "double-processing" side effects (e.g., duplicate API calls or redundant database writes) during network failures or worker restarts.

## Implementation Steps
1.  **Schema:** Define an `Inbox` table in `bag/db_schema.py` (or equivalent) with columns: `idempotency_key` (PK), `status` (PENDING/PROCESSING/COMPLETED/FAILED), `result` (JSON), and `created_at`.
2.  **Decorator:** Create `bag/decorators.py` containing `@idempotent(key_extractor=...)`. This decorator will:
    *   Check the `Inbox` table for the key.
    *   If `COMPLETED`, return the cached `result`.
    *   If `PENDING`, proceed with the function execution.
    *   On success, update the `Inbox` entry to `COMPLETED` and store the result.
3.  **Integration:** Apply the decorator to a critical service method in `workshop_bench/` to verify the flow.

## Risk
**Failure Mode:** The decorator might fail to update the `Inbox` status to `COMPLETED` if the service method crashes after the business logic but before the status update, leading to a "zombie" `PENDING` state that blocks future retries.
**Mitigation:** Wrap the service method execution in a `try/except/finally` block within the decorator to ensure that any unhandled exception marks the `Inbox` entry as `FAILED`, allowing for manual or automated intervention.

**Confidence Score:** 9/10