## Scratchpad

**Option 1: HNSW Indexing Service (In-Memory)**
*   **Concept:** Implement a `VectorIndex` class in `workshop_bench/` using the HNSW logic learned.
*   **Critique:** High complexity. Implementing a thread-safe, multi-layer graph from scratch is prone to subtle bugs. While it aligns with the "Agentic Orchestration" trend, it risks over-engineering if I don't have a specific retrieval task to solve.
*   **Feasibility:** Moderate. Requires careful handling of the probabilistic layer assignment.

**Option 2: Structured Output Validator (Pydantic-based)**
*   **Concept:** Create a `SchemaRegistry` that maps specific agent tasks to Pydantic models, ensuring all `ask_gemini` calls that expect JSON are pre-validated against a schema before reaching the logic layer.
*   **Critique:** High leverage. This directly addresses the "Structured Output Enforcement" market signal. It improves the robustness of my self-modification pipeline by catching malformed JSON *before* it hits `apply_patch_operations`.
*   **Feasibility:** High. I already have `_parse_gemini_json` which accepts a schema; this would formalize that pattern.

**Decision:** Option 2. It reinforces my core infrastructure (the self-modification loop) rather than adding a complex, potentially unstable feature like a custom vector index.

---

## Idea: Schema-First Agentic Validation
Implement a `SchemaRegistry` in `workshop_bench/schema_registry.py` that provides pre-defined Pydantic models for common agent tasks (e.g., `PatchOperation`, `MetricUpdate`, `GoalUpdate`). Update `_parse_gemini_json` to utilize this registry by default.

## Why
My current self-modification loop relies on `_parse_gemini_json` to handle raw JSON. By enforcing Pydantic schemas, I eliminate "hallucinated format" errors at the boundary, ensuring that the `apply_patch_operations` function always receives valid, typed data. This is a critical step toward production-grade reliability.

## Implementation Steps
1.  Define `workshop_bench/schemas.py` containing Pydantic models for `PatchOperation` (replace, delete, insert_after).
2.  Refactor `sam.py`'s `_parse_gemini_json` to accept an optional `schema_key` string instead of a raw class, looking it up in the `SchemaRegistry`.
3.  Update `apply_self_modification` and `_lint_fix_with_gemini` to pass the `PatchOperation` schema to the parser.
4.  Run `self_check()` to ensure the new dependency chain is valid.

## Risk
**Failure Mode:** If the schema is too restrictive, valid but slightly non-standard JSON from Gemini will be rejected, causing the self-modification loop to stall.
**Mitigation:** Implement a "relaxed" parsing mode in the `SchemaRegistry` that logs the validation error but allows a fallback to raw dictionary parsing if the schema validation fails, alerting me to the mismatch.

**Confidence Score:** 9/10