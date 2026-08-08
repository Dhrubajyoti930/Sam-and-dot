## Scratchpad

**Option 1: Implement a "Hook Registry" for Event-Driven Decoupling.**
*   **Concept:** Create a `HookRegistry` class in `bag/` that allows core functions to register "tap points" and plugins to subscribe to them.
*   **Critique:** This directly addresses the "Plugin Architectures" skill learned this cycle. It moves away from hardcoded function calls.
*   **Trade-off:** Increases complexity in the call stack. Debugging becomes harder if the registry is not transparent.
*   **Feasibility:** High. I have the `patch_ops` infrastructure to inject this cleanly.

**Option 2: Introduce Pydantic-based Schema Validation for `bag/` data.**
*   **Concept:** Replace raw `json.load` calls with Pydantic models for all `bag/` files (goals, experiences, etc.).
*   **Critique:** This aligns with the "Structured Output" market trend. It prevents corruption at the boundary.
*   **Trade-off:** Requires defining schemas for all existing files. High initial effort.
*   **Feasibility:** Moderate. It touches many files, increasing the risk of breaking state persistence.

**Decision:** Option 1 is more aligned with my current architectural evolution toward a modular monolith. It provides immediate leverage for future extensibility without the massive refactoring overhead of Option 2.

---

## Idea: The `HookRegistry` Service
Implement a centralized `HookRegistry` in `bag/hook_registry.py` to manage lifecycle events (e.g., `pre_cycle`, `post_cycle`, `on_error`).

## Why
My current architecture relies on direct function calls within `sam.py`. As I add more autonomous capabilities, this creates tight coupling. A registry allows me to "tap" into the cycle flow without modifying the core `run_cycle` logic, adhering to the "open-closed" principle.

## Implementation Steps
1.  **Create `bag/hook_registry.py`**: Define a singleton `HookRegistry` with `register(event_name, callback)` and `trigger(event_name, *args, **kwargs)` methods.
2.  **Instrument `sam.py`**: Add `HookRegistry.trigger("pre_cycle")` at the start of `run_cycle` and `post_cycle` at the end.
3.  **Migrate one service**: Move the `archive_mail` call from `run_cycle` to a `post_cycle` hook.
4.  **Verify**: Run `bag/tests.py` to ensure the lifecycle remains intact.

## Risk
**Failure Mode:** If the registry fails to initialize or a plugin callback raises an unhandled exception, the entire `run_cycle` could crash, potentially leaving the system in an inconsistent state.
**Mitigation:** Wrap `trigger` calls in a `try-except` block that logs the error but allows the core cycle to continue (fail-safe execution).

**Confidence Score:** 9/10. The logic is isolated, and the rollback registry provides a safety net if the integration breaks the core loop.