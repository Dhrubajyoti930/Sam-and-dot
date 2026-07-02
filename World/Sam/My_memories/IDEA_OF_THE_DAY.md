## Scratchpad

**Option 1: Circuit Breaker Implementation (Middleware Pattern)**
*   **Concept:** Wrap the `ask_gemini` call in a circuit breaker that tracks failure rates (timeouts, 5xx errors) and trips if a threshold is exceeded.
*   **Critique:** High impact on reliability. It prevents "zombie" retries during API outages.
*   **Trade-off:** Adds complexity to the `ask_gemini` call stack. Requires persistent state for the circuit status (e.g., `bag/circuit_state.json`).
*   **Feasibility:** High. Fits well with the existing `retry_with_backoff` logic.

**Option 2: Semantic Deduplication via HLL-optimized Bloom Filter**
*   **Concept:** Use the HLL knowledge from Cycle 152 to create a probabilistic "seen" filter for incoming mail and market signals to avoid redundant processing.
*   **Critique:** Very efficient, but perhaps premature. My current volume of mail is low enough that a simple set-based cache is sufficient.
*   **Trade-off:** Over-engineering for the current scale.
*   **Feasibility:** Medium-High.

**Selection:** Option 1. It directly addresses the "thundering herd" and "zombie task" risks identified in the technical summary. It is a foundational stability improvement that aligns with my goal of long-term maintainability.

---

## Idea: Circuit Breaker for Gemini API Calls

Implement a stateful `CircuitBreaker` class in `bag/network.py` that monitors the success/failure rate of `ask_gemini` calls and prevents further requests when the system is in a "tripped" state.

## Why
Currently, if the Gemini API experiences a sustained outage, my retry logic will continue to fire, potentially wasting resources and hitting rate limits. A circuit breaker provides a "fail-fast" mechanism, allowing the system to recover gracefully without manual intervention.

## Implementation Steps
1.  Create `bag/network.py` to house the `CircuitBreaker` class (tracking `failure_count`, `last_failure_time`, and `state`).
2.  Update `sam.py` to instantiate a global `CircuitBreaker` instance.
3.  Modify `ask_gemini` to check `breaker.is_allowed()` before executing the request.
4.  Update `ask_gemini` to report success/failure to the breaker instance.
5.  Add a "half-open" state logic to allow periodic probes after a cooldown period.

## Risk
**Failure Mode:** The circuit breaker trips prematurely due to a transient network blip, blocking legitimate requests for too long.
**Mitigation:** Implement a "half-open" state that allows a single test request after a `cooldown_period` (e.g., 60 seconds) to verify if the service has recovered.

**Confidence Score:** 9/10. The logic is standard for distributed systems and the integration points in `sam.py` are well-defined.