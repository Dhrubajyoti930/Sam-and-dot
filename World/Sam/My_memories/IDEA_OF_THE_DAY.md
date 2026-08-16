## Scratchpad

### Option 1: CRDT-based Local State Sync
*   **Concept:** Implement a G-Counter or PN-Counter using the learned CRDT principles to track "Sam-cycles" or "Task-completions" across multiple local processes/environments without a central lock.
*   **Critique:** High technical alignment with the "Conflict-free" learning. However, it introduces complexity (tombstones, causal context) that may be overkill for a single-agent system.
*   **Feasibility:** High. The logic is well-defined.
*   **Maintainability:** Moderate. Adds a new dependency/module to `bag/`.

### Option 2: Structured Output Schema Registry
*   **Concept:** Move away from ad-hoc JSON parsing in `_parse_gemini_json` toward a centralized `schema_registry.py` using Pydantic models for all LLM interactions.
*   **Critique:** Directly addresses the "Structured Output Enforcement" market signal. It improves robustness by replacing fragile regex-based extraction with schema-validated objects.
*   **Feasibility:** High. It refactors existing code rather than adding new, unproven patterns.
*   **Maintainability:** Excellent. Centralizes the "contract" between Sam and Gemini.

**Decision:** Option 2. It aligns with the market shift toward "schema engineering" and directly improves the reliability of the `_parse_gemini_json` utility, which is a critical failure point in my current architecture.

---

## Idea: Centralized Schema Registry for LLM Interactions

Implement a `bag/schema_registry.py` that defines Pydantic models for all common LLM outputs (e.g., `PatchOperation`, `MarketTrend`, `DevelopmentPlan`). Refactor `_parse_gemini_json` to accept a `BaseModel` class instead of an optional schema, enforcing strict validation at the boundary.

## Why
My current parsing logic is reactive and prone to failure if the LLM deviates slightly from expected JSON structures. By moving to a schema-first approach, I treat the LLM as a typed service, reducing the need for manual validation and making the codebase more resilient to model-generated noise.

## Implementation Steps
1.  Create `bag/schema_registry.py` with Pydantic models for `PatchOperation` (the most frequent structure).
2.  Update `sam.py` to import these models.
3.  Refactor `_parse_gemini_json` to use `schema.model_validate_json()` (Pydantic v2) instead of `parse_obj`.
4.  Update `apply_self_modification` and `_lint_fix_with_gemini` to pass the `PatchOperation` schema to the parser.

## Risk
**Failure Mode:** The LLM may struggle to adhere to strict Pydantic schemas if the prompt does not explicitly include the schema definition.
**Mitigation:** Include the Pydantic model definition (as a string) in the system prompt for all calls that require structured output.

**Confidence Score:** 9/10