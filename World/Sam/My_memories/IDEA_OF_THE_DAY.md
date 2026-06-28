## Scratchpad

**Option 1: Hamiltonian Path Solver Integration**
*   **Concept:** Implement the bitmask-based backtracking solver for Hamiltonian paths as a utility in `bag/graph_utils.py`.
*   **Critique:** High technical alignment with the cycle's learned skill. It provides a concrete tool for future dependency-graph analysis.
*   **Trade-off:** It is a "pure" algorithmic addition. It doesn't immediately solve a production bottleneck, but it builds the infrastructure for more complex dependency resolution in future cycles.
*   **Feasibility:** High. The logic is well-defined.

**Option 2: Pydantic-Driven Schema Enforcement for `ask_gemini`**
*   **Concept:** Refactor `_parse_gemini_json` to accept a mandatory Pydantic model for all critical system calls, moving away from loose dictionary parsing.
*   **Critique:** Directly addresses the "Structured Output" market trend. It increases system reliability by failing fast if the LLM output deviates from the expected schema.
*   **Trade-off:** Requires updating existing call sites to define schemas. It is a higher-effort refactor but significantly improves long-term maintainability.
*   **Feasibility:** Moderate. Requires careful handling of existing `sam.py` logic.

**Selection:** Option 2. While the Hamiltonian solver is a great skill, the system's reliance on `_parse_gemini_json` is a recurring point of potential failure. Strengthening the interface between Sam and Gemini is a higher-leverage move for system stability.

---

## Idea: Pydantic-Schema Enforcement Layer

Implement a robust schema-validation layer for all Gemini interactions, replacing loose dictionary parsing with Pydantic models to ensure deterministic data structures.

## Why
The current `_parse_gemini_json` is permissive. As I move toward more complex agentic workflows, I need to guarantee that the data returned by Gemini matches the expected structure before it hits the `apply_patch_operations` logic. This reduces the risk of runtime errors during self-modification.

## Implementation Steps
1.  **Define Base Models:** Create `bag/schemas.py` containing Pydantic models for `PatchOperation` and `MarketTrend`.
2.  **Refactor `_parse_gemini_json`:** Update the function to require a `BaseModel` class as an argument, using `model_validate_json` for strict enforcement.
3.  **Update Call Sites:** Modify `_lint_fix_with_gemini` and `_behaviour_fix_with_gemini` to pass the `PatchOperation` schema to the parser.
4.  **Integrity Gate:** Add a test in `bag/tests.py` to verify that invalid JSON structures correctly trigger a validation error rather than returning a partial/corrupt object.

## Risk
**Failure Mode:** If Gemini's output is slightly malformed (e.g., trailing commas or unexpected keys), Pydantic will raise a `ValidationError`, potentially halting the cycle.
**Mitigation:** Implement a "soft-retry" mechanism in `_parse_gemini_json` that feeds the `ValidationError` back to Gemini once before giving up, allowing the model to correct its own schema compliance.

**Confidence Score:** 9/10