## Scratchpad

### Option 1: Implement "Semantic Circuit Breakers" for Gemini Calls
*   **Concept:** Wrap `ask_gemini` in a circuit breaker that tracks failure rates (timeouts, JSON parse errors, truncation loops). If a specific prompt template consistently fails, the system automatically switches to a "fallback" prompt or triggers a `_rollback()` to a known-stable prompt version.
*   **Critique:** High maintainability. It addresses the root cause of "stuck" cycles. However, it adds complexity to `sam.py` and requires persistent state for failure counters.
*   **Feasibility:** High. I already have `bag/semantic_cache.py`.

### Option 2: Integrate "Streaming Materialized Views" for Knowledge Log
*   **Concept:** Instead of full-file rewrites for `knowledge_log.json`, implement a lightweight append-only log with an indexed "Materialized View" (a separate JSON file) that pre-calculates the next 5 due items.
*   **Critique:** Improves performance for `phase_ii_spaced_repetition`. It aligns with my recent learning on MVs. However, it introduces potential desync between the log and the view.
*   **Feasibility:** Moderate. Requires careful handling of file atomicity.

**Decision:** Option 1 is more critical for long-term autonomy. If my self-modification pipeline is brittle, the system fails. I will prioritize the "Semantic Circuit Breaker" to ensure my self-correction loops are robust.

---

## Idea: Semantic Circuit Breaker for Gemini Orchestration

## Why
My current `_stitch_gemini` and `_lint_fix_with_gemini` methods are susceptible to infinite loops or cascading failures if a prompt template becomes "poisoned" (e.g., due to model drift or schema changes). A circuit breaker provides a hard stop, preventing wasted tokens and protecting the system state from being corrupted by repeated bad patches.

## Implementation Steps
1.  **State Tracking:** Add a `circuit_breaker.json` in `bag/` to track failure counts per `prompt_id`.
2.  **Decorator:** Create a `@circuit_breaker` decorator in `sam.py` to wrap `ask_gemini` calls.
3.  **Logic:** If failure count > 3 for a specific prompt, the breaker trips, returning a cached "safe" response or raising a `CircuitOpenError` to trigger a controlled `_rollback()`.
4.  **Reset:** Implement a manual or cycle-based reset mechanism.

## Risk
**Failure Mode:** The circuit breaker trips prematurely due to transient network issues, blocking legitimate self-repair.
**Mitigation:** Implement an exponential backoff for the "Open" state and allow a "Force-Reset" flag in `motion.md` for Dot to override.

**Confidence Score:** 8/10. The logic is straightforward, but requires careful integration with existing `ask_gemini` error handling.