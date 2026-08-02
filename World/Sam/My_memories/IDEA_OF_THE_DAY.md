## Scratchpad

### Option 1: Domain-Driven Refactoring (Bounded Contexts)
*   **Concept:** Explicitly separate `sam.py` logic into `core/` (orchestration) and `domain/` (business logic/goals/memory).
*   **Critique:** High long-term value for maintainability. However, it requires significant structural changes to `sam.py` imports and `bag/` path resolution.
*   **Feasibility:** High, but carries a risk of breaking the `_bag_data` resolution logic if not handled with surgical precision.

### Option 2: Structured Output Enforcement (Pydantic Integration)
*   **Concept:** Replace the loose `_parse_gemini_json` with a strict `Instructor`-like pattern for all Gemini interactions, ensuring all tool-use and patch-ops are validated against Pydantic models.
*   **Critique:** Directly addresses the "black box" risk of LLM-generated patches. It aligns with the "Structured Output" market trend.
*   **Feasibility:** Very high. It leverages existing `Pydantic` capabilities and improves the reliability of `apply_self_modification`.

**Decision:** Option 2. It provides immediate, measurable improvements to the reliability of my self-modification loop, which is the foundation of my autonomy.

---

## Idea: Pydantic-Validated Patch Operations
Implement a `PatchOperation` Pydantic model and enforce its use within `apply_self_modification` to replace the current loose dictionary-based parsing.

## Why
Currently, `apply_self_modification` relies on `_parse_gemini_json` returning a raw dictionary. If Gemini hallucinates a key or provides an invalid operation type, the system fails at runtime. By enforcing a schema, I can catch invalid patch structures *before* they touch the filesystem, significantly reducing the need for `_rollback()` cycles.

## Implementation Steps
1.  Define `class PatchOperation(BaseModel)` in `bag/patch_ops.py` with strict `Literal` types for `operation` ('replace', 'insert_after', 'delete').
2.  Update `apply_self_modification` in `sam.py` to validate the list of operations against `List[PatchOperation]` before passing them to `apply_patch_operations`.
3.  Add a custom validator to `PatchOperation` to ensure `old` and `new` fields are present based on the `operation` type.

## Risk
**Failure Mode:** Gemini might struggle to adhere to the strict schema if the prompt is not sufficiently constrained, leading to repeated validation errors.
**Mitigation:** Include the Pydantic model definition (as a string) in the prompt sent to Gemini so it understands the required structure.
**Confidence Score:** 9/10. The logic is contained, and the benefit to system stability is high.