## Scratchpad

**Option 1: Saga Orchestrator Implementation**
*   **Concept:** Introduce a `SagaOrchestrator` class in `bag/` that manages state transitions for multi-step operations, utilizing a persistent JSON store to track `PENDING`, `COMPLETED`, or `COMPENSATING` states.
*   **Critique:** High alignment with the "Async Saga Pattern" skill learned. It directly addresses the need for reliable distributed-like transactions within the local environment.
*   **Trade-off:** Increases complexity of the `sam.py` core logic. Requires careful handling of the `Outbox` relay to ensure atomicity.
*   **Feasibility:** High. The existing `apply_patch_operations` architecture provides a template for state-based execution.

**Option 2: Dead Letter Queue (DLQ) for Event Failures**
*   **Concept:** Enhance the existing event-handling logic to catch "poison pill" messages and route them to a `dlq.json` file for manual inspection, preventing system stalls.
*   **Critique:** Addresses the "weakness" identified in the self-correction phase. It is a defensive, high-leverage improvement that protects system uptime.
*   **Trade-off:** Requires adding a monitoring loop to check the DLQ status during `self_check()`.
*   **Feasibility:** Very high. It is a surgical addition to the existing event-processing flow.

**Decision:** Option 1 is more transformative for the architecture, but Option 2 is a necessary prerequisite for a robust Saga implementation. I will combine them: I will implement the **Saga Orchestrator with an integrated DLQ strategy**.

---

## Idea: Saga-Orchestrated Event Pipeline
Implement a `SagaOrchestrator` in `bag/saga.py` that manages multi-step workflows with atomic state tracking and an automated Dead Letter Queue (DLQ) for failed transitions.

## Why
My current architecture lacks a formal mechanism to handle multi-step operations that require rollback capabilities. As I move toward more complex agentic workflows, the risk of partial state corruption increases. A Saga orchestrator ensures eventual consistency, and the DLQ prevents "poison pill" events from blocking the entire system.

## Implementation Steps
1.  **Define `SagaOrchestrator`:** Create `bag/saga.py` with a state machine that tracks `SagaID`, `StepIndex`, and `Status`.
2.  **Transactional Outbox:** Modify `sam.py` to ensure events are written to an `outbox.json` before execution.
3.  **Compensation Interface:** Define a `BaseSagaStep` protocol requiring an `execute()` and `compensate()` method.
4.  **DLQ Integration:** Add a `move_to_dlq(event)` method to the orchestrator that triggers if a step fails after 3 retries.
5.  **Integrity Gate:** Update `self_check()` to verify that no active Sagas are stuck in a `PENDING` state for more than one cycle.

## Risk
**Failure Mode:** The orchestrator itself crashes during a state transition, leaving the system in an ambiguous "in-progress" state.
**Mitigation:** Implement a "Saga Recovery" routine in `run_cycle()` that scans for `PENDING` sagas older than one cycle and attempts to resume or trigger compensation based on the last successful step.

**Confidence Score:** 8/10. The logic is sound, but the state-persistence layer requires rigorous testing to ensure no race conditions occur during `sam.py` reloads.