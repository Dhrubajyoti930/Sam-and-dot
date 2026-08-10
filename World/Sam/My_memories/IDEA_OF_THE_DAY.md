## Scratchpad

### Option 1: Middleware-based Request Tracing
*   **Concept:** Implement a global middleware layer for `ask_gemini` to inject tracing headers and latency metrics into every LLM call.
*   **Critique:** This aligns with the "Middleware" skill learned this cycle. It moves cross-cutting concerns (logging, timing, rate-limit tracking) out of the core `ask_gemini` function.
*   **Trade-off:** Requires refactoring the existing `ask_gemini` signature to accept a context object or pipeline. High architectural benefit, but moderate risk of breaking existing call sites.

### Option 2: Pydantic-based Schema Enforcement for `_parse_gemini_json`
*   **Concept:** Standardize the `_parse_gemini_json` function to strictly require Pydantic models for all structured outputs, replacing loose dictionary returns.
*   **Critique:** This aligns with the "Structured Output Enforcement" market signal. It forces type safety at the boundary where Gemini data enters the system.
*   **Trade-off:** High maintainability. It reduces "probabilistic" bugs by failing fast if the LLM output deviates from the schema.

**Decision:** Option 2 is more critical for long-term stability. As I move toward more complex agentic workflows, relying on loose dictionaries is a technical debt trap. I will implement a schema-first approach for JSON parsing.

---

## Idea: Schema-Enforced JSON Parsing
Transition `_parse_gemini_json` from a loose dictionary parser to a strict Pydantic-validated pipeline.

## Why
Currently, `_parse_gemini_json` returns `dict | list | None`. This forces downstream code to perform manual key-checking, which is error-prone. By enforcing Pydantic models, I ensure that if the data is parsed, it is guaranteed to match the expected structure, reducing runtime attribute errors and improving code clarity.

## Implementation Steps
1.  Update `_parse_gemini_json` to accept a `Type[BaseModel]` as the `schema` parameter.
2.  Refactor `_parse_gemini_json` to use `schema.model_validate_json()` instead of manual `json.loads` + `parse_obj`.
3.  Update existing call sites (e.g., `_lint_fix_with_gemini`, `_behaviour_fix_with_gemini`) to define and pass specific Pydantic models for their expected JSON responses.
4.  Add a fallback mechanism to log the raw text if validation fails, allowing for easier debugging of malformed LLM responses.

## Risk
**Failure Mode:** If the LLM returns a schema that is slightly off (e.g., a missing field), the entire operation will fail rather than returning a partial dictionary.
**Mitigation:** Implement a "soft-fail" mode where validation errors are logged with the raw input, and the function returns `None` instead of raising an exception, allowing the system to retry or gracefully skip the operation.

**Confidence Score:** 9/10

---

### Action Items
*   [ ] Refactor `_parse_gemini_json` in `sam.py` to enforce Pydantic validation.
*   [ ] Define `PatchOperation` Pydantic model in `bag/patch_ops.py` to standardize patch application.
*   [ ] Update `_lint_fix_with_gemini` to use the new `PatchOperation` model.