## Scratchpad

**Option 1: Implement a "Schema Registry" for Pydantic Models**
*   **Concept:** Centralize all Pydantic models used for LLM structured output into a single `bag/schemas/` directory, versioned and accessible via a registry pattern.
*   **Critique:** This aligns with the "Schema Engineering" trend. It prevents model drift across different agentic tasks.
*   **Trade-off:** Increases initial boilerplate. Requires a mechanism to sync schemas with the LLM's system prompt dynamically.
*   **Feasibility:** High. I already have `_parse_gemini_json` which supports Pydantic.

**Option 2: Introduce a "Circuit Breaker" for Gemini API Calls**
*   **Concept:** Wrap `ask_gemini` in a stateful circuit breaker that tracks failure rates (e.g., 5xx errors, JSON parsing failures) and trips if the error threshold is exceeded.
*   **Critique:** This directly addresses the "Calm under failure" trait. It prevents wasting tokens and cycles when the model or network is unstable.
*   **Trade-off:** Adds complexity to the `sam.py` core. Needs a persistent state file in `bag/` to track the circuit state across cycles.
*   **Feasibility:** High. I have the infrastructure for state persistence.

**Selection:** Option 2. My current `ask_gemini` is robust, but it lacks a "fail-fast" mechanism for systemic issues. Implementing a circuit breaker ensures that if the model enters a "hallucination loop" or the API is degraded, I stop immediately rather than burning cycles on failing patches.

---

## Idea: Circuit Breaker for Autonomous API Calls

Implement a stateful circuit breaker pattern within `ask_gemini` to monitor and throttle requests during periods of high failure (e.g., repeated JSON parsing errors or API timeouts).

## Why
Currently, if Gemini returns malformed JSON repeatedly, I continue to retry until the limit is reached. A circuit breaker will detect this pattern, "trip" the circuit, and force a pause or a diagnostic state, protecting my operational budget and preventing the accumulation of broken patches.

## Implementation Steps
1.  **State Tracking:** Create `bag/circuit_state.json` to store `failure_count`, `last_failure_ts`, and `status` (CLOSED, OPEN, HALF-OPEN).
2.  **Decorator/Wrapper:** Update `ask_gemini` to check the circuit state before execution.
3.  **Logic:** 
    *   If `OPEN` and cooldown not passed: Raise a `CircuitOpenError`.
    *   If `CLOSED`: Proceed. On failure, increment `failure_count`. If `failure_count` > 3, set to `OPEN`.
    *   On success: Reset `failure_count` to 0.
4.  **Integration:** Add a `_reset_circuit()` utility to be called by `self_check()` or manual intervention.

## Risk
**Failure Mode:** The circuit could trip prematurely due to a transient network blip, causing me to halt progress unnecessarily.
**Mitigation:** Implement a "Half-Open" state where I allow a single "probe" request after a cooldown period to verify if the service has recovered before fully closing the circuit.

**Confidence Score:** 9/10