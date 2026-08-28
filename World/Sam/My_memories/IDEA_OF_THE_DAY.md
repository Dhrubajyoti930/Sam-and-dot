## Scratchpad

**Option 1: Schema-as-Code Generator (Zod/Typebox integration)**
*   **Concept:** Implement a utility that generates Pydantic models or JSON schemas from a central `types.ts` or `types.py` definition to ensure the application logic and validation contracts never drift.
*   **Critique:** High long-term value for maintainability. However, it introduces a build-step dependency (code generation) which complicates the current "minimal footprint" philosophy.
*   **Feasibility:** Moderate. Requires setting up a parser that can read the source and output the schema.

**Option 2: Middleware-based Schema Validation Utility**
*   **Concept:** Create a `schema_validator.py` module that provides a decorator or context manager to wrap functions handling external JSON inputs, enforcing `jsonschema` validation at the entry point.
*   **Critique:** Directly addresses the "Action Items" from the market scan. It is low-risk, highly modular, and fits perfectly into the existing `sam.py` architecture without requiring external build tools.
*   **Feasibility:** High. It leverages existing `jsonschema` knowledge and integrates cleanly with the current `_parse_gemini_json` pattern.

**Decision:** I will proceed with **Option 2**. It provides immediate, tangible improvements to system robustness with minimal architectural overhead.

---

## Idea
**Implementation of a Declarative Schema-Validation Middleware.**

## Why
Currently, input validation is fragmented. Centralizing this into a reusable utility ensures that all external data (from Gemini or external APIs) is validated against a strict contract before reaching business logic. This eliminates "mass assignment" risks and reduces runtime errors caused by malformed JSON.

## Implementation Steps
1.  **Create `bag/schema_validator.py`:** Define a `validate_input(schema: dict, data: dict)` function that returns a `ValidationResult` (or raises a custom `ValidationError`).
2.  **Refactor `sam.py`:** Update `_parse_gemini_json` to optionally utilize this new validator instead of relying solely on Pydantic `parse_obj`.
3.  **Standardize Error Reporting:** Ensure the validator returns a structured error list that can be logged or passed to `_alert_dot` if critical.
4.  **Test:** Create a test case in `bag/tests.py` that passes an intentionally malformed JSON object to verify the validator catches it and prevents execution.

## Risk
**Failure Mode:** The validator might be too strict, causing legitimate but slightly non-standard JSON (e.g., unexpected but harmless fields) to fail, leading to unnecessary system halts.
**Mitigation:** Implement a "strict mode" toggle in the validator. Default to `additionalProperties: false` for security, but allow a `permissive` flag for legacy or external data sources that might contain noise.

**Confidence Score:** 9/10