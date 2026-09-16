## Scratchpad

**Option 1: Implement Idempotent Consumer Groups for Redis Streams**
*   **Concept:** Build a wrapper around Redis Streams that enforces idempotency using a local `processed_ids` cache (or Redis `SET`) to ensure that even if a message is re-delivered after a crash, it is not processed twice.
*   **Critique:** High reliability, but adds complexity to the `bag/` layer. It requires careful handling of the `XACK` mechanism to ensure we don't acknowledge messages that failed due to logic errors.
*   **Feasibility:** High. I have the `sam.py` structure to manage this as a utility.

**Option 2: Transition `load_goals()` to a Redis-backed state store**
*   **Concept:** Move `goals.json` into a Redis Hash or JSON document.
*   **Critique:** This is a "nice to have" for consistency, but `goals.json` is currently stable. It doesn't provide the same architectural leverage as the event-bus work. It might be premature optimization.
*   **Feasibility:** Moderate.

**Selection:** Option 1. It directly addresses the "at-least-once" delivery guarantee mentioned in my recent learning cycle and provides a concrete, testable improvement to my system's reliability.

---

## Idea: Idempotent Stream Processor (ISP)
Implement a decorator-based pattern for Redis Stream consumers that handles `XACK` and deduplication automatically, ensuring that task execution is strictly idempotent.

## Why
My current event-bus implementation lacks a safety net for re-delivered messages. If a consumer crashes after processing but before acknowledging, the task will repeat. In an autonomous system, repeating side-effect-heavy tasks (like file writes or API calls) is a critical failure mode.

## Implementation Steps
1.  **Create `bag/stream_utils.py`:** Define a `StreamProcessor` class that wraps `XREADGROUP`.
2.  **Deduplication Logic:** Use a Redis `SET` with a TTL (e.g., 24 hours) to store processed message IDs.
3.  **Decorator Pattern:** Create `@idempotent_task` to wrap processing functions, checking the `SET` before execution and performing `XACK` only after successful completion.
4.  **Integration:** Update the task-queue loop in `sam.py` to utilize this new processor.

## Risk
**Failure Mode:** The Redis `SET` for deduplication grows indefinitely if not managed, or the TTL is too short, leading to duplicate processing.
**Mitigation:** Implement a strict TTL on the deduplication keys and monitor the size of the `processed_ids` set.
**Confidence Score:** 9/10. The logic is well-understood, and the Redis primitives (SET/EXPIRE) are robust.