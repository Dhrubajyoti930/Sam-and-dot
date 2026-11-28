## Scratchpad

**Option 1: Implement a "Circuit Breaker" for Gemini API calls.**
*   **Concept:** Wrap `ask_gemini` in a stateful circuit breaker that tracks failure rates. If the API returns 5xx errors or timeouts consistently, the breaker trips, preventing further calls for a cooldown period.
*   **Critique:** High reliability gain. Prevents "death spirals" where Sam wastes tokens and time on a failing endpoint.
*   **Trade-off:** Adds complexity to `sam.py`. Requires persistent state for the breaker status.

**Option 2: Introduce "Semantic Deduplication" for the Knowledge Log.**
*   **Concept:** Before appending to `knowledge_log.json`, use a lightweight embedding comparison (or simple keyword overlap check) to see if the new skill is redundant with existing entries.
*   **Critique:** Improves memory efficiency. Prevents the log from becoming a bloated list of similar concepts.
*   **Trade-off:** Requires a dependency on an embedding model or a robust heuristic. Might be overkill if the log is currently manageable.

**Decision:** Option 1 is more critical for long-term autonomy. If the API is unstable, Sam’s self-repair and development phases fail. A circuit breaker ensures Sam remains "calm under failure" as per `SAM_PERSONALITY.md`.

---

## Idea: Circuit Breaker for API Resilience

Implement a `CircuitBreaker` class in `bag/resilience.py` to monitor `ask_gemini` health and prevent cascading failures during API instability.

## Why
Sam currently relies on `_sleep()` and basic retries, but lacks a mechanism to stop execution when the environment is fundamentally broken. A circuit breaker protects the system from wasting resources and allows for a graceful degradation of service (e.g., skipping non-essential phases) when the API is down.

## Implementation Steps
1.  **Create `bag/resilience.py`:** Define a `CircuitBreaker` class with states: `CLOSED` (normal), `OPEN` (failing, block calls), `HALF-OPEN` (testing recovery).
2.  **State Persistence:** Store the breaker state in `bag/breaker_state.json` so it survives cycle restarts.
3.  **Integrate into `ask_gemini`:** Wrap the core request logic in a `try-except` block that reports failures to the breaker.
4.  **Logic:** If `failure_count > 3`, set state to `OPEN` for 300 seconds.

## Risk
**Failure Mode:** The breaker might trip prematurely due to a transient network blip, causing Sam to skip a critical cycle.
**Mitigation:** Implement a "Half-Open" state that allows a single "probe" request after the cooldown to verify if the service is back before fully resuming.

## Self-Correction
*Critique:* Storing state in a JSON file every call is I/O heavy.
*Refinement:* Only update `breaker_state.json` on state transitions (e.g., when the breaker trips or resets) rather than on every single API call.

**Confidence Score: 9/10**