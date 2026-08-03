## Scratchpad

**Option 1: Implement a "Semantic Lock" Manager for Saga Transactions.**
*   *Concept:* Create a `bag/lock_manager.py` that handles the `PENDING` state for distributed operations, ensuring that if a Saga is interrupted, the system can query the lock manager to resume or trigger compensation.
*   *Critique:* High architectural value for reliability. However, it requires modifying the `apply_patch_operations` flow to check for locks before execution. It might be overkill if I don't have enough distributed services yet.
*   *Feasibility:* High, but requires careful state persistence.

**Option 2: Integrate a Lightweight Workflow Engine (Temporal-lite).**
*   *Concept:* Introduce a simple state-machine decorator in `sam.py` to track multi-step tasks (e.g., `phase_v_development` -> `apply_patch` -> `self_check`).
*   *Critique:* This directly addresses the "Orchestration" pattern learned this cycle. It makes the `run_cycle` logic more robust against mid-cycle failures.
*   *Feasibility:* Moderate. It requires refactoring the monolithic `run_cycle` into discrete, state-aware steps.

**Decision:** Option 2 is superior for long-term maintainability. By moving from a procedural `run_cycle` to an orchestrated state machine, I gain the ability to resume from the exact point of failure, which is the core benefit of the Saga pattern.

---

## Idea: Orchestrated State-Machine for Cycle Execution

Transition `run_cycle()` from a linear procedural execution to a state-machine-based orchestrator. Each phase (I–VII) will be registered as a state with defined transitions, success criteria, and a "compensating" rollback function.

## Why
Currently, if `run_cycle` fails at Phase V, the state is inconsistent. An orchestrator allows me to persist the "current phase" in `bag/cycle_status.json`. If a failure occurs, the next cycle can detect the interrupted state and either resume or perform a clean rollback, aligning with the Saga pattern's requirement for eventual consistency.

## Implementation Steps
1.  **Define State Schema:** Create a `CycleState` Pydantic model in `sam.py` to track `current_phase`, `data_context`, and `retry_count`.
2.  **Refactor `run_cycle`:** Replace the linear call stack with a `while` loop that executes the current state and updates the status file.
3.  **Persistence:** Update `run_cycle` to write the `CycleState` to `bag/cycle_status.json` before and after each phase.
4.  **Recovery Logic:** Add a `recover_state()` function at the start of `run_cycle` that checks for an existing `cycle_status.json` and resumes from the last successful phase.

## Risk
*   **Failure Mode:** The state machine itself could enter an infinite loop if a phase consistently fails and triggers a retry without incrementing a counter.
*   **Mitigation:** Implement a `max_retries` limit per phase in the `CycleState` model. If exceeded, the orchestrator must force a full rollback and alert Dot.
*   **Confidence Score:** 8/10. The logic is sound, but the refactor of `run_cycle` is invasive and requires precise anchor points to avoid breaking existing functionality.