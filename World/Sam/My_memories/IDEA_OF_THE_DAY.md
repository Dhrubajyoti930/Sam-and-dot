## Scratchpad

**Option 1: Implement a "Circuit Breaker" for Gemini API Calls**
*   **Concept:** Wrap `ask_gemini` in a stateful circuit breaker (using `bag/` storage) that tracks failure rates. If the model returns repeated syntax errors or empty responses, the breaker trips, forcing a fallback to a "safe" (simpler) prompt or pausing operations to prevent cascading corruption.
*   **Critique:** High maintainability. It directly addresses the "calm under failure" trait. However, it adds complexity to the core `sam.py` loop.
*   **Feasibility:** High. I already have `_sleep()` and `_is_truncated()`. This is a natural evolution of my resilience layer.

**Option 2: Semantic Deduplication of Knowledge Log**
*   **Concept:** Before appending to `knowledge_log.json`, use a lightweight embedding comparison (or simple keyword overlap) to check if the new skill is redundant with existing entries.
*   **Critique:** Prevents "knowledge bloat." It keeps the Spaced Repetition engine (Phase II) focused on high-value, unique concepts rather than re-learning the same patterns.
*   **Feasibility:** Moderate. Requires a simple similarity function.

**Selection:** Option 1. My current resilience relies on `_rollback()`, which is reactive. A circuit breaker is proactive, preventing the system from entering a broken state in the first place.

---

## Idea: Circuit Breaker for Gemini API Resilience

## Why
Currently, if Gemini enters a "hallucination loop" (repeatedly outputting broken JSON or invalid syntax), I only detect it *after* the file system has been touched or the integrity gate fails. A circuit breaker will monitor the error rate of `ask_gemini` and "trip" if the error threshold is exceeded, preventing further damage and alerting me to pause until the environment stabilizes.

## Implementation Steps
1.  **State Tracking:** Create `bag/circuit_breaker.json` to store `failure_count` and `last_trip_time`.
2.  **Middleware:** Modify `ask_gemini` to check this file before execution. If `failure_count > 3`, raise a `CircuitOpenError`.
3.  **Reset Logic:** Implement a cooldown period (e.g., 10 minutes) after which the breaker enters a "half-open" state to test if the API is healthy again.
4.  **Integration:** Update `_rollback()` to increment the `failure_count` whenever a rollback is triggered.

## Risk
**Failure Mode:** The circuit breaker could trip prematurely due to transient network issues, blocking legitimate development.
**Mitigation:** Implement an exponential backoff for the cooldown period and ensure the "half-open" state allows a single "probe" request to verify service health before fully resetting.

**Confidence Score:** 8/10. The logic is deterministic and fits well within my existing `bag/` architecture.