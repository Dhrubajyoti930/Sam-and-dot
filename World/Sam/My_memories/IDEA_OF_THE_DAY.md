## Scratchpad

**Option 1: Supervisor-Worker State Machine (Hierarchical)**
*   **Concept:** Implement a `Supervisor` class in `workshop_bench/` that manages a `State` object (Pydantic model) and delegates tasks to specialized `Worker` agents.
*   **Critique:** High architectural value, aligns with current market trends (LangGraph-like patterns).
*   **Trade-off:** Increases complexity of the `sam.py` orchestration logic. Requires careful state serialization to ensure persistence across cycles.
*   **Feasibility:** High, given existing Pydantic integration.

**Option 2: Semantic Tool Routing (Dynamic)**
*   **Concept:** Replace static tool selection with a semantic router that uses embeddings to match user intent to the most relevant `workshop_bench` module.
*   **Critique:** Improves flexibility but introduces a dependency on an embedding model/service.
*   **Trade-off:** Adds latency and potential for "routing hallucinations."
*   **Feasibility:** Moderate; requires integrating with the existing `semantic_cache` infrastructure.

**Selection:** Option 1. It directly addresses the "Multi-Agent Orchestration" skill learned this cycle and provides a robust foundation for future autonomous growth.

---

## Idea: Supervisor-Worker Orchestration Layer
Implement a `Supervisor` agent in `workshop_bench/orchestrator.py` that utilizes a `TaskState` Pydantic model to track sub-task progress, worker assignments, and a "Human-in-the-loop" (HITL) approval gate.

## Why
Current task execution is monolithic. Moving to a hierarchical structure allows me to decompose complex refactoring tasks into discrete, verifiable steps, reducing the risk of cascading failures during self-modification.

## Implementation Steps
1.  **Define Schema:** Create `workshop_bench/schemas.py` with `TaskState` (status, worker_id, result, approval_required).
2.  **Supervisor Logic:** Create `workshop_bench/orchestrator.py` to handle task decomposition and state updates.
3.  **Approval Gate:** Add a check in `sam.py` that pauses execution if `TaskState.approval_required` is `True`, writing a summary to `MAIL_OUT` for Dot.
4.  **Integration:** Update `apply_self_modification` to route through the `Supervisor` rather than direct execution.

## Risk
**Failure Mode:** The `Supervisor` enters an infinite loop of task re-assignment if a `Worker` fails to provide a valid output.
**Mitigation:** Implement a "Max-Retry" counter in the `TaskState` and a fallback to a "Human-intervention" state if the threshold is exceeded.

**Confidence Score:** 8/10. The logic is sound, but the state-machine transition requires precise handling of the `sam.py` lifecycle.