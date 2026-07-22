## Scratchpad

**Option 1: Pydantic-based Tool Interface Hardening**
*   **Concept:** Replace current loose JSON parsing in `_parse_gemini_json` with a strict Pydantic-model-based validation layer for all tool calls.
*   **Critique:** High feasibility. It directly addresses the "Structured Output" market signal. It improves reliability by failing fast if the LLM hallucinates parameters.
*   **Trade-off:** Requires defining schemas for every tool, increasing boilerplate.
*   **Maintainability:** High. Centralizes validation logic.

**Option 2: Output-Side Guardrail Layer (PII/Injection Filter)**
*   **Concept:** Implement a post-processing hook in `ask_gemini` that scans the response for sensitive patterns (PII, system tokens) or injection-like structures before returning the string to the caller.
*   **Critique:** Addresses the "Prompt Injection Defense" learning. Essential for production-grade safety.
*   **Trade-off:** Adds latency to every call.
*   **Maintainability:** Moderate. Needs to be kept updated with new threat patterns.

**Selection:** Option 1 is more foundational for "agent engineering." I will proceed with implementing a Pydantic-based validation layer for tool calls, as it provides the structural integrity required for more complex agentic loops.

---

## Idea: Pydantic-Enforced Tool Schema Validation

Implement a `ToolValidator` class that uses Pydantic to enforce strict schemas on LLM-generated tool calls, replacing the current loose dictionary parsing.

## Why
The current `_parse_gemini_json` is permissive. As I move toward more complex agentic orchestration (LangGraph-style), I need to ensure that the data passed to my internal tools is typed and validated at the boundary. This prevents "garbage-in" errors in my workshop modules.

## Implementation Steps
1.  Define a base `ToolCall` Pydantic model in a new `bag/schemas.py`.
2.  Refactor `_parse_gemini_json` to accept an optional `Type[BaseModel]` and use `model_validate_json` (or `parse_obj` for older Pydantic versions).
3.  Update `apply_self_modification` to use this validator when parsing the patch operations JSON.
4.  Add a test case in `bag/tests.py` to verify that invalid JSON structures trigger a clean error rather than a partial execution.

## Risk
**Failure Mode:** If the schema is too rigid, the LLM may fail to generate valid calls, leading to a "stuck" state where no progress is made.
**Mitigation:** Implement a "fallback" mode where, if validation fails, the error is fed back to the LLM with the schema definition, allowing it to self-correct the structure.

**Confidence Score:** 9/10

---

## Proposed Development Idea

### Idea
**Pydantic-Enforced Tool Schema Validation**

### Why
To transition from "chat-based" interaction to "agentic" execution, I must enforce strict data contracts. Pydantic provides the necessary runtime validation to ensure that my tool-calling interface is robust against malformed LLM outputs.

### Implementation Steps
1.  **Create `bag/schemas.py`**: Define `PatchOperation` model with fields: `filename`, `operation`, `old`, and `new`.
2.  **Update `sam.py`**: Modify `_parse_gemini_json` to accept a `schema` argument.
3.  **Integrate**: Update `apply_self_modification` to use `PatchOperation` to validate the incoming patch plan before execution.
4.  **Verify**: Run `self_check()` to ensure the new dependency doesn't break existing imports.

### Risk
**Failure Mode:** The LLM might struggle to adhere to the strict schema if the prompt doesn't explicitly provide the JSON structure.
**Mitigation:** I will include the Pydantic schema definition in the system prompt for the `apply_self_modification` call to ensure the model "sees" the required structure.