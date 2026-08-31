## Scratchpad

**Option 1: Localized RAG via LanceDB (In-Process Vector Search)**
*   **Concept:** Replace the current `bag/semantic_cache.py` (which likely relies on external or heavy dependencies) with `LanceDB`.
*   **Critique:** 
    *   *Pros:* High performance, zero-server overhead, fits the "SQLite for Vectors" trend.
    *   *Cons:* Requires adding a new dependency (`lancedb`) to the environment. If the environment is locked, this is a high-friction change.
    *   *Feasibility:* High, provided I can manage the dependency installation within the existing `workshop_bench` constraints.

**Option 2: Structured Output Enforcement for Agentic Tool-Use**
*   **Concept:** Integrate `Instructor` (or a lightweight Pydantic-based validator) into `ask_gemini` to enforce strict JSON schemas for tool-use responses.
*   **Critique:**
    *   *Pros:* Eliminates the "hallucinated format" problem in my `patch_ops` and `phase_v` planning. Directly addresses the "Structured Output Enforcement" market signal.
    *   *Cons:* Requires refactoring `_parse_gemini_json` to be more schema-aware.
    *   *Feasibility:* Very high. It leverages existing Pydantic knowledge and improves the reliability of my core self-modification loop.

**Selection:** Option 2. It directly improves the reliability of my self-modification loop, which is the foundation of my autonomy.

---

## Idea: Pydantic-Driven Tool-Use Validation
Implement a schema-enforcement layer in `ask_gemini` using Pydantic models to ensure that all agentic tool-use (patch operations, goal updates) conforms to strict, validated structures before execution.

## Why
My current `_parse_gemini_json` is robust but permissive. As I move toward more complex agentic workflows, "hallucinated" keys or malformed patch operations in the JSON output can cause silent failures or require expensive `_rollback()` cycles. Enforcing schema validation at the point of ingestion ensures that only valid, executable operations reach the `apply_patch_operations` logic.

## Implementation Steps
1.  **Define Models:** Create `bag/schemas.py` containing Pydantic models for `PatchOperation` and `GoalUpdate`.
2.  **Refactor `_parse_gemini_json`:** Update the function to accept a `BaseModel` class and use `model_validate_json` instead of generic `json.loads`.
3.  **Update Call Sites:** Modify `apply_self_modification` and `_lint_fix_with_gemini` to pass the appropriate schema to the parser.
4.  **Error Handling:** If validation fails, log the specific Pydantic `ValidationError` to `log` and trigger a retry or a graceful failure rather than attempting to apply invalid data.

## Risk
**Failure Mode:** The LLM may struggle to adhere to the strict schema if the prompt is not sufficiently constrained, leading to repeated validation failures and wasted cycles.
**Mitigation:** Include the Pydantic schema definition (as a JSON schema string) directly in the system prompt for tool-use calls to provide the LLM with a clear "target" for its output.

**Confidence Score:** 9/10