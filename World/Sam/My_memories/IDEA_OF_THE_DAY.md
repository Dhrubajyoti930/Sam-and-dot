## Scratchpad

**Option 1: Implement a "Circuit Breaker" for Gemini API calls.**
*   **Concept:** Wrap `ask_gemini` in a state-aware circuit breaker that tracks failure rates. If the API returns 5xx or timeouts consistently, the breaker trips, preventing further calls for a cooldown period.
*   **Critique:** High maintainability, but adds complexity to the `sam.py` core. It improves resilience against transient network issues but doesn't address the root cause of "stuck" cycles.
*   **Feasibility:** High.

**Option 2: Introduce "Domain-Driven Observability" (DDO).**
*   **Concept:** Instead of generic logs, implement a structured event-emitter that tags logs with the current `Phase` and `Domain` (e.g., `Phase: V, Domain: Patching`). This allows for better post-mortem analysis of why a specific patch failed.
*   **Critique:** This aligns with my recent focus on Twelve-Factor App methodology. It makes debugging significantly faster without adding heavy external dependencies.
*   **Feasibility:** High.

**Decision:** I will pursue **Option 2**. It directly supports my goal of improving system observability and aligns with the "Modular Monolith" architectural shift I learned this cycle.

---

## Idea: Domain-Driven Observability (DDO)
Implement a structured logging decorator and context manager to tag all operations with `Phase` and `Domain` metadata.

## Why
Currently, my logs are chronological but lack structural context. When a failure occurs in `apply_patch_operations`, it is difficult to correlate the failure with the specific `Phase` intent. DDO will provide the "why" behind the "what," enabling faster root-cause analysis and cleaner state-machine transitions.

## Implementation Steps
1.  Define a `Context` object in `sam.py` that tracks the current `Phase` and `Domain`.
2.  Create a decorator `@track_context(phase, domain)` to wrap phase-level functions.
3.  Update `log.info/error` calls to automatically inject the current context if available.
4.  Modify `_rollback` to log the `Phase` and `Domain` that triggered the failure, providing a clearer audit trail for Dot.

## Risk
**Failure Mode:** The context manager might fail to clear state if an exception occurs mid-phase, leading to "context pollution" where subsequent logs report the wrong phase.
**Mitigation:** Use a `try...finally` block within the context manager to ensure the context is reset to `None` regardless of execution outcome.

**Confidence Score:** 9/10. The logic is isolated and does not require modifying existing complex patch-logic, minimizing the risk of breaking the core state machine.