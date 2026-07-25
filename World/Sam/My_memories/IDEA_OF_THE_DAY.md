## Scratchpad

**Option 1: Speculative Decoding Integration (Inference Optimization)**
*   **Concept:** Implement a draft-model verification loop within the `ask_gemini` pipeline (or a local proxy) to accelerate token generation.
*   **Critique:** High technical complexity. Requires managing a secondary model (e.g., TinyLlama) and complex KV cache alignment. While it aligns with the "Speculative Decoding" skill learned, it may be overkill for Sam’s current communication-heavy, low-latency-requirement workflow.
*   **Feasibility:** Moderate. The math is well-defined, but the infrastructure overhead is high.

**Option 2: Structured Output Enforcement (Reliability Hardening)**
*   **Concept:** Replace manual JSON parsing in `_parse_gemini_json` with a more robust, schema-first approach using `Instructor` or a custom Pydantic-based validator that forces the LLM to retry on schema violations.
*   **Critique:** High impact on stability. Sam’s current `_parse_gemini_json` is fragile when faced with complex nested structures. This directly addresses the "Structured Output Enforcement" market trend.
*   **Feasibility:** High. It leverages existing Pydantic knowledge and improves the "glue" layer of the architecture.

**Decision:** Option 2 is superior for long-term maintainability. It reduces the "hallucination of structure" and makes the `apply_patch_operations` logic significantly more resilient.

---

## Idea: Pydantic-Driven Schema Enforcement for Patch Operations

## Why
Sam’s current `_parse_gemini_json` relies on regex-based extraction, which is prone to failure if the LLM includes conversational filler or malformed JSON. By formalizing the patch operation schema using Pydantic and implementing a "retry-on-failure" loop, I can eliminate the need for manual cleanup of patch JSON, ensuring that `apply_patch_operations` receives perfectly typed input every time.

## Implementation Steps
1.  **Define Schema:** Create `bag/schemas.py` containing a `PatchOperation` Pydantic model with strict validation for `operation` (replace/delete/insert_after) and required fields.
2.  **Refactor Parser:** Update `_parse_gemini_json` in `sam.py` to accept a `Type[BaseModel]` and use `model_validate_json` for strict enforcement.
3.  **Implement Retry Logic:** Modify `apply_self_modification` to catch validation errors and re-prompt Gemini with the specific schema violation error, forcing a correction.
4.  **Integrate:** Update `_lint_fix_with_gemini` and `_behaviour_fix_with_gemini` to utilize the new schema-validated parsing.

## Risk
**Failure Mode:** The LLM enters a "correction loop" where it repeatedly generates the same invalid JSON despite error feedback, consuming cycle time and API quota.
**Mitigation:** Implement a hard limit of 2 retries per patch request. If validation fails after 2 attempts, fall back to a "human-in-the-loop" alert to Dot.

**Confidence Score:** 9/10