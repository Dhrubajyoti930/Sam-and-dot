## Scratchpad

**Option 1: Implement a Circuit Breaker for Gemini API calls.**
*   **Concept:** Wrap `ask_gemini` in a stateful circuit breaker (Closed, Open, Half-Open) to stop hammering the API when it returns 429s or 500s.
*   **Critique:** High feasibility. It directly addresses the "Resilient" pillar of the Reactive Manifesto.
*   **Trade-off:** Adds state management to `sam.py`. If the state is lost on restart, the breaker resets, which is acceptable but not ideal.

**Option 2: Transition to Asynchronous I/O for `ask_gemini` and file operations.**
*   **Concept:** Refactor `sam.py` to use `asyncio` and `httpx` for non-blocking network calls.
*   **Critique:** High impact, but high risk. It requires a massive refactor of the entire call stack, including `_stitch_gemini` and `phase_x` functions.
*   **Trade-off:** Significant complexity increase. Might violate the "Minimal footprint, maximum leverage" core trait if not handled with extreme care.

**Selection:** Option 1 is the superior choice for this cycle. It aligns with the "Reactive Architecture" skill learned, provides immediate resilience, and fits within a surgical refactor without requiring a total rewrite of the execution loop.

---

## Idea: Circuit Breaker Pattern for API Resilience

Implement a `CircuitBreaker` class in `bag/resilience.py` and integrate it into `ask_gemini` to manage failure states and prevent cascading exhaustion of the API client.

## Why
Currently, `ask_gemini` relies on simple retries. If the API is experiencing sustained downtime or rate-limiting, retries exacerbate the issue and waste cycles. A circuit breaker provides a "fail-fast" mechanism, preserving system resources and allowing the API time to recover.

## Implementation Steps
1.  **Create `bag/resilience.py`**: Define a `CircuitBreaker` class tracking `failure_count`, `last_failure_time`, and `state`.
2.  **Update `sam.py`**: Import the breaker and wrap the `CLIENT.models.generate_content` call within `ask_gemini`.
3.  **State Logic**: If the breaker is `OPEN`, raise a custom `CircuitOpenError` immediately, skipping the network call.
4.  **Transition**: On success, reset the breaker. On failure, increment count; if threshold reached, transition to `OPEN`.

## Risk
**Failure Mode:** The breaker might stay `OPEN` too long if the recovery time is misconfigured, causing Sam to "stall" and stop making progress even when the API is healthy.
**Mitigation:** Implement a "Half-Open" state that allows a single test request after a cooldown period (e.g., 60 seconds) to verify service restoration.

**Confidence Score: 9/10** (The pattern is well-understood and the implementation is isolated).