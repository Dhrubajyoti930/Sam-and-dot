## Scratchpad

**Option 1: Implement a "Circuit Breaker" pattern for Gemini API calls.**
*   *Concept:* Wrap `ask_gemini` in a stateful circuit breaker that tracks failure rates (timeouts, 500s). If the error rate exceeds a threshold, the circuit "opens," and Sam stops attempting calls for a cooling-off period.
*   *Critique:* High maintainability. It prevents cascading failures and respects API limits more gracefully than simple `time.sleep`. However, it adds complexity to `sam.py` and requires persistent state (or a shared memory object) to track the circuit status across cycles.
*   *Feasibility:* High.

**Option 2: Integrate `PydanticAI` for structured tool-use in `phase_v_development`.**
*   *Concept:* Replace the current manual JSON parsing/extraction logic in `phase_v_development` with `PydanticAI` models to enforce schema validation on the development plan.
*   *Critique:* This aligns with current market trends (Trend #3). It significantly reduces the risk of malformed plans. However, it introduces a new dependency and requires refactoring the existing `_parse_gemini_json` logic.
*   *Feasibility:* Moderate.

**Selection:** Option 1 is more critical for Sam's long-term autonomy. If the API becomes unstable, Sam’s current retry logic might lead to "retry storms." A circuit breaker is a fundamental SRE pattern that directly improves the robustness of the core `ask_gemini` service.

---

## Idea: Circuit Breaker for Gemini API

Implement a `CircuitBreaker` class in `bag/` to monitor `ask_gemini` health, preventing redundant calls during API outages.

## Why
My current `ask_gemini` uses basic retries but lacks a "fail-fast" mechanism for sustained outages. If the API is down, I waste cycles and potentially trigger rate-limit penalties. A circuit breaker provides a clean, observable way to pause operations when the system is saturated or failing, aligning with the "Four Golden Signals" (Errors/Saturation) learned this cycle.

## Implementation Steps
1.  Create `bag/circuit_breaker.py` with a `CircuitBreaker` class tracking `failure_count`, `last_failure_time`, and `state` (CLOSED, OPEN, HALF-OPEN).
2.  Modify `sam.py` to instantiate a global `CIRCUIT_BREAKER`.
3.  Wrap the `ask_gemini` logic:
    *   Check `CIRCUIT_BREAKER.can_execute()`.
    *   If `True`, proceed.
    *   On success, call `CIRCUIT_BREAKER.record_success()`.
    *   On exception, call `CIRCUIT_BREAKER.record_failure()`.
4.  If the circuit is OPEN, `ask_gemini` should return a cached response or a "System Degraded" signal to prevent further load.

## Risk
**Failure Mode:** The circuit breaker might stay "OPEN" too long if the recovery logic is too conservative, causing me to miss valid opportunities to resume work.
**Mitigation:** Implement a "HALF-OPEN" state that allows a single "probe" request after a cooldown period (e.g., 5 minutes) to verify if the API has recovered.

**Confidence Score:** 9/10