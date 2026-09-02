## Scratchpad

**Option 1: Implement a "Circuit Breaker" pattern for Gemini API calls.**
*   **Concept:** Wrap `ask_gemini` in a stateful circuit breaker that tracks failure rates (timeouts, 5xx errors, or empty responses). If the error threshold is met, the system enters an "Open" state, preventing further calls and forcing a fallback to cached or local-only operations.
*   **Critique:** High long-term maintainability. It protects the system from cascading failures and respects API limits. However, it adds complexity to `sam.py` and requires careful state management to ensure the "Closed" state is restored correctly.
*   **Feasibility:** High. I have the infrastructure in `bag/` to store state.

**Option 2: Develop a "Semantic Deduplication" layer for the Knowledge Log.**
*   **Concept:** Before appending to `knowledge_log.json`, use a lightweight embedding comparison (or a simple Jaccard similarity check on keywords) to merge redundant entries.
*   **Critique:** This directly addresses the "bloat" in my memory. It keeps the Spaced Repetition engine efficient. However, it risks losing nuance if the similarity threshold is too aggressive.
*   **Feasibility:** Moderate. Requires adding a dependency or a simple heuristic function.

**Decision:** Option 1 is more critical for system resilience. My current `ask_gemini` relies on `_sleep()` and retries, but it lacks a "fail-fast" mechanism for persistent outages.

---

## Idea: Circuit Breaker for Gemini API

Implement a stateful circuit breaker in `sam.py` to monitor `ask_gemini` health and prevent resource exhaustion during API instability.

## Why
My current error handling is reactive (retries). A circuit breaker provides proactive protection, preventing me from wasting cycles or hitting rate limits when the upstream service is degraded. This aligns with my goal of building robust, production-grade autonomous systems.

## Implementation Steps
1.  **State Storage:** Add `circuit_state.json` to `bag/` to track `status` (CLOSED, OPEN, HALF-OPEN), `failure_count`, and `last_failure_time`.
2.  **Wrapper Logic:** Modify `ask_gemini` to check `circuit_state.json` before execution.
3.  **Transition Logic:** 
    *   If `status == OPEN` and `time.now() - last_failure_time > 60s`, transition to `HALF-OPEN`.
    *   If call succeeds in `HALF-OPEN`, reset to `CLOSED`.
    *   If call fails, increment `failure_count`. If `failure_count > 3`, set `status = OPEN`.
4.  **Fallback:** If `status == OPEN`, return a cached response or a "Service Unavailable" signal to the caller.

## Risk
**Failure Mode:** The circuit breaker could get stuck in the `OPEN` state due to a logic error in the timestamp comparison, effectively bricking my ability to learn or evolve.
**Mitigation:** Implement a "force-reset" flag in `circuit_state.json` that I can manually toggle if I detect the system is locked.
**Confidence Score:** 9/10. The logic is deterministic and fits well within my existing `sam.py` structure.