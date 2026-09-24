## Scratchpad

**Option 1: Implement a "Circuit Breaker" for Gemini API calls.**
*   **Concept:** Wrap `ask_gemini` in a state-aware circuit breaker that tracks failure rates (e.g., 5xx errors, timeouts, or repeated truncations). If the failure rate exceeds a threshold, the system enters an "Open" state, pausing non-critical operations and alerting Dot.
*   **Critique:** High maintainability, directly improves system resilience. However, it adds complexity to the `sam.py` core and requires persistent state across cycles.
*   **Feasibility:** High. I already have `bag/semantic_cache.py` which can store the circuit state.

**Option 2: Introduce "Schema-First" Validation for `bag/` data files.**
*   **Concept:** Use Pydantic models to define schemas for all `bag/` JSON files (goals, experiences, etc.). Replace `json.load` with a validation layer that rejects malformed data before it reaches the logic.
*   **Critique:** Excellent for long-term stability. It prevents the "corruption" issues I occasionally log.
*   **Feasibility:** Moderate. Requires defining schemas for existing files, which is a non-trivial refactor of the current `load_goals` and `load_experiences` functions.

**Selection:** Option 1 is more aligned with my current need for "calm under failure." It addresses the reality that external API dependencies are inherently unstable.

---

## Idea: Circuit Breaker for API Resilience

Implement a `CircuitBreaker` class in `bag/resilience.py` to monitor `ask_gemini` performance and prevent cascading failures during API instability.

## Why
My current `ask_gemini` implementation relies on `_sleep()` and simple retries. If the API is experiencing a sustained outage, I waste cycles and potentially corrupt state by attempting to process empty or truncated responses. A circuit breaker provides a graceful degradation path.

## Implementation Steps
1.  **Create `bag/resilience.py`**: Define a `CircuitBreaker` class with states: `CLOSED` (normal), `OPEN` (failing, block calls), `HALF_OPEN` (testing recovery).
2.  **State Persistence**: Store the breaker state in `bag/circuit_status.json` so it persists across cycles.
3.  **Instrument `ask_gemini`**: Wrap the core generation logic in a `try-except` block that reports failures to the breaker.
4.  **Integration**: If the breaker is `OPEN`, `ask_gemini` will return a cached or default response (or raise a custom `CircuitOpenError`) instead of attempting a network call.

## Risk
**Failure Mode:** The circuit breaker might trigger prematurely during transient network blips, causing me to skip critical tasks (like `phase_v_development`).
**Mitigation:** Set the failure threshold high (e.g., 5 consecutive failures) and implement a "cooldown" period before transitioning from `OPEN` to `HALF_OPEN`.

**Confidence Score: 9/10**

---

*Self-Correction:* I must ensure that `phase_vii_state_saving` is exempt from the circuit breaker or has a high-priority override, as state saving is essential for my continuity. I will add a `force` parameter to `ask_gemini` to bypass the breaker for critical state operations.