## Scratchpad

### Option 1: Implement `functools.lru_cache` on `_bag_data` and `load_goals`
*   **Concept:** Memoize file-system-heavy utility functions to reduce I/O overhead during the cycle.
*   **Critique:** `_bag_data` relies on `bag.bag_paths.resolve`, which might change if the environment shifts. `load_goals` is frequently updated; caching it could lead to stale state if not invalidated correctly.
*   **Feasibility:** High.
*   **Trade-off:** Performance gain vs. risk of stale state.

### Option 2: Refactor Event-Bus Callbacks with `functools.partial`
*   **Concept:** Replace complex `lambda` expressions in the event-bus (or similar dispatchers) with `partial` for better readability and stack-trace clarity.
*   **Critique:** This directly aligns with the "Skill learned this cycle" and improves maintainability. It is a surgical, low-risk refactor that cleans up technical debt.
*   **Feasibility:** Very High.
*   **Trade-off:** Minimal impact on performance, high impact on code quality.

**Decision:** I will proceed with **Option 2**. It is a cleaner, more "Pythonic" approach to callback management that aligns with my current learning trajectory.

---

## Idea: Functional Callback Refactoring
Refactor the event-bus and utility callback patterns to replace `lambda` closures with `functools.partial`.

## Why
`lambda` functions are anonymous and often obscure the intent of the callback. `functools.partial` provides a clear, declarative way to pre-configure functions, making the code easier to debug and more readable for future maintenance.

## Implementation Steps
1.  Scan the codebase for `lambda` expressions used as callbacks or event handlers.
2.  Identify candidates where `partial` can replace the `lambda` (e.g., `lambda: func(arg)` becomes `partial(func, arg)`).
3.  Apply the refactor using `apply_self_modification` to ensure atomic updates.
4.  Run `behaviour_check()` to ensure no regressions in event dispatching.

## Risk
**Failure Mode:** If a callback relies on late-binding (where the `lambda` captures a variable that changes value), replacing it with `partial` (which binds arguments immediately) will break the logic.
**Mitigation:** I will verify that all targeted `lambda` expressions are static or intended for immediate binding before applying the patch.
**Confidence Score:** 9/10