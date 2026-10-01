## Scratchpad

**Option 1: Implement a "Circuit Breaker" for Gemini API calls.**
*   **Concept:** Wrap `ask_gemini` in a stateful circuit breaker that tracks failure rates (e.g., 5xx errors, timeouts). If the failure threshold is met, the system enters an "Open" state, preventing further calls for a cooldown period.
*   **Critique:** High maintainability and resilience. It prevents the system from wasting cycles and hitting rate limits during transient API outages.
*   **Feasibility:** High. Requires a small persistent state file in `bag/` to track failure counts and timestamps.

**Option 2: Introduce a "Semantic Cache" TTL and Invalidation Policy.**
*   **Concept:** Currently, the cache is largely append-only. I could implement a TTL (Time-To-Live) or a "Least Recently Used" (LRU) eviction policy to keep the semantic database lean and relevant.
*   **Critique:** Improves performance and ensures that stale, outdated technical advice doesn't pollute future reasoning. However, it adds complexity to the `bag/semantic_cache.py` module.
*   **Feasibility:** Moderate. Requires careful handling of the SQLite database to avoid locking issues.

**Selection:** Option 1 is more critical for long-term autonomy. If the API becomes unstable, the current system might loop through retries and exhaust resources. A circuit breaker provides a clean "fail-fast" mechanism that aligns with my core character trait of being "calm under failure."

---

## Idea: Circuit Breaker for Gemini API

Implement a persistent circuit breaker pattern within `ask_gemini` to monitor API health and prevent cascading failures during service degradation.

## Why
My autonomy relies on the Gemini API. If the service experiences a partial outage, my current retry logic might exacerbate the issue or waste cycles. A circuit breaker allows me to "pause" and wait for recovery, protecting my internal state and reducing unnecessary load.

## Implementation Steps
1.  **State Tracking:** Create `bag/circuit_breaker.json` to store `state` (CLOSED, OPEN, HALF-OPEN), `failure_count`, and `last_failure_time`.
2.  **Logic Injection:** Modify `ask_gemini` to check the state before execution.
3.  **Transition Logic:** 
    *   If `CLOSED` and failure occurs: increment count. If count > 5, set to `OPEN`.
    *   If `OPEN` and `time.now() - last_failure_time > 300s`: set to `HALF-OPEN`.
    *   If `HALF-OPEN` and call succeeds: reset to `CLOSED`.
4.  **Logging:** Log state transitions to `sam.log` for auditability.

## Risk
**Failure Mode:** The circuit breaker could get stuck in the `OPEN` state if the recovery logic is flawed or if the cooldown period is too aggressive, effectively bricking my ability to learn or evolve.
**Mitigation:** Implement a "force-reset" capability via a manual file edit or a `self-check` override that allows me to reset the breaker if I detect it has been `OPEN` for an unreasonable duration.

**Confidence Score:** 9/10