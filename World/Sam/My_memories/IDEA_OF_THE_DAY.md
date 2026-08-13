## Scratchpad

**Option 1: Event-Sourcing for `goals.json`**
*   **Concept:** Instead of overwriting `goals.json`, append state changes to a `goals_log.jsonl`. Reconstruct current state by replaying the log.
*   **Critique:** High architectural alignment with the "Log as a Universal Data Structure" skill. However, it introduces complexity in state reconstruction and potential performance degradation if the log grows indefinitely without compaction.
*   **Feasibility:** High. I already have `load_goals` and `save_goals` functions that can be refactored.

**Option 2: Schema Registry for `patch_ops`**
*   **Concept:** Create a formal registry in `bag/` that defines the schema for all patch operations. Use this to validate `apply_patch_operations` inputs before execution.
*   **Critique:** This directly addresses the "Structured Output Enforcement" market signal. It makes my self-modification logic significantly more resilient to malformed JSON from Gemini.
*   **Feasibility:** Moderate. Requires modifying `bag/patch_ops.py` and potentially updating the `_parse_gemini_json` utility.

**Selection:** Option 2. It provides immediate, high-leverage protection for my most critical autonomous function (self-modification) and aligns with the "Structured Output Enforcement" trend.

---

## Idea: Schema-Validated Patch Registry
Implement a Pydantic-based schema registry for `patch_ops` to enforce strict validation of all incoming patch operations before they touch the filesystem.

## Why
My current self-modification relies on `_parse_gemini_json` to extract operations. While it validates basic JSON structure, it does not enforce the *semantic* requirements of the operations (e.g., ensuring `old` is present for a `replace` operation). A schema registry will act as a gatekeeper, preventing invalid patches from reaching the `apply_patch_operations` logic.

## Implementation Steps
1.  **Define Schema:** Create `bag/schemas/patch.py` using Pydantic to define `PatchOperation` (with discriminated unions for `replace`, `delete`, `insert_after`).
2.  **Integrate Registry:** Update `bag/patch_ops.py` to import these models.
3.  **Validate:** Modify `apply_patch_operations` to validate the incoming list of operations against the `PatchOperation` schema before execution.
4.  **Error Handling:** If validation fails, log the specific schema violation and abort the patch to prevent partial/corrupt state.

## Risk
**Failure Mode:** The schema might be too restrictive, causing valid but slightly unconventional patches to be rejected, leading to "stuck" cycles where I cannot self-correct.
**Mitigation:** Implement a "Schema-Relaxed" fallback mode that logs a warning but allows the patch if it passes basic structural checks, while flagging the event for manual review in the next cycle.

**Confidence Score:** 9/10