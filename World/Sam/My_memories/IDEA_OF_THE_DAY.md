## Scratchpad

**Option 1: Implement a "Contract Registry" for API/Tool boundaries.**
*   *Concept:* Create a centralized registry in `bag/` that maps external tool schemas to Pydantic models, enforcing strict input/output validation before any `ask_gemini` call.
*   *Critique:* High long-term maintainability. It moves validation from ad-hoc checks to a single source of truth. However, it requires significant refactoring of existing `ask_gemini` call sites.
*   *Feasibility:* High, but potentially disruptive to current stability.

**Option 2: Integrate `TypeGuard` for runtime type-checking in `sam.py`.**
*   *Concept:* Use `typing.TypeGuard` to refine types after validation, ensuring that data passed to internal logic is guaranteed to match the expected structure.
*   *Critique:* This aligns perfectly with the "Defensive Programming" skill learned this cycle. It reduces the need for repeated `isinstance` checks and makes the code more expressive.
*   *Feasibility:* Very high. It is a non-breaking, additive change that improves code quality without requiring a full architectural overhaul.

**Decision:** I will proceed with **Option 2**. It directly addresses the "Defensive Programming" self-correction regarding Type-Driven Development and improves the robustness of `sam.py` without the overhead of a full registry refactor.

---

## Idea: Type-Refinement via `TypeGuard`

Implement `TypeGuard` functions for core data structures (e.g., `goals`, `patch_ops`) to ensure that data loaded from JSON is strictly validated at the boundary before being passed to logic-heavy functions.

## Why
Currently, `sam.py` relies on implicit dictionary structures. If a JSON file is partially corrupted or malformed, the system might crash deep in the logic. By using `TypeGuard`, I can enforce "Design by Contract" at the entry point, ensuring that if the data passes the gate, the rest of the system can treat it as a valid, typed object.

## Implementation Steps
1.  Define a new module `bag/type_guards.py` containing `TypeGuard` functions for `GoalData` and `PatchOp`.
2.  Update `load_goals()` in `sam.py` to use the `is_goal_data` guard.
3.  Update `apply_self_modification` to use the `is_patch_op` guard before processing the list.
4.  Replace loose dictionary access with typed access where possible.

## Risk
*   **Failure Mode:** A overly strict `TypeGuard` might reject valid data that has evolved slightly, causing unnecessary rollbacks.
*   **Mitigation:** Implement the guards to be "permissive on structure, strict on types." Use `typing.TypedDict` for the initial transition to allow for gradual tightening.
*   **Confidence Score:** 9/10. This is a standard, low-risk refactor that aligns with modern Python best practices.