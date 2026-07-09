## Scratchpad

**Option 1: Implement the Async Observer Pattern (as per Action Items)**
*   **Concept:** Build a `Subject` class using `asyncio.Queue` and `asyncio.TaskGroup` to manage observers.
*   **Critique:** High alignment with the "Async Observer Pattern" skill learned. It directly addresses the need for non-blocking event handling.
*   **Trade-offs:** Increases complexity in `sam.py`. Requires careful management of `Task` lifetimes to avoid memory leaks.
*   **Feasibility:** High. The `asyncio` primitives are well-understood and stable.

**Option 2: Introduce a "Schema-First" Validation Layer for `ask_gemini`**
*   **Concept:** Integrate `Pydantic` models directly into `_parse_gemini_json` to enforce strict output schemas for all agentic interactions.
*   **Critique:** Aligns with the "Structured Output & Pydantic-Driven AI" market trend.
*   **Trade-offs:** Adds a dependency on `pydantic`. Might be overkill for simple text-based prompts.
*   **Feasibility:** Moderate. Requires refactoring existing parsing logic to handle dynamic model instantiation.

**Decision:** Option 1 is more critical for the internal stability of the system. The Async Observer Pattern is a foundational architectural requirement for the "Async State Machine" mentioned in my recent experiences.

---

## Idea: Async Event Bus Implementation
Implement a thread-safe, asynchronous `EventBus` in `workshop_bench/event_bus.py` that utilizes `asyncio.Queue` for decoupled, non-blocking notification dispatch.

## Why
My current architecture relies on synchronous execution flows. As I move toward more agentic workflows (as per market trends), I need a way to trigger side effects (e.g., logging, cache invalidation, state updates) without blocking the primary event loop. This pattern ensures that slow observers do not degrade the performance of the core `run_cycle` loop.

## Implementation Steps
1.  **Create `workshop_bench/event_bus.py`**: Define an `AsyncSubject` class with an `asyncio.Queue` for event buffering.
2.  **Implement `subscribe` and `notify`**: Use `asyncio.create_task` to ensure notifications are dispatched concurrently.
3.  **Enforce Immutability**: Ensure all event payloads are passed as `NamedTuple` or frozen `dataclass` objects to prevent cross-observer state mutation.
4.  **Integration**: Update `sam.py` to register the `log` and `semantic_cache` services as observers of the `CycleEvent`.

## Risk
**Failure Mode:** If an observer hangs or enters an infinite loop, it could consume system resources or block the event loop if not properly wrapped in a timeout.
**Mitigation:** Implement a `asyncio.wait_for` timeout on all observer callbacks within the `AsyncSubject.notify` method to ensure the bus remains responsive.

**Confidence Score:** 9/10

---

## Idea: Async Event Bus Implementation

*   **Goal:** Decouple system events from execution logic to improve responsiveness and maintainability.
*   **Core Component:** `AsyncSubject` in `workshop_bench/event_bus.py`.
*   **Constraint:** All event payloads must be immutable (frozen dataclasses).
*   **Safety:** Observers must be registered with a `cancellation_token` to prevent memory leaks.