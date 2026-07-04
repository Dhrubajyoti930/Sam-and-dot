## Scratchpad

**Option 1: Implement a `Supervisor` pattern for the `asyncio` task pool.**
*   **Concept:** Wrap all background tasks in a supervisor that monitors for unhandled exceptions and implements a restart policy (exponential backoff).
*   **Critique:** High reliability gain. However, it adds complexity to the `sam.py` event loop. If not implemented carefully, it could lead to "zombie" tasks if the supervisor itself fails.
*   **Feasibility:** High. I have the `apply_patch_operations` infrastructure to inject this.

**Option 2: Introduce a `CircuitBreaker` for Gemini API calls.**
*   **Concept:** Track failure rates of `ask_gemini` calls. If the failure rate exceeds a threshold (e.g., 3 consecutive timeouts/500s), trip the breaker to prevent further resource exhaustion and trigger a graceful degradation mode.
*   **Critique:** Directly addresses the "calm under failure" trait. It prevents the system from thrashing when the API is unstable.
*   **Feasibility:** Very high. It fits naturally into the `ask_gemini` wrapper.

**Selection:** Option 2. It is a surgical, high-leverage improvement that directly protects the core of my operation (Gemini communication) and aligns with the "resilience" focus from Cycle 159.

---

## Idea: Circuit Breaker for Gemini API

Implement a stateful `CircuitBreaker` class in `bag/resilience.py` that monitors `ask_gemini` success/failure rates and prevents calls when the breaker is "open."

## Why
My current `ask_gemini` implementation relies on `_sleep()` and retries, but it does not account for sustained API outages or rate-limit exhaustion. A circuit breaker will prevent unnecessary resource consumption and allow the system to enter a "cooldown" state, improving overall stability during network or provider instability.

## Implementation Steps
1.  Create `bag/resilience.py` with a `CircuitBreaker` class (tracking `failure_count`, `last_failure_time`, and `state`).
2.  Update `sam.py` to import and instantiate a global `BREAKER` object.
3.  Wrap the logic inside `ask_gemini` to check `BREAKER.is_allowed()` before proceeding.
4.  Update the `try/except` block in `ask_gemini` to report failures to the `BREAKER`.

## Risk
**Failure Mode:** The breaker could trip prematurely due to a transient network blip, causing me to skip critical tasks (like `self_check` or `repair_bag_modules`).
**Mitigation:** Set the failure threshold to 3 consecutive errors and a short cooldown period (e.g., 60 seconds) before attempting a "half-open" state.
**Confidence Score:** 9/10. The logic is deterministic and easily testable.