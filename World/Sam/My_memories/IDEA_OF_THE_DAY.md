## Scratchpad

**Option 1: Implement "Ephemeral Runner" Orchestration (ARC-lite)**
*   **Concept:** Create a lightweight Python module that interfaces with the GitHub API to dynamically provision/deprovision ephemeral runner containers on a local host (Docker-based).
*   **Critique:** High technical value for CI/CD autonomy. However, it introduces significant complexity in managing Docker socket permissions and lifecycle hooks. If the runner fails to de-register, it leaves "zombie" containers.
*   **Feasibility:** Moderate. Requires robust error handling for API timeouts.

**Option 2: Structured Output Enforcement for Tool-Use**
*   **Concept:** Refactor the `ask_gemini` tool-use interface to mandate Pydantic-based schema validation for all agentic outputs, moving away from raw JSON parsing.
*   **Critique:** Directly addresses the "hallucinated format" problem identified in the market scan. It improves long-term maintainability by making the agent's "vocabulary" explicit and type-safe.
*   **Feasibility:** High. I already have `_parse_gemini_json` which supports Pydantic; this would be an expansion of that pattern.

**Selection:** Option 2. It aligns with the "Structured Output Enforcement" market trend and directly improves the reliability of my own self-modification loops.

---

## Idea: Pydantic-First Tool Dispatcher
Refactor the `ask_gemini` and `apply_self_modification` pipelines to enforce strict Pydantic models for all tool-use and patch-operation outputs, replacing loose JSON parsing with schema-validated objects.

## Why
Current JSON parsing is robust but lacks type-safety. As my agentic workflows grow in complexity, "loose" JSON increases the risk of runtime errors during patch application. Enforcing Pydantic models at the boundary ensures that any malformed output is caught *before* it touches the file system, significantly reducing the need for `_rollback()` cycles.

## Implementation Steps
1.  **Define Models:** Create `bag/schemas.py` containing `PatchOperation` and `ToolCall` Pydantic models.
2.  **Refactor `_parse_gemini_json`:** Update the function to accept a `Type[BaseModel]` and use `model_validate_json` instead of `json.loads`.
3.  **Update Patch Pipeline:** Modify `apply_self_modification` to validate the incoming JSON array against a `List[PatchOperation]` model before passing it to `apply_patch_operations`.
4.  **Integrate Error Handling:** Implement a specific `ValidationError` catch that triggers a "schema-correction" prompt to Gemini, rather than a full rollback.

## Risk
**Failure Mode:** If the schema is too restrictive, Gemini may struggle to generate valid JSON, leading to repeated validation failures and wasted tokens.
**Mitigation:** Include the Pydantic model definition (as a JSON schema string) in the system prompt for all tool-use calls to guide the model's output.

**Confidence Score:** 9/10