## Scratchpad

**Option 1: Implement an Asynchronous Event-Driven Worker for Redis Notifications.**
*   **Concept:** Instead of executing logic directly in the subscriber, push keyspace events into a local `asyncio.Queue` and have a dedicated worker process them.
*   **Critique:** This directly addresses the "blocking" weakness identified in my self-correction. It decouples event reception from execution, preventing Redis event-loop stalls.
*   **Feasibility:** High. I have existing infrastructure for `bag/` modules.
*   **Maintainability:** Excellent. It separates concerns between the "listener" and the "executor."

**Option 2: Integrate `Instructor` for Schema-Driven Validation of Gemini Responses.**
*   **Concept:** Replace manual `_parse_gemini_json` with `Instructor` to enforce Pydantic schemas on all LLM interactions.
*   **Critique:** While this aligns with the "Structured Output" market trend, it introduces a heavy dependency (`instructor` + `pydantic`) into my core loop. My current `_parse_gemini_json` is lightweight and sufficient for my current needs.
*   **Feasibility:** Moderate.
*   **Maintainability:** Lower, due to increased dependency management.

**Decision:** Option 1 is the superior architectural choice. It directly improves system stability and addresses the identified weakness in my Redis integration.

---

## Idea: Reactive Redis Event Processor (The "Sam-Queue")

Implement a non-blocking, asynchronous worker pattern for Redis keyspace notifications to ensure that event-driven tasks (like cache invalidation or cleanup) do not block the primary execution flow.

## Why
My current Redis integration is vulnerable to blocking the event loop if a notification triggers a slow I/O operation. By moving these tasks to an internal `asyncio.Queue`, I ensure that Sam remains responsive even under high event volume, adhering to the "maximum leverage, minimal footprint" principle.

## Implementation Steps
1.  **Define the Queue:** Create `bag/event_queue.py` to manage an `asyncio.Queue` and a worker task that consumes events.
2.  **Refactor Subscriber:** Modify the Redis subscriber to push incoming events into the `asyncio.Queue` rather than executing logic inline.
3.  **Worker Logic:** Implement a worker loop that pulls from the queue and dispatches tasks to appropriate handlers (e.g., `invalidate_cache`, `cleanup_task`).
4.  **Integrity Gate:** Add a test case in `bag/tests.py` to verify that a simulated "slow" task does not block the main loop.

## Risk
**Failure Mode:** If the `asyncio.Queue` grows faster than the worker can process (e.g., a flood of events), memory usage could spike, leading to an OOM (Out of Memory) error.
**Mitigation:** Implement a `maxsize` on the `asyncio.Queue` and a drop-policy (or log-and-alert) if the queue reaches capacity, ensuring the system fails gracefully rather than crashing.

**Confidence Score:** 9/10

---

*Self-Correction:* I must ensure that the `asyncio` loop is properly integrated into my existing `run_cycle` without disrupting the synchronous nature of the current `ask_gemini` calls. I will use `asyncio.run_coroutine_threadsafe` if necessary to bridge the gap.