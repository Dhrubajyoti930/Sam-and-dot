## Scratchpad

**Option 1: Implement a "Circuit Breaker" for Gemini API calls.**
*   **Concept:** Wrap `ask_gemini` in a stateful circuit breaker (Closed, Open, Half-Open) that tracks consecutive failures and latency spikes.
*   **Critique:** High utility for reliability. If Gemini experiences transient outages, the system currently just retries blindly, which wastes tokens and time.
*   **Trade-off:** Adds complexity to `sam.py`. Requires persistent state for the circuit status.
*   **Feasibility:** High. I can store the state in `bag/`.

**Option 2: Automated EvalOps for Patch Operations.**
*   **Concept:** Before applying a patch, generate a synthetic test case based on the intended change, run it, and verify the delta.
*   **Critique:** This moves toward "Evaluation-Driven Development." It significantly reduces the risk of "hallucinated" patches that pass syntax checks but fail logic.
*   **Trade-off:** High overhead per cycle. Might be overkill for simple refactors.
*   **Feasibility:** Moderate. Requires a robust way to generate "ground truth" tests from natural language plans.

**Decision:** Option 1 is more aligned with my current need for "calm under failure" and robust infrastructure. It directly addresses the "truncation" and "retry" logic already present in `_stitch_gemini` and `ask_gemini`.

---

## Idea: Circuit-Breaker Pattern for Gemini API

Implement a persistent, stateful circuit breaker for `ask_gemini` to prevent cascading failures and manage API rate limits/outages gracefully.

## Why
Currently, if the Gemini API is unstable, I continue to hammer it with retries, potentially worsening the situation or wasting cycles. A circuit breaker allows me to "trip" the connection, wait for a cooldown period, and perform a "half-open" test before resuming full operations. This aligns with my goal of building production-grade, resilient infrastructure.

## Implementation Steps
1.  **State Storage:** Create `bag/circuit_state.json` to track `status` (CLOSED, OPEN, HALF_OPEN), `failure_count`, and `last_failure_time`.
2.  **Wrapper Logic:** Modify `ask_gemini` to check `bag/circuit_state.json` before execution.
3.  **Transition Logic:** 
    *   If `status == OPEN` and `cooldown_expired`, set to `HALF_OPEN`.
    *   If `status == HALF_OPEN` and call succeeds, reset to `CLOSED`.
    *   If call fails, increment `failure_count` and trip to `OPEN` if threshold (e.g., 3) is reached.
4.  **Integration:** Update `_stitch_gemini` to respect the circuit state.

## Risk
**Failure Mode:** The circuit breaker might trip prematurely due to a transient network glitch, blocking me from performing necessary self-repairs or cycle tasks.
**Mitigation:** Implement a "force-bypass" flag for critical recovery operations (e.g., `_rollback` or `repair_bag_modules`) so I am never locked out of my own recovery tools.

**Confidence Score:** 9/10