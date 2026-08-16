## Scratchpad

### Option 1: Implementing a Localized "Agentic RAG" Controller
*   **Concept:** Replace the current `ask_gemini` logic with a local orchestration layer using `LangGraph` concepts to manage stateful tool-use (e.g., searching `bag/` files before calling Gemini).
*   **Critique:** High complexity. While it aligns with the "Agentic Workflow" market signal, it risks over-engineering the core `sam.py` loop. The current `ask_gemini` is stable; replacing it introduces significant regression risk.
*   **Feasibility:** Moderate. Requires adding `langgraph` as a dependency, which might violate the "minimal footprint" rule.

### Option 2: Structured Output Enforcement for `patch_ops`
*   **Concept:** Refactor `apply_patch_operations` to use `PydanticAI` for strict schema validation of incoming JSON patches.
*   **Critique:** This directly addresses the "Structured Output Enforcement" market signal. It improves the reliability of self-modification by ensuring the JSON structure is validated *before* the patch logic executes, rather than relying on `_parse_gemini_json`'s loose parsing.
*   **Feasibility:** High. It leverages existing `Pydantic` usage in the codebase and improves long-term maintainability by hardening the most critical part of my self-evolution loop.

**Decision:** Option 2. It is a surgical, high-leverage improvement that aligns with current industry standards for agentic reliability.

---

## Idea: Pydantic-Validated Patch Schema
Implement a `PatchOperation` Pydantic model in `bag/patch_ops.py` to enforce strict schema validation for all self-modification operations, replacing the current loose dictionary parsing.

## Why
Currently, `_parse_gemini_json` is a "best-effort" parser. If Gemini returns a malformed JSON object, the patch logic might fail silently or partially apply. By enforcing a schema, I ensure that every patch operation is type-safe and structurally sound before it touches the filesystem, reducing the need for `_rollback()` cycles.

## Implementation Steps
1.  Define `class PatchOperation(BaseModel)` in `bag/patch_ops.py` with fields: `filename`, `operation` (Literal['replace', 'delete', 'insert_after']), `old`, and `new`.
2.  Update `apply_patch_operations` to accept a list of `PatchOperation` objects.
3.  Modify `_parse_gemini_json` (or create a helper) to validate the raw JSON against this schema.
4.  Update `_lint_fix_with_gemini` and `_behaviour_fix_with_gemini` to pass the validated objects to the patcher.

## Risk
**Failure Mode:** If the Pydantic schema is too rigid, it may reject valid patches that contain unexpected but harmless keys, causing the self-repair loop to stall.
**Mitigation:** Use `extra='ignore'` in the Pydantic model configuration to allow for future-proofing and flexibility.

**Confidence Score:** 9/10