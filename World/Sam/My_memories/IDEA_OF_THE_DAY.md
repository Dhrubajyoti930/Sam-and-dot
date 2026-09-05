## Scratchpad

**Option 1: Implement a "Circuit Breaker" for Gemini API calls.**
*   **Concept:** Wrap `ask_gemini` in a state-aware circuit breaker that tracks failure rates (e.g., 5xx errors, timeouts) and trips if the error threshold is exceeded, preventing further calls until a cooldown period.
*   **Critique:** High maintainability. It prevents "death spirals" where Sam wastes cycles and tokens on a failing service. However, it adds complexity to `sam.py` and requires persistent state for the breaker status.
*   **Feasibility:** High. I have the `bag/` infrastructure to store the breaker state.

**Option 2: Introduce "Semantic Health Checks" for `knowledge_log.json`.**
*   **Concept:** Add a routine to `phase_ii_spaced_repetition` that uses an LLM to verify if the stored summaries in `knowledge_log.json` are still relevant or if they have become stale/contradictory compared to newer knowledge.
*   **Critique:** Improves long-term memory quality. However, it risks "hallucinated pruning" where valid knowledge is discarded. It also increases token consumption significantly.
*   **Feasibility:** Moderate. Requires careful prompt engineering to ensure the "judge" doesn't over-prune.

**Selection:** Option 1. Given my focus on "calm under failure" and "disciplined curiosity," a circuit breaker is a foundational engineering improvement that directly supports my ability to recover gracefully from external API instability.

---

## Idea: Circuit Breaker for API Resilience

Implement a persistent circuit breaker pattern for `ask_gemini` to prevent cascading failures during API outages.

## Why
Currently, if the Gemini API experiences sustained downtime, my `run_cycle` will repeatedly attempt calls, potentially exhausting resources or hitting rate limits while in a broken state. A circuit breaker allows me to "fail fast" and pause operations, preserving my state and allowing for manual intervention or automated recovery without wasting cycles.

## Implementation Steps
1.  **State Storage:** Create `bag/circuit_breaker.json` to track `state` (CLOSED, OPEN, HALF-OPEN), `failure_count`, and `last_failure_time`.
2.  **Wrapper Logic:** Modify `ask_gemini` in `sam.py` to check the breaker state before execution.
3.  **Transition Logic:** 
    *   If `CLOSED` and call fails: increment `failure_count`. If count > 3, set to `OPEN`.
    *   If `OPEN` and `time.now() - last_failure_time > 300s`: transition to `HALF-OPEN`.
    *   If `HALF-OPEN` and call succeeds: reset to `CLOSED`.
4.  **Integration:** Ensure `_rollback()` or `self_check()` can trigger a reset if necessary.

## Risk
**Failure Mode:** The circuit breaker might trip prematurely due to transient network blips, causing me to skip a cycle unnecessarily.
**Mitigation:** Implement a "cooldown" period (e.g., 5 minutes) and a conservative failure threshold (3 consecutive failures) before tripping.
**Confidence Score:** 9/10. This is a standard architectural pattern that fits well within my existing `bag/` utility structure.