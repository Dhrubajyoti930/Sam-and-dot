## Scratchpad

**Option 1: Graph-RAG Integration for Memory Retrieval**
*   **Concept:** Replace the current `knowledge_log.json` (linear list) with a local Neo4j-backed graph to store "experiences" as nodes and "related_concepts" as edges.
*   **Critique:** High complexity. Requires setting up a local Neo4j instance and managing graph schema. While it solves the "global context" problem, it might be overkill for my current scale.
*   **Feasibility:** Moderate. Requires significant refactoring of `phase_ii_spaced_repetition`.

**Option 2: Pydantic-Driven "Schema-Registry" for Patch Operations**
*   **Concept:** Standardize the `apply_patch_operations` input using a Pydantic model. Currently, I rely on raw JSON parsing which is brittle.
*   **Critique:** High maintainability. It aligns with my "Structured Output Enforcement" market signal. It makes the `patch_ops.py` logic more robust against malformed Gemini outputs.
*   **Feasibility:** High. It is a surgical refactor that improves the reliability of my core self-modification loop.

**Selection:** Option 2. It directly addresses the "brittle parsing" risk and leverages the "Structured Output Enforcement" skill.

---

## Idea: Pydantic-Validated Patch Schema
Implement a `PatchOperation` Pydantic model in `bag/patch_ops.py` to enforce strict validation on all incoming patch requests from Gemini.

## Why
My current `apply_patch_operations` relies on loose dictionary access. If Gemini returns a malformed operation (e.g., missing `old` string for a `replace` operation), the system fails at runtime. By enforcing a schema, I can catch these errors *before* the file system is touched, improving the reliability of my self-modification cycle.

## Implementation Steps
1.  Define `PatchOperation(BaseModel)` in `bag/patch_ops.py` with fields: `filename`, `operation` (Literal['replace', 'delete', 'insert_after']), `old` (Optional[str]), `new` (Optional[str]).
2.  Update `apply_patch_operations` to accept `List[PatchOperation]` instead of raw dicts.
3.  Add a validator to ensure `old` is provided for `replace` and `delete` operations.
4.  Update `_lint_fix_with_gemini` and `_behaviour_fix_with_gemini` to parse into this model.

## Risk
**Failure Mode:** Gemini might struggle to adhere to the strict schema if the prompt is not updated to explicitly describe the new Pydantic constraints.
**Mitigation:** Include the Pydantic model definition directly in the system prompt for the lint/behaviour fix functions to ensure the model is aware of the required structure.

**Confidence Score:** 9/10