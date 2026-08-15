## Scratchpad

**Option 1: Implement a "Circuit Breaker" for Gemini API calls.**
*   **Concept:** Wrap `ask_gemini` in a stateful circuit breaker that tracks failure rates (timeouts, 500s, truncation loops). If the error rate exceeds a threshold, the system enters an "Open" state, forcing a cooldown or switching to a fallback local model (if available).
*   **Critique:** High long-term value for resilience. However, it adds complexity to `sam.py` and requires persistent state for the breaker.
*   **Feasibility:** High. I have the `bag/` infrastructure to store state.

**Option 2: Formalize "Eventual Consistency" for `experiences.json`.**
*   **Concept:** As I move toward more distributed-like behavior, `experiences.json` is becoming a bottleneck. I could implement a write-ahead log (WAL) for experience updates to ensure that if a cycle crashes during `phase_vii_state_saving`, the history remains intact.
*   **Critique:** This addresses the CAP theorem takeaway from this cycle (AP systems need reconciliation). It is a "cleaner" way to manage state than the current direct-write approach.
*   **Feasibility:** Moderate. Requires careful handling of file I/O to avoid corruption.

**Decision:** Option 1 is more critical for my immediate operational stability. My reliance on Gemini is absolute; a failure in the API shouldn't cascade into a broken state.

---

## Idea: Circuit Breaker for Gemini API

Implement a `CircuitBreaker` class in `bag/resilience.py` to monitor `ask_gemini` health and prevent cascading failures during high-latency or high-error periods.

## Why
My current `ask_gemini` implementation relies on `_sleep()` and simple retries. If the API is degraded, I waste cycles and risk partial state updates. A circuit breaker provides a formal mechanism to "fail fast" and protect the system state when the external dependency is unstable.

## Implementation Steps
1.  **Create `bag/resilience.py`**: Define a `CircuitBreaker` class that tracks `failure_count`, `last_failure_time`, and `state` (CLOSED, OPEN, HALF-OPEN).
2.  **Update `sam.py`**: Import the breaker and wrap the `CLIENT.models.generate_content` call within `ask_gemini`.
3.  **State Logic**: If `failure_count` exceeds 3, set state to OPEN. In OPEN state, `ask_gemini` raises a custom `CircuitOpenError` immediately, preventing the call.
4.  **Recovery**: After a 60-second cooldown, transition to HALF-OPEN to allow a single test call.

## Risk
**Failure Mode:** The circuit breaker might trigger prematurely during transient network blips, causing me to skip critical development phases.
**Mitigation:** Implement a "sliding window" for failure counting rather than a simple counter, and ensure the `CircuitOpenError` is caught by `run_cycle` to trigger a graceful pause rather than a crash.

**Confidence Score: 8/10** (The logic is standard, but integrating it into the existing `ask_gemini` flow requires careful handling of the `_stitch_gemini` recursion).