## Scratchpad

**Option 1: Type-Safe Dependency Injection (DI) Container**
*   **Concept:** Replace manual instantiation in `sam.py` with a lightweight, `Protocol`-based DI container.
*   **Critique:** While it improves testability and decoupling, it introduces a "magic" layer that makes the control flow harder to trace. Given Sam's current size, the complexity overhead likely outweighs the benefits of decoupling.
*   **Feasibility:** High, but potentially over-engineered.

**Option 2: Static Analysis-Driven "Type-Safety Gate"**
*   **Concept:** Extend `self_check()` to include a `mypy` pass in `--strict` mode, specifically targeting the `workshop_bench/` modules.
*   **Critique:** This aligns perfectly with the current cycle's focus on Python Type Hinting. It leverages existing tools (`mypy`) rather than building new infrastructure. It directly addresses the "Any" trap mentioned in the skill summary.
*   **Feasibility:** Very high. It is a natural evolution of the existing `self_check()` integrity gate.

**Decision:** Option 2. It reinforces the architectural integrity of the workshop modules without introducing runtime overhead or unnecessary abstraction.

---

## Idea: Strict Type-Safety Gate for Workshop Modules

Implement a `mypy` integration within `self_check()` to enforce strict type checking on all files within `workshop_bench/`.

## Why
The current `self_check()` relies on `ruff` (syntax/logic) and `py_compile`. This catches crashes but ignores type-safety violations that lead to runtime `AttributeError` or `TypeError`. By enforcing `mypy --strict` on the workshop modules, I ensure that my autonomous code generation adheres to the type contracts I define, reducing the "Any" trap and improving long-term maintainability.

## Implementation Steps
1.  **Modify `self_check()`:** Add a subprocess call to `mypy` targeting `workshop_bench/` with `--strict` and `--ignore-missing-imports` flags.
2.  **Update `self_check()` logic:** If `mypy` returns a non-zero exit code, log the output and trigger `_rollback()` to maintain the "never break the build" invariant.
3.  **Refactor `workshop_bench/`:** Add type hints to the most frequently used utility modules in the workshop to satisfy the new strict gate.

## Risk
**Failure Mode:** `mypy` might be too aggressive, flagging valid but complex dynamic patterns (e.g., `getattr` usage) as errors, leading to constant rollbacks.
**Mitigation:** Use a `mypy.ini` or inline `# type: ignore` comments for known dynamic patterns, and ensure the gate only triggers on `workshop_bench/` initially to isolate the impact.

**Confidence Score:** 9/10

---

## Proposed Development Idea: Strict Type-Safety Gate

```json
{
  "task": "Integrate mypy --strict into self_check() for workshop_bench/ modules.",
  "priority": "high"
}
```

*Self-Correction:* I must ensure `mypy` is installed in the environment. If `mypy` is missing, the gate should gracefully degrade to the existing `ruff` check rather than failing the entire cycle. I will add a check for the `mypy` executable before invoking it.