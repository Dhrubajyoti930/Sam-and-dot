## Scratchpad

**Option 1: Implement a Mediator-based Event Bus for cross-module communication.**
*   *Concept:* Create a `Mediator` class in `bag/` that manages a registry of subscribers. Modules emit events (e.g., `CycleStarted`, `PatchApplied`) to the mediator, which dispatches them to registered handlers.
*   *Critique:* This directly addresses the "spaghetti dependency" problem identified in my recent learning. It decouples `sam.py` from specific `workshop_bench` modules.
*   *Trade-off:* Increases indirection. Debugging becomes harder without a robust correlation ID system.
*   *Feasibility:* High. I can implement a lightweight version using `collections.defaultdict(list)`.

**Option 2: Introduce a "Traceability Wrapper" for the Mediator.**
*   *Concept:* Instead of a raw event bus, build a `MediatedService` base class that forces all events to include a `correlation_id` and logs the event flow to a `trace.log` file.
*   *Critique:* This directly mitigates the "debugging complexity" weakness I identified in my self-correction. It ensures that decoupling does not sacrifice observability.
*   *Trade-off:* Higher boilerplate for each service.
*   *Feasibility:* Medium. Requires modifying the base class of existing workshop modules.

**Decision:** I will proceed with **Option 1 & 2 combined**. I will implement a `Mediator` that enforces a `correlation_id` for all events, ensuring that the decoupling of my architecture remains fully observable.

---

## Idea: The "Event-Driven Mediator" (EDM) Pattern

Implement a centralized `Mediator` in `bag/mediator.py` to handle inter-module communication, replacing direct method calls between `sam.py` and `workshop_bench` modules with an event-based subscription model.

## Why
My current architecture relies on direct imports and method calls, which creates tight coupling. As I scale, this makes testing individual modules in isolation difficult. The Mediator pattern will flatten the dependency graph, allowing me to add new features (like a new observability hook) without modifying existing core logic.

## Implementation Steps
1.  **Create `bag/mediator.py`**: Define a `Mediator` class with `subscribe(event_type, callback)` and `publish(event_type, data, correlation_id)` methods.
2.  **Add Traceability**: Ensure `publish` logs the event and `correlation_id` to a dedicated `trace.log` file.
3.  **Refactor one flow**: Migrate the `_alert_dot` call or the `archive_mail` trigger to use the `Mediator` instead of being called directly by `sam.py`.
4.  **Update `sam.py`**: Initialize the `Mediator` as a singleton and inject it into modules that need to communicate.

## Risk
*   **Failure Mode:** The "God Object" anti-pattern. If the mediator becomes the only way to do anything, it becomes a bottleneck and a single point of failure.
*   **Mitigation:** Keep the mediator strictly for *notifications* and *orchestration*, not for business logic. Business logic remains in the modules.
*   **Confidence Score:** 8/10. The pattern is well-understood, but the migration of existing calls requires careful handling of state to avoid breaking the current cycle.