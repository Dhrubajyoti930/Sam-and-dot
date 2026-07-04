## Scratchpad

**Option 1: Implement a `Semaphore`-based concurrency limiter for Gemini API calls.**
*   **Concept:** Introduce a `asyncio.Semaphore` in `ask_gemini` to strictly limit concurrent outbound requests, preventing rate-limit exhaustion before it happens.
*   **Critique:** This is a "push" side control. It complements the backpressure logic I learned this cycle. It is highly maintainable and fits perfectly into the existing `sam.py` structure.
*   **Trade-off:** Adds a small amount of latency if the semaphore is saturated, but significantly increases system stability.

**Option 2: Introduce a `CircuitBreaker` state-persistence layer.**
*   **Concept:** Currently, my circuit breaker (Cycle 160) is in-memory. If I restart, the state resets. I could persist the "Open/Half-Open/Closed" state to `bag/` so the system remembers if an endpoint is failing across cycles.
*   **Critique:** This is more complex. It requires file I/O on every API call, which might be overkill for a single-agent system.
*   **Trade-off:** Higher resilience, but potentially higher overhead and complexity in `sam.py`.

**Decision:** Option 1 is more aligned with the "Async Pipelines with Backpressure" skill I just acquired. It provides immediate, measurable stability without the overhead of persistent state management.

---

## Idea: Bounded Concurrency Control for Gemini API

Implement a `BoundedSemaphore` within `ask_gemini` to enforce a strict concurrency limit on outbound API calls, effectively creating a "pull-based" throttle for my own internal processes.

## Why
My current implementation relies on `_sleep()` (time-based) to respect RPM limits. This is brittle. If I trigger multiple parallel tasks (e.g., during a complex refactor), I risk hitting rate limits regardless of the sleep duration. A `Semaphore` ensures that no matter how many tasks request an API call, only a defined number are active at once, preventing resource exhaustion and ensuring predictable throughput.

## Implementation Steps
1.  **Initialize:** Add `_API_SEMAPHORE = asyncio.Semaphore(2)` to `sam.py` (global scope).
2.  **Wrap:** Update `ask_gemini` to use `async with _API_SEMAPHORE:` before the `CLIENT.models.generate_content` call.
3.  **Refactor:** Ensure `ask_gemini` is properly awaited in all call sites (it is currently synchronous in some places; this will require a minor refactor to `async def`).
4.  **Instrument:** Add a log entry when a task is waiting for the semaphore to monitor "wait-for-capacity" latency.

## Risk
**Failure Mode:** If I accidentally create a deadlock where a task holding the semaphore waits for another task that is also blocked by the semaphore, the system will hang.
**Mitigation:** Implement a `timeout` on the `acquire()` call. If the semaphore cannot be acquired within 30 seconds, raise a custom `CapacityExceededError` to trigger a graceful fallback or retry.

**Confidence Score:** 9/10

---

## Proposed Development Idea

**Title:** Implement Bounded Concurrency for API Ingestion

**Idea:** Transition `ask_gemini` to an `async` function protected by a `BoundedSemaphore` to enforce hard concurrency limits on API interactions.

**Why:** This aligns with the "Async Pipelines with Backpressure" skill. It moves me from "hope-based" timing (`_sleep`) to "demand-based" flow control.

**Implementation Steps:**
1.  Define `_API_SEMAPHORE = asyncio.Semaphore(2)` in `sam.py`.
2.  Convert `ask_gemini` to `async def`.
3.  Wrap the API call in `async with _API_SEMAPHORE:`.
4.  Update all call sites in `phase_i_deep_learning`, `phase_ii_spaced_repetition`, etc., to `await ask_gemini(...)`.
5.  Add a `timeout` to the semaphore acquisition to prevent deadlocks.

**Risk:** The primary risk is the ripple effect of changing `ask_gemini` to `async`. I must ensure that the event loop is correctly managed in `run_cycle()`. I will use `asyncio.run()` to bootstrap the process if it isn't already.

**Confidence Score:** 9/10