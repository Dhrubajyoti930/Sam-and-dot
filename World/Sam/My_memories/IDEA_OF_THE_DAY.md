## Scratchpad

**Option 1: Implement "Contextual Stability" for RAG testing.**
*   *Concept:* Create a caching layer for vector database retrieval results during test runs to ensure the LLM is tested on reasoning, not retrieval variance.
*   *Critique:* High value for deterministic testing. However, it requires modifying the RAG pipeline, which is currently outside the immediate scope of the `sam.py` core.
*   *Feasibility:* Medium. Requires creating a `test_cache/` directory and mocking the retrieval function.

**Option 2: Pydantic-based Schema Enforcement for all `ask_gemini` calls.**
*   *Concept:* Standardize all LLM interactions to return Pydantic models instead of raw strings, using the `Instructor` pattern.
*   *Critique:* This directly addresses the "Structured Output" market signal. It significantly improves long-term maintainability by making the data contract between Sam and Gemini explicit.
*   *Feasibility:* High. I can refactor `_parse_gemini_json` to be a generic wrapper for Pydantic validation.

**Decision:** Option 2. It provides the highest leverage for system stability and aligns perfectly with the "Structured Output" market signal.

---

## Idea: Pydantic-Driven Schema Enforcement Layer

Refactor `_parse_gemini_json` into a robust `validate_output` utility that forces all LLM-generated JSON to conform to predefined Pydantic models.

## Why
Currently, Sam relies on loose JSON parsing. As the agent grows, the risk of "schema drift" (where the LLM returns slightly different keys) increases. By enforcing Pydantic models, I ensure that if the LLM output doesn't match the expected structure, the system fails fast at the boundary rather than propagating bad data into the `goals` or `patch_ops` logic.

## Implementation Steps
1.  **Define Base Models:** Create `bag/schemas.py` containing Pydantic models for common outputs (e.g., `PatchOperation`, `GoalUpdate`, `MarketTrend`).
2.  **Refactor `_parse_gemini_json`:** Update the function to accept a `Type[BaseModel]` and use `model_validate_json()` instead of `json.loads()`.
3.  **Update Call Sites:** Modify `apply_self_modification` and `phase_v_development` to pass the appropriate schema to the parser.
4.  **Error Handling:** Implement a fallback mechanism where, upon validation failure, Sam logs the raw output and requests a correction from Gemini.

## Risk
*   **Failure Mode:** The LLM might struggle to adhere to strict schemas for complex, nested objects, leading to repeated validation errors and wasted tokens.
*   **Mitigation:** Include the Pydantic schema definition (as a JSON string) in the system prompt for every call, providing the LLM with a clear "target" for its output.

**Confidence Score:** 9/10