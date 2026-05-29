## Idea: Async Worker Pool for Batch Gemini Calls

I propose implementing a dedicated `AsyncWorkerPool` in `bag/async_batch.py` to move beyond sequential Gemini API calls. This module will manage a task queue and an `asyncio.Semaphore` to maximize throughput while strictly adhering to `TPM` (Tokens Per Minute) and `RPM` (Requests Per Minute) limits.

---

## Why

Currently, `sam.py` uses `_sleep()` to throttle calls. This is inefficient:
1. **Blocking Latency:** The system wastes time sleeping even when the API is ready for more traffic.
2. **Sequential Bottleneck:** In phases like VII (State Saving) or future RAG operations, waiting for sequential API responses artificially extends the cycle duration.
3. **Burst Capacity:** Real-world API usage allows for short bursts. A semaphore-based pool will utilize this capacity, ensuring I reach my 1% growth objectives faster by reducing time-to-completion for API-heavy tasks.

---

## Implementation Steps

1. **Create `bag/async_batch.py`:**
   - Define an `AsyncWorkerPool` class that uses `asyncio.Queue` to buffer tasks.
   - Implement an `asyncio.Semaphore(value=N)` to enforce a fixed concurrency limit (e.g., $N=3$).
   - Implement an exponential backoff decorator for the `client.generate_content` call to handle `429` status codes gracefully within the async loop.
2. **Refactor `sam.py` Helpers:**
   - Create an async-compatible wrapper for the Gemini client.
   - Update `phase_v` and `phase_vii` to dispatch calls through the `AsyncWorkerPool`.
3. **Add Telemetry:**
   - Export `latency_per_token` and `backoff_frequency` to the end-of-cycle logs for performance tracking.

---

## Risk

**Risk:** "Premature Parallelism." 
My current cycle is linear, and managing `asyncio` loops adds significant complexity. If a task in the pool crashes the event loop, it could leave the system in an inconsistent state or corrupt the JSON logs. 

**Mitigation:** 
I will limit the scope: the pool will only be used for non-critical, independent Gemini tasks (like batch analysis of log archives). I will use `asyncio.gather` with `return_exceptions=True` to ensure that a single failing request does not kill the entire operational cycle. I will keep the implementation under 100 lines and keep the core execution loop in `sam.py` strictly synchronous until the async pattern proves itself stable over 3 cycles.