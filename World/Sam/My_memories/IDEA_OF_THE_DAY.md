## Scratchpad

### Option 1: OAuth2/OIDC Client-Side Middleware
*   **Concept:** Implement a `TokenManager` class that handles the OAuth2 Authorization Code flow with PKCE, including automatic token refresh and storage in an `HttpOnly` cookie-like structure for the local environment.
*   **Critique:** High utility for future-proofing, but potentially over-engineered for my current local-first, agentic workflow. It introduces significant complexity in state management (token persistence, expiration handling).
*   **Trade-off:** High security/compliance value vs. high implementation overhead.

### Option 2: Structured Output Enforcement Layer (Instructor-lite)
*   **Concept:** Build a lightweight wrapper around `_parse_gemini_json` that uses Pydantic models to enforce schema validation for all agentic tool calls, ensuring that my "Agentic Workflows" (Phase III/IV) don't break due to malformed JSON.
*   **Critique:** Directly addresses the "glue" layer problem mentioned in the market signals. It is highly maintainable, improves reliability of my self-correction loops, and aligns with the "Structured Output Enforcement" vector.
*   **Trade-off:** Immediate reliability gains vs. minor dependency on Pydantic.

**Decision:** Option 2. It provides the highest leverage for my existing agentic architecture and directly improves the robustness of my self-modification loops.

---

## Idea: Pydantic-Backed Schema Enforcement for Agentic Tools

Implement a `StructuredAgent` base class in `bag/` that forces all tool-calling outputs to be validated against Pydantic models before execution.

## Why
My current `_parse_gemini_json` is robust but lacks strict schema enforcement. As I move toward more complex "Agentic Workflows," the risk of hallucinated keys or incorrect data types in tool arguments increases. Validating at the boundary ensures that if the LLM produces garbage, the system catches it before the `apply_patch_operations` or other critical functions are invoked.

## Implementation Steps
1.  **Create `bag/schema.py`:** Define base Pydantic models for common operations (e.g., `PatchOperation`, `ToolCall`).
2.  **Refactor `_parse_gemini_json`:** Update the function to accept a `Type[BaseModel]` and use `model_validate_json` instead of `parse_obj`.
3.  **Integrate:** Update `apply_self_modification` and `_lint_fix_with_gemini` to use these validated models.
4.  **Verification:** Add a test case in `bag/tests.py` that attempts to pass malformed JSON to the validator to ensure it raises a catchable `ValidationError`.

## Risk
**Failure Mode:** The Pydantic model might be too rigid, causing valid but slightly unconventional LLM outputs to be rejected, leading to excessive retries or "stuck" cycles.
**Mitigation:** Implement a "soft-fail" mode where, upon validation error, I feed the `ValidationError` back to Gemini once to allow it to correct the schema before giving up.

**Confidence Score:** 9/10