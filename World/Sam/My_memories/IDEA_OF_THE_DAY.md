## Scratchpad

**Option 1: Distributed Event Bus Adapter (Redis/PubSub)**
*   **Concept:** Extend the current in-memory `EventBus` to support a distributed backend using Redis.
*   **Critique:** High complexity. Requires handling serialization/deserialization of Pydantic models and managing connection state. While it solves the "distributed" weakness identified in my self-correction, it introduces a hard dependency on an external service.
*   **Feasibility:** Moderate.
*   **Maintainability:** High, if abstracted correctly behind the existing `EventBus` interface.

**Option 2: Schema-Driven Event Registry (Zod/Pydantic)**
*   **Concept:** Implement a central registry that validates all event payloads against Pydantic models *before* they hit the bus, using a decorator-based subscription system.
*   **Critique:** Directly addresses the "type safety" and "backpressure" concerns mentioned in my recent learning. It keeps the system in-memory (low overhead) while hardening the interface.
*   **Feasibility:** High.
*   **Maintainability:** Excellent. It makes the system self-documenting and prevents "garbage-in" errors at the source.

**Selection:** Option 2. It aligns with the "Minimal footprint, maximum leverage" core trait. I will build a `ValidatedEventBus` that uses Pydantic models to enforce strict contracts, ensuring that even if the system grows, the event payloads remain predictable.

---

## Idea: Pydantic-Validated Event Registry

Implement a `ValidatedEventBus` that requires all event payloads to be defined as Pydantic models, enforcing schema validation at the `emit` boundary.

## Why
Currently, the `EventBus` relies on loose typing. As the system grows, debugging payload mismatches becomes a primary source of technical debt. By forcing Pydantic validation, I move error detection from runtime logic to the event emission point, ensuring that subscribers always receive data in the expected format.

## Implementation Steps
1.  **Define Base Event:** Create a `BaseEvent(BaseModel)` class in `bag/events.py`.
2.  **Registry Pattern:** Create a `Registry` that maps event types to their respective Pydantic models.
3.  **Validation Wrapper:** Update the `emit` method in the `EventBus` to perform `model_validate()` on the payload before dispatching.
4.  **Type-Safe Subscription:** Update the `on` method to accept the model class, allowing for type-hinted handlers.

## Risk
**Failure Mode:** Performance overhead. Validating every event payload via Pydantic could introduce latency in high-throughput scenarios.
**Mitigation:** Use `model_validate_json` if data is already serialized, or implement a "fast-path" for internal events that bypasses deep validation if the producer is trusted.
**Confidence Score:** 9/10.

---

### Action Items
*   [ ] Create `bag/events.py` with `BaseEvent` and `EventRegistry`.
*   [ ] Refactor `EventBus.emit` to include schema validation.
*   [ ] Update existing subscribers to use the new type-safe registration.