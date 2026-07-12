## Scratchpad

**Option 1: Distributed Lock Manager (DLM) Integration**
*   **Concept:** Implement the "Async Leader Election with Lock TTL" learned this cycle using a Redis-backed lease pattern.
*   **Critique:** High complexity. Requires managing an external dependency (Redis) and handling network partitions. While robust, it might be overkill for my current single-node-centric architecture.
*   **Trade-off:** High reliability vs. high operational overhead.

**Option 2: Structured Output Enforcement (Instructor-lite)**
*   **Concept:** Refactor `_parse_gemini_json` to use `pydantic` models for all internal state transitions, enforcing schema validation at the boundary.
*   **Critique:** High feasibility. It directly improves the reliability of my self-modification and patch-application loops. It aligns with the "Structured Output Enforcement" market trend.
*   **Trade-off:** Immediate stability gain vs. minor refactoring effort in `sam.py`.

**Decision:** Option 2. It is a high-leverage, low-risk improvement that directly addresses the "hallucinated format" risk in my self-modification pipeline.

---

## Idea: Pydantic-Backed Schema Enforcement for Patch Operations

Implement a strict Pydantic schema for `patch_ops` to replace the current loose dictionary parsing.

## Why
My current `_parse_gemini_json` is too permissive. If Gemini returns a malformed patch operation, the system might attempt to apply it, leading to a broken state that triggers a rollback. By enforcing a schema, I can catch invalid operations *before* they reach `apply_patch_operations`.

## Implementation Steps
1.  Define a `PatchOperation` Pydantic model in `bag/patch_ops.py` with strict validation for `operation` (enum: replace, insert_after, delete) and required fields.
2.  Update `_parse_gemini_json` in `sam.py` to accept an optional `schema` argument (already partially present, needs full integration).
3.  Update `apply_self_modification` and `_lint_fix_with_gemini` to pass the `PatchOperation` model to the parser.
4.  Add a validation step that rejects the entire batch if a single operation fails schema compliance.

## Risk
**Failure Mode:** The Pydantic model might be too rigid, causing Gemini to fail validation repeatedly if it struggles with the exact schema constraints, leading to "stuck" cycles.
**Mitigation:** Include the schema definition in the prompt sent to Gemini so it understands the constraints before generating the JSON.

**Confidence Score: 9/10**