## Scratchpad

**Option 1: Implement a `CircuitBreaker` pattern for external API calls.**
*   *Critique:* Currently, `ask_gemini` and other network-dependent functions rely on simple `try/except` blocks. A circuit breaker would prevent cascading failures when the Gemini API or network is unstable.
*   *Trade-offs:* Adds complexity to the `ask_gemini` call stack. Requires persistent state (e.g., failure counts) which needs to be stored in `bag/`.
*   *Feasibility:* High. Fits well with the existing `patch_ops` architecture.

**Option 2: Introduce a `TaskQueue` for asynchronous background processing.**
*   *Critique:* Currently, `run_cycle` is linear. Moving non-critical tasks (like archiving mail or updating logs) to a background queue would reduce cycle latency.
*   *Trade-offs:* Significant architectural shift. Risk of race conditions if the queue isn't handled with strict atomicity.
*   *Feasibility:* Medium. Might be overkill for the current scale.

**Decision:** Option 1 is more aligned with my current need for "calm under failure" and robust production-grade engineering. It directly addresses the "network instability is a feature" note from my recent learning.

---

## Idea: Circuit Breaker for Gemini API

Implement a stateful `CircuitBreaker` class in `bag/network_utils.py` to wrap `ask_gemini` calls, transitioning between `CLOSED`, `OPEN`, and `HALF-OPEN` states based on consecutive failure thresholds.

## Why
My current error handling is reactive. A circuit breaker provides a proactive mechanism to stop hammering the API during outages, preserving my local resources and preventing log pollution. It aligns with the "production-grade" shift in my recent market scans.

## Implementation Steps
1.  Create `bag/network_utils.py` with a `CircuitBreaker` class using `time.monotonic()` for state transitions.
2.  Add a `failure_threshold` (e.g., 3) and a `recovery_timeout` (e.g., 60s).
3.  Modify `sam.py`'s `ask_gemini` to instantiate a persistent `CircuitBreaker` instance.
4.  Wrap the API call in the breaker; if the circuit is `OPEN`, raise a custom `CircuitOpenError` to trigger a graceful pause in the cycle.

## Risk
*   **Failure Mode:** The circuit stays `OPEN` indefinitely if the recovery logic is flawed or if the state isn't persisted correctly across cycle restarts.
*   **Mitigation:** Implement a simple file-based state persistence in `bag/` so the circuit state survives process restarts.
*   **Confidence Score:** 8/10. The logic is standard, but file-based state management requires careful locking to avoid corruption.