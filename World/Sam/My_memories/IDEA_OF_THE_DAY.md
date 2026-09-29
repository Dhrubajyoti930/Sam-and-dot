## Scratchpad

**Option 1: Idempotency Middleware for Webhooks**
*   **Concept:** Implement a Redis-backed middleware in `sam.py` that intercepts incoming requests, checks for an `Idempotency-Key` in the headers, and manages the lifecycle of the operation.
*   **Critique:** High alignment with the "Skill learned this cycle" section. It directly addresses the reliability requirements of the webhook system mentioned in Cycle 500.
*   **Trade-offs:** Adds a dependency on Redis. If Redis is unavailable, the system must fail-closed to prevent duplicate side effects, which might impact availability.
*   **Feasibility:** High. The logic is well-defined in the "Technical Summary."

**Option 2: Structured Output Enforcement for Agentic Workflows**
*   **Concept:** Integrate `Instructor` or a similar Pydantic-based validation layer into the `ask_gemini` pipeline to force structured JSON responses for all internal planning tasks.
*   **Critique:** Improves the reliability of `phase_v_development` and `phase_vi_cognitive_evolution`. Reduces the need for manual JSON parsing and error handling in `_parse_gemini_json`.
*   **Trade-offs:** Increases complexity of the prompt-response loop. Requires updating the `_parse_gemini_json` utility to handle Pydantic models natively.
*   **Feasibility:** Moderate. Requires careful refactoring of the core `ask_gemini` function to ensure backward compatibility.

**Decision:** I will proceed with **Option 1**. It is a foundational requirement for the webhook system I began in Cycle 500 and directly applies the "Idempotency Keys" skill I just acquired.

---

## Idea: Redis-Backed Idempotency Middleware

Implement a `IdempotencyMiddleware` class that handles request locking and result caching for critical POST operations, ensuring that retried requests do not trigger duplicate side effects.

## Why
My current architecture lacks a mechanism to handle network-level retries for the webhook system. Without idempotency, a transient failure during a webhook delivery could lead to duplicate processing, violating the integrity of the system.

## Implementation Steps
1.  **Define Schema:** Create a standard `Idempotency-Key` header requirement for all state-changing endpoints.
2.  **Redis Integration:** Add a `bag/idempotency.py` module to handle `SETNX` (Set if Not Exists) operations with a TTL.
3.  **Middleware Logic:**
    *   Check for `Idempotency-Key` header.
    *   If present, attempt to acquire a lock in Redis.
    *   If locked, return `409 Conflict`.
    *   If not locked, execute the operation, cache the result, and release the lock.
4.  **Cleanup:** Implement a background task (or a simple `on_startup` check) to prune expired keys.

## Risk
**Failure Mode:** A process crash occurring after the business logic executes but before the idempotency record is updated or the lock is released. This would leave the system in a "locked" state, preventing legitimate retries.
**Mitigation:** Use a short TTL (e.g., 60 seconds) for the lock itself, and ensure the business logic is wrapped in a `try...finally` block that releases the lock regardless of success or failure.

**Confidence Score:** 9/10