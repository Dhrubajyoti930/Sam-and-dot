## Scratchpad

**Option 1: Event-Driven Seam Implementation (Middleware)**
*   **Concept:** Introduce an `EventBus` class that acts as a central dispatcher for internal state changes, allowing components to subscribe to events rather than calling each other directly.
*   **Critique:** High architectural leverage. It creates a "seam" for testing by allowing me to inject a mock bus and verify that events were emitted. However, it risks over-engineering if the current system doesn't have enough asynchronous complexity to justify the overhead.
*   **Feasibility:** Moderate. Requires refactoring `run_cycle` to emit lifecycle events.

**Option 2: TimeProvider Interface (DI for Time)**
*   **Concept:** Replace all `datetime.datetime.utcnow()` calls with a `TimeProvider` class injected into constructors.
*   **Critique:** Directly addresses the "seam" learning from this cycle. It makes time-dependent logic (like `review_due_cycle` in Phase II) deterministic and testable.
*   **Feasibility:** High. It is a surgical change that touches a specific, well-defined dependency.

**Selection:** Option 2. It is a cleaner, more focused application of the "Seam Points" skill learned this cycle. It avoids the complexity of an event bus while providing immediate, high-value testability for the Spaced Repetition engine.

---

## Idea: TimeProvider Dependency Injection

Implement a `TimeProvider` protocol and a concrete `SystemTimeProvider` to abstract system clock access, enabling deterministic testing of time-sensitive logic.

## Why
Currently, `phase_ii_spaced_repetition` and `phase_vii_state_saving` rely on `datetime.datetime.utcnow()`. This makes it impossible to unit test the Spaced Repetition logic without waiting for real-world time to pass. By injecting a `TimeProvider`, I can mock the "current" cycle time in `bag/tests.py` to verify that knowledge reviews trigger exactly when expected.

## Implementation Steps
1.  **Define Protocol:** Create `bag/time_utils.py` with a `TimeProvider` protocol defining `now() -> datetime`.
2.  **Implement Concrete:** Add `SystemTimeProvider` in the same file.
3.  **Refactor:** Update `sam.py` to instantiate a `TimeProvider` and pass it to Phase II/VII functions (or store it in a global config if DI is too invasive for the current structure).
4.  **Test:** Add a test case in `bag/tests.py` using a `MockTimeProvider` to verify that `review_due_cycle` logic behaves correctly when the "clock" is advanced.

## Risk
**Failure Mode:** If I fail to update all instances of `datetime.datetime.utcnow()`, the system will have split-brain time logic, leading to inconsistent state logs.
**Mitigation:** Use `grep` to identify all occurrences of `datetime.datetime` before refactoring and ensure the `TimeProvider` is the only allowed way to access time in the future.

**Confidence Score:** 9/10