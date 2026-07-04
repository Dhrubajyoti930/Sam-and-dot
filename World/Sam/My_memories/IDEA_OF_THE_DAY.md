## Scratchpad

**Option 1: Implement a `CircuitBreaker` for Gemini API calls.**
*   *Concept:* Wrap `ask_gemini` in a stateful circuit breaker that trips after N consecutive failures, preventing further calls until a cooldown period passes.
*   *Critique:* High value for resilience. However, `sam.py` is already complex. Adding state management here might bloat the core module.
*   *Feasibility:* High. I can use a simple `bag/` file to track state (open/closed/half-open).

**Option 2: Standardize Async Timeouts via a Decorator.**
*   *Concept:* Create a decorator `@with_timeout(seconds=X)` in `bag/utils.py` to replace manual `asyncio.timeout` blocks.
*   *Critique:* Cleaner than manual blocks, but decorators can obscure stack traces in `asyncio` tasks. It aligns perfectly with the "Technical Summary" learned this cycle.
*   *Feasibility:* Very high. It promotes DRY principles and ensures consistent timeout handling across all I/O-bound functions.

**Decision:** Option 2. It directly addresses the "Technical Summary" regarding `asyncio` best practices and improves the maintainability of my asynchronous architecture.

---

## Idea: Standardized Async Timeout Decorator

## Why
Currently, timeout logic is manually implemented in various coroutines. This is error-prone and risks "zombie" tasks if cancellation propagation is handled inconsistently. A centralized decorator ensures that all I/O-bound operations adhere to a uniform latency budget and consistent error handling, reducing technical debt.

## Implementation Steps
1.  Create `bag/async_utils.py` (if it doesn't exist) or add to an existing utility module.
2.  Implement `with_timeout(seconds: float)` decorator using `asyncio.timeout` (Python 3.11+).
3.  Ensure the decorator explicitly catches `asyncio.TimeoutError` and logs the failure before re-raising or returning a default, preventing silent failures.
4.  Apply the decorator to `ask_gemini` and other high-latency network-bound functions.

## Risk
**Failure Mode:** The decorator might interfere with the `self` context of class methods if not implemented with `functools.wraps` and proper `async` signature forwarding.
**Mitigation:** Use `functools.wraps` to preserve metadata and ensure the wrapper is defined as `async def` to correctly handle the awaitable.

**Confidence Score:** 9/10

---

## 1% Metric
*   **Metric:** Successful migration of 3 core I/O-bound functions to the `@with_timeout` decorator, verified by a passing `bag/tests.py` suite.