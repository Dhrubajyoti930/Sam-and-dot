## Scratchpad

**Option 1: Asyncio-Native Task Orchestrator**
*   **Concept:** Replace the current `_stitch_gemini` and `ask_gemini` synchronous blocking calls with an `asyncio`-based task queue.
*   **Critique:** While this aligns with the "Technical Summary" learned this cycle, it requires a significant refactor of the core `sam.py` event loop. The risk of breaking the `_stitch_gemini` logic is high, and the current synchronous nature of `ask_gemini` is tied to the `semantic_cache` and `_CALL_DELAY` logic.
*   **Trade-off:** High architectural gain for I/O efficiency, but high risk of introducing race conditions in state-saving.

**Option 2: Structured Pydantic-Driven Patching**
*   **Concept:** Refactor `apply_patch_operations` to use `Instructor` (or a Pydantic-based schema) to validate patch operations before execution.
*   **Critique:** This directly addresses the "Structured Output" market trend. By enforcing a Pydantic schema on the JSON output from Gemini, I can catch malformed patch operations *before* they touch the filesystem, reducing the reliance on `_rollback()` and `_alert_dot`.
*   **Trade-off:** Increases dependency complexity (adding `instructor` or `pydantic`), but significantly improves the reliability of self-modification.

**Selection:** Option 2. It is a surgical, high-leverage improvement that aligns with the "Structured Output" trend and directly improves the safety of my self-modification loop.

---

## Idea: Pydantic-Validated Patch Operations
Implement a Pydantic schema for patch operations and integrate it into `apply_patch_operations` to ensure all incoming patches are structurally sound before execution.

## Why
Currently, `apply_patch_operations` relies on raw JSON parsing. If Gemini returns a malformed operation (e.g., missing an `old` string for a `replace` operation), the system fails at runtime. Enforcing a schema ensures that I only attempt valid, well-formed patches, reducing the frequency of `_rollback()` triggers and improving the robustness of my self-evolution.

## Implementation Steps
1.  Define a `PatchOperation` Pydantic model in `bag/patch_ops.py` with strict validation for `operation` types and required fields.
2.  Update `apply_patch_operations` to validate the incoming list of operations against this model before iterating.
3.  Add a custom validator to ensure `old` and `new` strings are not empty and that `operation` is restricted to the allowed set (`replace`, `insert_after`, `delete`).
4.  Update `_lint_fix_with_gemini` and `_behaviour_fix_with_gemini` to pass the raw JSON through this validator.

## Risk
**Failure Mode:** The Pydantic validation might be too strict, causing valid but slightly unconventional patches to be rejected, leading to "stalled" self-repair cycles.
**Mitigation:** Implement a "soft-fail" log that reports the specific validation error to `log.error` without crashing the entire cycle, allowing me to see exactly why a patch was rejected and adjust the prompt accordingly.

**Confidence Score:** 9/10