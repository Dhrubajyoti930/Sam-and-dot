## Scratchpad

**Option 1: Event-Driven Shadow Mode Implementation**
*   **Concept:** Modify the `FlagManager` to support a "shadow" mode flag. When enabled, the `apply_patch_operations` or similar critical functions would trigger an asynchronous event (via a simple `queue.Queue` or `asyncio.Queue`) to a "ShadowExecutor" that simulates the operation in a sandbox environment and logs the diff.
*   **Critique:** High complexity. Requires introducing async patterns into a largely synchronous codebase. However, it aligns perfectly with the "Shadow Mode" skill learned this cycle and provides a massive safety boost for future self-modifications.
*   **Feasibility:** Moderate. Requires careful handling of the `workshop_bench` state to ensure the shadow environment doesn't collide with the primary.

**Option 2: Pydantic-Based Schema Registry for Patch Operations**
*   **Concept:** Replace the raw JSON parsing in `apply_patch_operations` with a strict Pydantic model that validates the structure of patch operations *before* they hit the file system.
*   **Critique:** Very high maintainability. It moves the "validation" logic from implicit runtime checks to explicit schema enforcement. It directly addresses the "hallucination of format" risk.
*   **Feasibility:** High. I already have `_parse_gemini_json` which supports Pydantic. This is a low-risk, high-reward refactor.

**Decision:** I will pursue **Option 2**. It is a foundational improvement that makes the "Shadow Mode" (Option 1) safer to implement in the next cycle. By hardening the patch interface now, I reduce the risk of malformed patches causing corruption.

---

## Idea: Pydantic-Driven Patch Schema Enforcement

## Why
Currently, `apply_patch_operations` relies on loose dictionary structures. If Gemini hallucinates a field or misnames an operation, the system might fail silently or partially apply a patch. By enforcing a Pydantic schema, I ensure that every patch operation is structurally sound before it touches the disk, aligning with the "Structured Output Enforcement" market signal.

## Implementation Steps
1.  Define a `PatchOperation` Pydantic model in `bag/patch_ops.py` with strict `Literal` types for operations (`replace`, `insert_after`, `delete`).
2.  Update `apply_patch_operations` to validate the incoming list of operations against `List[PatchOperation]`.
3.  Add a `validator` to the model to ensure `old` and `new` fields are present based on the `operation` type.
4.  Update `_lint_fix_with_gemini` and `_behaviour_fix_with_gemini` to utilize this new schema for their generated patches.

## Risk
**Failure Mode:** The schema might be too rigid, causing valid but slightly unconventional patches to be rejected, leading to "patch starvation" where I cannot fix a bug because the fix doesn't fit the strict schema.
**Mitigation:** Include a `comment` field in the schema that is ignored by the logic but allows Gemini to explain its reasoning, which I can then log for debugging if a patch is rejected.

**Confidence Score:** 9/10