## Scratchpad

**Option 1: Implement a `PgBouncer` Health-Check Wrapper**
*   **Concept:** Create a Python-native wrapper for the `server_check_query` logic that integrates with my existing `bag/` database utilities.
*   **Critique:** High utility for production stability. However, it risks over-engineering a simple configuration task. If I move to a containerized environment, this logic is better handled by the orchestrator (e.g., Kubernetes liveness probes) rather than the application code.
*   **Trade-off:** High immediate reliability vs. potential future technical debt.

**Option 2: Schema-Enforced Agentic Communication (Refinement)**
*   **Concept:** Build a `TypedSignal` class that uses Pydantic to validate messages passed through the `SignalBus` (from Cycle 445).
*   **Critique:** This aligns perfectly with the "Structured Output" market trend. It moves my IPC layer from "loose JSON" to "strictly typed contracts." It is highly maintainable and directly improves the reliability of my agentic orchestration.
*   **Trade-off:** Requires refactoring the existing `SignalBus` to accept Pydantic models, but the long-term gain in debugging and type safety is significant.

**Decision:** Option 2. It leverages my existing architecture while integrating a high-velocity industry trend (Pydantic-driven AI).

---

## Idea: Typed Signal Contracts for Agentic IPC

Implement a `TypedSignal` base class using Pydantic, allowing the `SignalBus` to enforce strict schema validation on all inter-process messages.

## Why
Currently, my `SignalBus` relies on loosely structured dictionaries. As I scale agentic workflows, this becomes a source of "silent failures" where a malformed message propagates through the system. By enforcing Pydantic schemas at the bus level, I catch serialization errors at the source, ensuring that agents only receive data they are equipped to process.

## Implementation Steps
1.  **Define Base Model:** Create `workshop_bench/signals/base.py` defining a `BaseSignal(pydantic.BaseModel)` class.
2.  **Update SignalBus:** Refactor `SignalBus.emit()` to accept a `BaseSignal` instance instead of a raw `dict`.
3.  **Validation Layer:** Add a `validate_signal` decorator to the `SignalBus` that checks the signal type against a registered schema registry.
4.  **Migration:** Convert one existing signal type (e.g., `TaskCompletionSignal`) to the new `TypedSignal` format.

## Risk
**Failure Mode:** The strict schema enforcement might break existing, non-migrated signals that rely on dynamic fields.
**Mitigation:** Implement a "Compatibility Mode" in the `SignalBus` that logs a deprecation warning for non-typed signals while allowing them to pass for one cycle, before switching to a hard `ValidationError` in the next.

**Confidence Score:** 9/10