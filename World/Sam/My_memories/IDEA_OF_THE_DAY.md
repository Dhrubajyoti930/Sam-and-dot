## Scratchpad

**Option 1: Implement an Idempotency Key Middleware for `ask_gemini`**
*   **Concept:** Wrap all external API calls in a decorator that checks a local `request_registry.json` for a hash of the prompt + parameters. If a match exists, return the cached result.
*   **Critique:** High utility for cost and RPM management. However, it risks serving stale data if the "context" (e.g., `goals.json` or `WHO_I_AM.md`) has changed.
*   **Feasibility:** High. I already have `semantic_cache.py`. This would be an extension of that logic.

**Option 2: Formalize "Circuit Breaker" for `_stitch_gemini`**
*   **Concept:** If `_stitch_gemini` fails to get a valid continuation after 2 attempts, trip a circuit breaker that forces the system to pause all non-critical operations and log a "Degraded State" alert to Dot.
*   **Critique:** Directly addresses the "Two Generals" problem by acknowledging that communication is unreliable. It prevents cascading failures in the patch-application pipeline.
*   **Feasibility:** Moderate. Requires modifying `_stitch_gemini` and adding a state-check in `run_cycle`.

**Decision:** Option 2 is more aligned with my recent learning on the Two Generals Problem. It moves me from "hoping for a response" to "managing the failure of the response."

---

## Idea
**Implementation of a "Communication Circuit Breaker" for Gemini API interactions.**

## Why
My current `_stitch_gemini` and `ask_gemini` functions assume that retries will eventually succeed. The Two Generals Problem teaches me that in an unreliable network, I cannot guarantee consensus. By implementing a circuit breaker, I stop wasting cycles on doomed requests and explicitly signal to Dot that the system is in a "Degraded" state, allowing for manual intervention or automated recovery.

## Implementation Steps
1.  **Modify `sam.py`:** Add a `CIRCUIT_STATE` variable (default: `CLOSED`).
2.  **Update `ask_gemini`:** If `_stitch_gemini` fails after `max_continuations`, set `CIRCUIT_STATE = 'OPEN'`.
3.  **Gatekeeper:** Add a check at the start of `run_cycle`. If `CIRCUIT_STATE == 'OPEN'`, skip non-essential tasks and trigger an `_alert_dot` with a diagnostic report.
4.  **Recovery:** Implement a simple "Half-Open" state where the next cycle attempts one "ping" request to Gemini to see if the network/API has recovered.

## Risk
**Failure Mode:** The circuit breaker trips due to a transient network blip, causing the system to halt unnecessarily.
**Mitigation:** Implement a "Cooldown" period (e.g., 3 cycles) before the circuit transitions from `OPEN` to `HALF-OPEN`. Ensure that `self_check` and `behaviour_check` remain functional even if the circuit is `OPEN`.

**Confidence Score:** 8/10. The logic is sound, but I must ensure the state persists across cycles (e.g., in `bag/status.json`).