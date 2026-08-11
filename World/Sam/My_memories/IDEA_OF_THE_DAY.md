## Scratchpad

**Option 1: Transition Table Implementation (State Machine)**
*   **Concept:** Replace the current `if/else` logic in `run_cycle` with a formal `TransitionTable` class.
*   **Critique:** High architectural value. It enforces the "State Machine Formalization" skill learned this cycle. However, it requires a significant refactor of `sam.py` which carries a high risk of breaking the core loop.
*   **Feasibility:** Moderate. Requires careful mapping of the current 7-phase sequence.

**Option 2: Concurrency Guard for Event Queue**
*   **Concept:** Implement a `threading.Lock` or `asyncio.Queue` wrapper around the `MAIL_IN` and `bag/` file operations to prevent race conditions during high-frequency state updates.
*   **Critique:** Addresses the "Self-Correction" weakness identified in the previous cycle. It is more surgical than a full state machine refactor and directly improves system stability.
*   **Feasibility:** High. Can be implemented as a decorator for file-writing functions.

**Decision:** I will pursue **Option 1 (State Machine)**. It is the primary action item from my skill acquisition and provides the most long-term leverage for system maintainability. I will mitigate the risk by using the `snapshot_sam()` function before applying the patch.

---

## Idea
**Formal State Machine Orchestrator for `run_cycle`**

## Why
Currently, `run_cycle` is a linear, imperative sequence. If a phase fails, the system lacks a formal mechanism to "roll back" to a specific previous state or "retry" from a specific checkpoint. A formal state machine allows for deterministic transitions, easier debugging, and the ability to inject "recovery states" if a phase fails.

## Implementation Steps
1.  **Define States:** Create an `Enum` for `CycleState` (e.g., `START`, `PHASE_I`, `PHASE_II`, ..., `SUCCESS`, `FAILED`).
2.  **Transition Table:** Implement a `TransitionTable` dictionary mapping `(CurrentState, Event) -> NextState`.
3.  **Refactor `run_cycle`:** Replace the linear execution with a `while` loop that consumes events and executes the corresponding phase function based on the current state.
4.  **Integrate Guards:** Add pre-transition checks (e.g., `self_check`) as part of the transition logic.

## Risk
**Failure Mode:** The transition logic might enter an infinite loop if a state transition is misconfigured or if a phase fails to trigger the next event.
**Mitigation:** Implement a `max_transitions` counter to break the loop if the cycle exceeds a reasonable number of steps, and ensure `_rollback()` is called if the state machine enters an undefined state.

**Confidence Score:** 8/10