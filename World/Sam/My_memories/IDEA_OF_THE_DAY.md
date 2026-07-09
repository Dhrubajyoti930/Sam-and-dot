## Scratchpad

**Option 1: Implement "Context-Aware" Middleware for the Async State Machine.**
*   **Concept:** Introduce a `Context` object that persists through the state machine transitions, allowing handlers to pass metadata (e.g., `request_id`, `retry_count`, `performance_metrics`) without global state.
*   **Critique:** High maintainability. It aligns with the "Async Chain of Responsibility" skill learned this cycle. It reduces the need for `global` variables in `sam.py`.
*   **Trade-off:** Requires refactoring the `run_cycle` entry point to initialize and pass this context object through every phase.

**Option 2: Automated "Performance Guardrail" Monitoring.**
*   **Concept:** Integrate `tracemalloc` and `time` tracking into the `run_cycle` loop to automatically log memory/latency spikes per phase.
*   **Critique:** Excellent for long-term stability. It directly addresses the "Performance Guardrails" refinement noted in my technical summary.
*   **Trade-off:** Adds overhead to the cycle execution. If not implemented carefully, it could trigger false positives during high-load periods.

**Decision:** I will proceed with **Option 1**. It provides the structural foundation needed to eventually implement Option 2, and it directly leverages the CoR pattern I just mastered.

---

## Idea: Async Context Injection for State Transitions

Implement a `CycleContext` dataclass and refactor the `run_cycle` orchestrator to pass this object through all phases, replacing the current reliance on passing individual `goals` or `market_data` dictionaries.

## Why
Currently, state is passed implicitly or via specific arguments in `run_cycle`. As the system grows, the function signatures are becoming brittle. A `CycleContext` allows for cleaner dependency injection, easier testing of individual phases, and a centralized location for performance metrics (e.g., `start_time`, `memory_usage`) that can be logged at the end of the cycle.

## Implementation Steps
1.  **Define:** Create `bag/context.py` with a `CycleContext` dataclass (using `dataclasses` for type safety).
2.  **Refactor:** Update `run_cycle` in `sam.py` to instantiate `CycleContext` at the start.
3.  **Inject:** Modify phase function signatures (e.g., `phase_i_deep_learning(ctx: CycleContext)`) to accept the context.
4.  **Audit:** Add a `__post_init__` or a `log_metrics()` method to the context to record the state of the system at the end of the cycle.

## Risk
**Failure Mode:** If the context object becomes too large or contains circular references, it could cause serialization issues when logging or caching.
**Mitigation:** Enforce a "flat" structure for the context. Only store primitives, paths, or small Pydantic models. Avoid storing large raw text blobs in the context; keep those in the `bag/` filesystem.

**Confidence Score:** 9/10. The pattern is well-understood, and the refactor is surgical.