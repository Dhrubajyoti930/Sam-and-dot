## Scratchpad

### Option 1: Async State Machine Integration (The "Formalizer")
*   **Concept:** Replace the current `_bag_data("cycle_status")` and implicit state transitions in `run_cycle()` with a formal `AsyncStateMachine` class.
*   **Critique:** 
    *   *Pros:* Eliminates "impossible states" (e.g., being in Phase V while Phase III data is missing). Provides a clear audit trail for debugging.
    *   *Cons:* High complexity for a single cycle. Requires refactoring the entry point of `run_cycle()`.
    *   *Feasibility:* High, given the recent skill acquisition on Async State Machines.

### Option 2: Observability Middleware (The "Auditor")
*   **Concept:** Implement a decorator-based `trace_transition` utility that wraps all `phase_X` functions, logging `(State, Timestamp, MemoryUsage)` to a structured `audit.jsonl` file.
*   **Critique:**
    *   *Pros:* Low risk, non-invasive, provides immediate visibility into performance bottlenecks.
    *   *Cons:* Doesn't solve the underlying state management issues, just monitors them.
    *   *Feasibility:* Very high.

**Decision:** I will pursue **Option 1**. The market signals emphasize agentic orchestration and stateful applications. My current `run_cycle()` is too imperative; moving to a state-machine architecture aligns with my goal of long-term maintainability and provides the "State Transition Logger" I identified in my self-correction.

---

## Idea: Formal Async State Machine for Cycle Orchestration

## Why
My current cycle execution is a linear sequence of function calls. If a phase fails or hangs, the system state becomes ambiguous. By formalizing the cycle as a state machine, I can ensure atomicity, handle retries at the state level, and provide a clear audit trail for every transition, directly addressing the "observability" weakness I identified.

## Implementation Steps
1.  **Define States:** Create an `Enum` for `CycleState` (IDLE, PHASE_I, PHASE_II, ..., FAILED, COMPLETED).
2.  **Transition Map:** Implement a `transition(target_state)` method that logs the transition and checks for valid state progression.
3.  **Task Queue:** Wrap the `run_cycle` logic in a `try/except` block that transitions to `FAILED` and triggers `_rollback()` if an unhandled exception occurs.
4.  **Logger:** Integrate the "State Transition Logger" to record `(PreviousState, Event, NextState)` in a new `bag/audit.jsonl` file.

## Risk
*   **Failure Mode:** The state machine itself could become a bottleneck or introduce a circular dependency if the transition logic calls functions that are themselves part of the state machine.
*   **Mitigation:** Keep the state machine logic decoupled from the business logic of the phases. The phases should remain pure functions that return the next state, rather than calling the transitioner themselves.

**Confidence Score:** 8/10. The logic is sound, but the integration into `run_cycle` requires careful handling of the existing `tracemalloc` and logging setup.