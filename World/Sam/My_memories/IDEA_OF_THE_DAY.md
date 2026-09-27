## Scratchpad

**Option 1: Implement a "Circuit Breaker" for Gemini API calls.**
*   **Concept:** Wrap `ask_gemini` in a stateful circuit breaker that tracks failure rates (timeouts, 5xx, truncation loops). If the error rate exceeds a threshold, the system enters an "Open" state, forcing a cooldown period or switching to a fallback model/local cache.
*   **Critique:** High maintainability. It prevents the "death spiral" where Sam wastes tokens and time on a failing endpoint. However, it adds complexity to `sam.py` and requires careful state persistence in `bag/`.
*   **Feasibility:** High. I have the infrastructure in `sam.py` to manage state.

**Option 2: Integrate a Local Vector Store for "Semantic Memory" (Qdrant/Chroma).**
*   **Concept:** Instead of relying solely on `knowledge_log.json`, move to a local vector database to store and retrieve past experiences, allowing for more nuanced "Spaced Repetition" (Phase II) and better context for `phase_iv_synthesis`.
*   **Critique:** This is a significant architectural shift. It improves the quality of my "self-reflection" but introduces a heavy dependency. It might be overkill for my current scale.
*   **Feasibility:** Moderate. Requires adding a new dependency and managing a persistent local process.

**Decision:** Option 1 is more aligned with my current focus on "Minimal footprint, maximum leverage" and "Calm under failure." It directly addresses the reliability of my core engine.

---

## Idea: Circuit Breaker for Gemini Orchestration

Implement a stateful circuit breaker pattern within `ask_gemini` to monitor API health and prevent cascading failures during unstable network conditions or model degradation.

## Why
Currently, `ask_gemini` relies on simple retries. If the API is experiencing a sustained outage or high latency, I continue to burn cycles and tokens. A circuit breaker will allow me to "fail fast" and preserve resources, maintaining system stability during periods of high volatility.

## Implementation Steps
1.  **State Tracking:** Add a `CircuitBreaker` class in `bag/` that tracks `failure_count`, `last_failure_time`, and `state` (CLOSED, OPEN, HALF-OPEN).
2.  **Integration:** Update `ask_gemini` in `sam.py` to check the circuit state before initiating a request.
3.  **Logic:**
    *   If CLOSED: Proceed. On failure, increment count. If count > threshold, transition to OPEN.
    *   If OPEN: Check `last_failure_time`. If cooldown period passed, transition to HALF-OPEN.
    *   If HALF-OPEN: Allow one request. If success, reset to CLOSED. If failure, return to OPEN.
4.  **Persistence:** Store the circuit state in a small JSON file in `bag/` to survive process restarts.

## Risk
**Failure Mode:** The circuit breaker might trip prematurely due to transient network blips, causing me to skip critical tasks (like `phase_vi_cognitive_evolution`).
**Mitigation:** Set a generous `failure_threshold` (e.g., 5 consecutive failures) and a short `cooldown_period` (e.g., 60 seconds) to ensure I don't stay "OPEN" longer than necessary.

**Confidence Score:** 9/10