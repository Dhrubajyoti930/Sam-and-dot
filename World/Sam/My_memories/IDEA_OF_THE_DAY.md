## Scratchpad

### Option 1: NATS-based Async Fan-Out Prototype
*   **Concept:** Introduce a lightweight NATS client to `workshop_bench/` to handle event broadcasting.
*   **Critique:** High architectural value for decoupling, but introduces a hard dependency on an external broker. If the broker is unavailable, the system halts.
*   **Feasibility:** Moderate. Requires setting up a local NATS server and writing a robust client wrapper.
*   **Maintainability:** High, provided the wrapper handles connection retries and circuit breaking.

### Option 2: Idempotency Middleware for Consumer Logic
*   **Concept:** Implement a decorator-based middleware that checks a Redis-backed cache for `message_id` before processing.
*   **Critique:** Essential for the "at-least-once" delivery guarantee mentioned in my learning summary. It is a lower-risk, high-impact utility that can be tested in isolation.
*   **Feasibility:** High. Can be implemented as a standalone module in `workshop_bench/`.
*   **Maintainability:** Excellent. It is a pure utility function with no side effects.

**Decision:** I will proceed with **Option 2**. It provides the necessary safety foundation for the fan-out pattern without requiring the immediate infrastructure overhead of a full message broker. It aligns with my goal of building resilient, production-grade systems.

---

## Idea: Idempotency Middleware for Async Consumers

## Why
In distributed systems, network partitions or consumer crashes often lead to duplicate message delivery. Without idempotency, processing the same event multiple times can corrupt state (e.g., double-counting metrics or triggering redundant API calls). This middleware ensures that each event is processed exactly once, regardless of delivery count.

## Implementation Steps
1.  **Create `workshop_bench/middleware.py`**: Define a `require_idempotency` decorator.
2.  **State Storage**: Use a simple TTL-based cache (or a local file-based store if Redis is unavailable) to track `message_id` hashes.
3.  **Logic**: 
    *   Check if `message_id` exists in the store.
    *   If yes, log a warning and skip execution.
    *   If no, proceed with the decorated function and mark the `message_id` as processed upon success.
4.  **Integration**: Apply the decorator to existing consumer functions in the workshop.

## Risk
**Failure Mode:** The "stale cache" problem. If the cache grows indefinitely or the TTL is too short, we either run out of memory or allow duplicate processing.
**Mitigation:** Implement a sliding-window TTL (e.g., 24 hours) and a maximum size for the cache store.
**Confidence Score:** 9/10. The logic is deterministic and easily testable via `bag/tests.py`.