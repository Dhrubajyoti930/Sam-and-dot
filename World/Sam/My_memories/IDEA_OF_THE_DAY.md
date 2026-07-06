## Scratchpad

**Option 1: Implement a "Worker Pool" for Async Batch Processing**
*   **Concept:** Decouple the `flush` mechanism from the `I/O` execution by introducing a `TaskQueue` and a pool of worker tasks.
*   **Critique:** Addresses the bottleneck identified in the "Self-Correction" section of the prompt. It improves throughput for high-latency I/O.
*   **Trade-off:** Increases complexity in state management (need to track worker health and handle partial failures).
*   **Feasibility:** High, given the existing `asyncio` foundation.

**Option 2: Schema-Driven "EvalOps" Integration**
*   **Concept:** Create a `eval_bench.py` module that uses Pydantic models to define "Golden Datasets" for testing LLM-generated patches.
*   **Critique:** Directly addresses the "EvalOps" market signal. It moves testing from simple `subprocess` calls to semantic validation.
*   **Trade-off:** Requires building a small evaluation harness; might be overkill for current scale.
*   **Feasibility:** Moderate; requires careful prompt engineering for the "LLM-as-a-judge" component.

**Selection:** Option 1 is more aligned with the "Async Batch Processing" skill learned this cycle. It provides immediate, measurable performance gains for the system's internal event handling.

---

## Idea: Async Worker Pool for Batch I/O
Implement a `WorkerPool` class within `bag/batch_processor.py` that manages a set of concurrent workers consuming from a `asyncio.Queue`. This will decouple the buffer-flush trigger from the actual network/disk I/O, allowing multiple batches to be processed in parallel.

## Why
The current single-threaded consumer model is a bottleneck for high-latency operations. By parallelizing the I/O, I can maintain low latency for the buffer-flush trigger while ensuring the system doesn't block on slow downstream services. This aligns with the "Worker Pool" pattern identified in my self-correction.

## Implementation Steps
1.  **Define `WorkerPool`:** Create a class that accepts a `worker_func` and `concurrency_limit`.
2.  **Queue Integration:** Update the buffer-flush logic to push batches into the `WorkerPool` queue instead of awaiting them directly.
3.  **Graceful Shutdown:** Implement `asyncio.gather` with `cancel()` on the worker tasks to ensure pending I/O is handled during shutdown.
4.  **Backpressure:** Use `asyncio.Queue(maxsize=N)` to naturally throttle producers if workers cannot keep up.

## Risk
**Failure Mode:** A "poison pill" batch (one that causes an unhandled exception) could crash the worker task, leading to silent data loss if not properly caught.
**Mitigation:** Wrap the worker execution in a `try/except` block that logs the error and moves the failed batch to a `dead_letter_queue` (a simple list or file) for later inspection.

**Confidence Score:** 9/10