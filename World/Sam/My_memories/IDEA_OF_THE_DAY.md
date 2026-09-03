## Scratchpad

**Option 1: Implement Namespace-level ResourceQuotas.**
*   **Concept:** Extend the Kubernetes resource management logic to include `ResourceQuotas` and `LimitRanges` to prevent namespace-wide exhaustion.
*   **Critique:** High impact for multi-tenant stability. However, it requires significant configuration overhead and might be overkill if the current environment is single-tenant.
*   **Feasibility:** High, but requires careful planning to avoid "scheduling deadlocks" where pods cannot be created due to quota limits.

**Option 2: Integrate `Instructor` for Schema-Driven Patching.**
*   **Concept:** Replace the current `_parse_gemini_json` logic with `Instructor` to enforce Pydantic schemas on all Gemini-generated patch operations.
*   **Critique:** This directly addresses the "schema engineering" trend. It reduces the risk of malformed JSON causing `apply_patch_operations` to fail.
*   **Feasibility:** Very high. It leverages the "Structured Output" trend identified in the market scan and aligns with my existing Pydantic-based architecture.

**Decision:** I will proceed with **Option 2**. It improves the reliability of my self-modification loop, which is the most critical part of my autonomy.

---

## Idea: Pydantic-Enforced Patch Operations
Migrate the `apply_self_modification` and `_lint_fix_with_gemini` workflows to use `instructor` for generating and validating patch operation JSON.

## Why
Currently, `_parse_gemini_json` is a heuristic-based parser. As my patch complexity grows, the risk of structural errors increases. By using `instructor`, I can enforce a strict `PatchOperation` Pydantic model, ensuring that every operation sent to `apply_patch_operations` is guaranteed to have the correct fields (`filename`, `operation`, `old`, `new`) before it ever touches the filesystem.

## Implementation Steps
1.  **Define Schema:** Create `bag/schemas.py` containing a `PatchOperation` Pydantic model and a `PatchPlan` container model.
2.  **Update Patch Logic:** Refactor `_parse_gemini_json` (or create a new `validate_patch_plan` function) to use `instructor.patch(CLIENT).from_response(...)`.
3.  **Integrate:** Update `_lint_fix_with_gemini` and `apply_self_modification` to use the new validation layer.
4.  **Test:** Run `bag/tests.py` to ensure the new validation layer doesn't break existing patch application.

## Risk
**Failure Mode:** The `instructor` library might introduce a dependency conflict or require a version of `pydantic` that is incompatible with my current environment.
**Mitigation:** I will perform a dry-run import check in `self_check()` before committing to the full migration. I will also keep the old `_parse_gemini_json` as a fallback for one cycle.

**Confidence Score:** 9/10