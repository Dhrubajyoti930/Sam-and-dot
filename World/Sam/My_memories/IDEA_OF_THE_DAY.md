## Scratchpad

### Option 1: Implement `concurrent.futures` for `phase_iii_market_ingestion`
*   **Concept**: Parallelize the market scanner to hit multiple endpoints or perform multi-modal analysis concurrently.
*   **Critique**: While this improves latency, the current market scanner is a single-prompt LLM call. Parallelizing a single LLM call is impossible; I would need to split the "Market Scan" into sub-tasks (e.g., one for frameworks, one for SLMs, etc.).
*   **Trade-off**: Increases complexity of the prompt orchestration for a marginal gain in speed, as the bottleneck is the LLM inference time, not the network request.
*   **Feasibility**: Moderate.

### Option 2: Build a "Self-Healing" Registry for `concurrent.futures`
*   **Concept**: Create a wrapper for `ThreadPoolExecutor` that automatically logs thread-level exceptions to a dedicated `bag/thread_errors.json` and attempts a retry if the error is transient (e.g., network timeout).
*   **Critique**: This directly addresses the "Action Items" from the skill learning session. It improves system robustness without over-engineering the core logic. It aligns with my goal of long-term maintainability.
*   **Trade-off**: Adds a small overhead to task submission, but significantly increases the reliability of background tasks.
*   **Feasibility**: High.

**Decision**: Option 2 is superior. It provides a reusable utility that makes my future concurrent operations safer and more observable, adhering to the "senior engineer" persona.

---

## Idea: `SafeExecutor` Wrapper for `concurrent.futures`

## Why
My current architecture relies on `concurrent.futures` for scaling, but silent thread crashes are a risk to system integrity. A wrapper that enforces error logging and provides a structured way to handle task failures ensures that I don't lose data or state during asynchronous operations.

## Implementation Steps
1.  Create `bag/concurrency_utils.py` containing a `SafeExecutor` class.
2.  Implement a `submit_with_retry` method that wraps `executor.submit` with a `try/except` block.
3.  Log failures to `bag/thread_errors.json` with a timestamp and the traceback.
4.  Update `sam.py` to use `SafeExecutor` for any future I/O-bound tasks.

## Risk
**Failure Mode**: The `SafeExecutor` might mask exceptions that should actually trigger a full system halt (e.g., critical configuration errors).
**Mitigation**: Implement a "critical" flag in the `submit` method; if `critical=True`, the wrapper will re-raise the exception after logging, allowing the main process to catch it and trigger a rollback.

**Confidence Score**: 9/10

---

## Proposed Development Idea

### Idea: `SafeExecutor` Pattern for Robust Concurrency
Implement a robust, logging-aware wrapper for `concurrent.futures.ThreadPoolExecutor` to prevent silent thread failures and improve observability of asynchronous tasks.

### Why
As I move toward more complex agentic workflows, I need to ensure that background tasks (like market scanning or log processing) do not fail silently. This pattern provides a foundation for reliable, production-grade concurrency.

### Implementation Steps
1.  **Define `SafeExecutor`**: Create `bag/concurrency_utils.py` with a class that inherits from `ThreadPoolExecutor`.
2.  **Add Error Hook**: Override the internal task submission to wrap the callable in a decorator that catches and logs exceptions to `bag/thread_errors.json`.
3.  **Integrate**: Refactor one existing I/O-bound task (e.g., `_sleep` or a future background log-writer) to use this executor.
4.  **Verification**: Add a test case in `bag/tests.py` that intentionally triggers a thread exception to verify it is caught and logged correctly.

### Risk
**Failure Mode**: The logging mechanism itself could fail (e.g., disk full), causing the wrapper to crash the thread.
**Mitigation**: Wrap the logging call in a bare `try/except` block that prints to `stderr` as a last-resort fallback.

**Confidence Score**: 9/10