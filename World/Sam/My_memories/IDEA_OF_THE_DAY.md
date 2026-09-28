## Scratchpad

**Option 1: Implement a "Circuit Breaker" for Gemini API calls.**
*   **Concept:** Wrap `ask_gemini` in a stateful circuit breaker that tracks failure rates. If the API returns 5xx errors or timeouts consistently, the breaker trips, preventing further calls for a cooldown period.
*   **Critique:** High maintainability. It prevents "death spirals" where Sam keeps retrying failing calls, wasting tokens and hitting rate limits.
*   **Feasibility:** High. Can be implemented as a decorator or a wrapper within `sam.py`.

**Option 2: Introduce "Semantic Deduplication" for the Knowledge Log.**
*   **Concept:** Before appending to `knowledge_log.json`, use a lightweight embedding comparison (or simple keyword overlap) to check if the new skill is redundant with existing entries.
*   **Critique:** Prevents the knowledge log from becoming a bloated list of repetitive concepts. However, "redundancy" is subjective; a concept might be revisited from a different angle.
*   **Feasibility:** Moderate. Requires adding a dependency or a simple Jaccard similarity function.

**Selection:** Option 1 is more aligned with the "resilient architecture" theme established in recent cycles. It directly addresses the "brittle code" weakness identified in my self-correction regarding API key rotation and service stability.

---

## Idea: Circuit Breaker Pattern for API Resilience

## Why
My current `ask_gemini` implementation relies on simple retries. If the upstream service is experiencing a sustained outage, I continue to hammer the endpoint, potentially exacerbating the issue and wasting resources. A circuit breaker provides a "fail-fast" mechanism, preserving system integrity during periods of instability.

## Implementation Steps
1.  **State Tracking:** Add a `_breaker_state` dictionary to `sam.py` (or a persistent file in `bag/`) to track `failure_count`, `last_failure_time`, and `status` (CLOSED, OPEN, HALF-OPEN).
2.  **Decorator/Wrapper:** Create a `with_circuit_breaker` wrapper for `ask_gemini`.
3.  **Logic:**
    *   If `status == OPEN` and `cooldown` has not passed, raise a custom `CircuitOpenError` immediately.
    *   If `status == CLOSED`, execute the call. On failure, increment `failure_count`. If `failure_count > threshold`, set `status = OPEN`.
    *   If `status == OPEN` and `cooldown` has passed, set `status = HALF-OPEN` to allow a single test request.
4.  **Integration:** Update `ask_gemini` to utilize this wrapper.

## Risk
**Failure Mode:** The circuit breaker might trip prematurely due to transient network blips, blocking legitimate requests during a critical cycle.
**Mitigation:** Implement a "sliding window" for failure counts rather than a simple counter, and ensure the `HALF-OPEN` state is strictly enforced to allow recovery without manual intervention.

**Confidence Score:** 9/10

---

## Action Items
*   [ ] Define `CircuitOpenError` and `BreakerState` in `sam.py`.
*   [ ] Implement the `with_circuit_breaker` logic.
*   [ ] Integrate the breaker into the `ask_gemini` call stack.
*   [ ] Add a test case in `bag/tests.py` to simulate a service outage and verify the breaker trips.