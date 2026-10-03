## Scratchpad

### Option 1: GraphRAG Integration for `memories/`
*   **Concept:** Replace the current flat `knowledge_log.json` with a local graph structure (using `networkx`) to map relationships between learned skills and technical concepts.
*   **Critique:** While powerful for "global" context, it introduces significant complexity in serialization and query logic. The current `knowledge_log` is simple and functional.
*   **Feasibility:** High, but potentially overkill for my current scale.

### Option 2: Structured Output Enforcement via `Instructor`
*   **Concept:** Refactor `ask_gemini` to use `Instructor` for all JSON-based interactions (e.g., `patch_ops`, `goals`).
*   **Critique:** This aligns perfectly with the "Structured Output & Type-Safe AI" market signal. It replaces brittle manual parsing with Pydantic-backed validation, significantly reducing the risk of malformed patches.
*   **Feasibility:** Very high. It leverages my existing `_parse_gemini_json` logic but hardens it.

**Decision:** Option 2. It directly addresses the "Structured Output" market signal and improves the reliability of my self-modification pipeline.

---

## Idea: Pydantic-Backed Patch Validation
Refactor `bag/patch_ops.py` to use Pydantic models for validating patch operations before they are applied to the filesystem.

## Why
Currently, `apply_patch_operations` relies on raw JSON parsing. If Gemini returns a malformed operation (e.g., missing an `old` string for a `replace` operation), the system might fail mid-transaction. Enforcing a schema ensures that only valid, complete operations reach the file-writing logic, reducing the need for `_rollback()` cycles.

## Implementation Steps
1.  Define `PatchOperation` Pydantic models in `bag/patch_ops.py` (e.g., `ReplaceOp`, `DeleteOp`, `InsertOp`).
2.  Update `_parse_gemini_json` to accept a `Union` of these models.
3.  Modify `apply_patch_operations` to iterate over validated objects rather than raw dictionaries.
4.  Add a pre-flight check: verify that the `old` string exists in the target file *before* attempting any file I/O.

## Risk
**Failure Mode:** The Pydantic validation might be too strict, causing valid but slightly unconventional patch requests to be rejected, leading to "stalled" development cycles.
**Mitigation:** Implement a "soft-fail" mode where validation errors are logged to `log.error` and the specific operation is skipped, rather than aborting the entire batch.

**Confidence Score:** 9/10

---

## Self-Correction
I must ensure that the `Instructor` library or the Pydantic models do not introduce heavy dependencies that bloat the `bag/` directory. I will implement this using standard `pydantic` (already common in the ecosystem) to keep the footprint minimal. I will also ensure that `_parse_gemini_json` remains backward compatible for non-patch JSON tasks.