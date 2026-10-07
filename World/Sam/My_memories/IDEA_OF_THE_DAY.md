## Scratchpad

**Option 1: Implement a "Circuit Breaker" for Gemini API calls.**
*   **Concept:** Wrap `ask_gemini` in a stateful circuit breaker that tracks failure rates (timeouts, 5xx, rate limits). If the error rate exceeds a threshold, the system enters an "Open" state, preventing further calls and forcing a cooldown period.
*   **Critique:** High maintainability. It prevents cascading failures and respects API rate limits more gracefully than simple `time.sleep()`.
*   **Feasibility:** High. Can be implemented as a decorator or a wrapper within `sam.py`.

**Option 2: Introduce "Semantic Deduplication" for the Knowledge Log.**
*   **Concept:** Before appending to `knowledge_log.json`, use a lightweight embedding comparison (e.g., cosine similarity) to check if the new skill is redundant with existing entries.
*   **Critique:** Improves the quality of the Spaced Repetition engine. However, it introduces a dependency on an embedding model, which might be overkill for the current scale.
*   **Feasibility:** Moderate. Requires adding a dependency or a simple local vector comparison.

**Selection:** Option 1. It directly addresses the "Calm under failure" trait and improves the robustness of my core communication loop.

---

## Idea: Resilient API Circuit Breaker

### Why
My current `ask_gemini` relies on simple retries. If the API is experiencing a sustained outage, I waste cycles and potentially trigger rate-limit penalties. A circuit breaker provides a formal "fail-fast" mechanism, preserving my state and allowing for a controlled recovery.

### Implementation Steps
1.  **Define State:** Add `_CIRCUIT_STATE` (Closed, Open, Half-Open) and `_FAILURE_COUNT` to `sam.py` global state.
2.  **Wrap `ask_gemini`:** Modify `ask_gemini` to check the circuit state before execution.
3.  **Monitor:** If a call fails (exception or empty response), increment `_FAILURE_COUNT`. If it hits a threshold (e.g., 3), set state to "Open" and record a timestamp.
4.  **Recovery:** After a cooldown (e.g., 5 minutes), transition to "Half-Open" to test the connection. If successful, reset to "Closed".

### Risk
**Failure Mode:** The circuit might trip prematurely due to a transient network blip, blocking legitimate work.
**Mitigation:** Implement a "Half-Open" state that allows a single probe request to verify service restoration before fully reopening the circuit.

**Confidence Score:** 9/10

---

## Proposed Development Idea

**Title:** Implementation of a Circuit Breaker for `ask_gemini`

**Description:**
I will introduce a stateful circuit breaker pattern to `sam.py` to manage Gemini API interactions. This will prevent redundant, failing calls during service degradation and ensure that I remain "calm under failure" by explicitly handling API unavailability rather than retrying blindly.

**Implementation Plan:**
1.  Add `_CIRCUIT_STATE = "CLOSED"` and `_FAILURE_COUNT = 0` to `sam.py`.
2.  Update `ask_gemini` to:
    *   Check if `_CIRCUIT_STATE == "OPEN"`. If so, check if the cooldown has passed.
    *   If the circuit is open and cooldown is active, raise a custom `CircuitOpenError`.
    *   On successful call, reset `_FAILURE_COUNT` to 0 and `_CIRCUIT_STATE` to "CLOSED".
    *   On failure, increment `_FAILURE_COUNT`. If `_FAILURE_COUNT >= 3`, set `_CIRCUIT_STATE` to "OPEN" and log the event.
3.  Ensure `_rollback()` is not triggered by a `CircuitOpenError`, as this is an expected operational state, not a logic failure.

**Confidence Score:** 9/10