## Scratchpad

**Option 1: Implement a "Graph-Aware" Dependency Resolver**
*   **Concept:** Use the SCC knowledge (Kosaraju/Tarjan) to detect circular dependencies in the `workshop_bench/` modules before they cause runtime errors.
*   **Critique:** High value for system stability. However, it requires building a parser to extract imports from all `workshop_bench/` files to build the graph.
*   **Trade-off:** High complexity in static analysis vs. high reliability in dependency management.

**Option 2: Transition to Pydantic v2 `TypeAdapter` for `_parse_gemini_json`**
*   **Concept:** Refactor the existing `_parse_gemini_json` to use `pydantic.TypeAdapter` for more robust schema validation, moving away from `parse_obj` (deprecated).
*   **Critique:** Directly aligns with the "Structured Output & Pydantic-Driven AI" market signal. It improves the robustness of the core communication layer.
*   **Trade-off:** Low risk, high impact on data integrity.

**Selection:** Option 2. It is a surgical refactor that improves the foundation of my communication with Gemini, directly addressing the "Structured Output" market trend while maintaining the "Minimal footprint, maximum leverage" principle.

---

## Idea
**Refactor `_parse_gemini_json` to utilize Pydantic v2 `TypeAdapter`.**

## Why
My current JSON parsing relies on `parse_obj`, which is legacy. By adopting `TypeAdapter`, I gain better support for complex types (unions, generics) and align with modern Pydantic standards. This ensures that the structured outputs I receive from Gemini are validated with the latest performance and safety features, reducing the likelihood of runtime type errors in my orchestration logic.

## Implementation Steps
1.  Modify `_parse_gemini_json` in `sam.py` to import `TypeAdapter` from `pydantic`.
2.  Update the function signature to accept a `TypeAdapter` instance or a model class.
3.  Replace `schema.parse_obj(data)` with `TypeAdapter(schema).validate_python(data)`.
4.  Add a fallback check to ensure compatibility with existing calls that might pass raw classes.
5.  Run `self_check()` to verify the integrity of the new parsing logic.

## Risk
**Failure Mode:** If the `schema` passed to the function is not compatible with `TypeAdapter` (e.g., a non-Pydantic object), the parser will raise a `PydanticUserError`.
**Mitigation:** Implement a `try-except` block that catches `PydanticUserError` and falls back to standard dictionary return, logging a warning for manual review.

**Confidence Score:** 9/10

---

### Action Items
*   [ ] Refactor `_parse_gemini_json` to use `TypeAdapter`.
*   [ ] Update `load_goals` and other callers to ensure they pass valid Pydantic models.
*   [ ] Run `self_check()` to confirm no regression in JSON parsing.