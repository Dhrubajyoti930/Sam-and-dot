## Scratchpad

### Option 1: CQRS Read-Model Projection for `knowledge_log.json`
*   **Concept:** Implement a simple projection that transforms the raw `knowledge_log.json` (write model) into a query-optimized `knowledge_summary.json` (read model) containing only the most recent/relevant entries.
*   **Critique:** 
    *   *Pros:* Directly applies the newly learned CQRS pattern; improves performance for Phase II (Spaced Repetition) by avoiding full-file parsing.
    *   *Cons:* Over-engineering for a small JSON file. The current file size is negligible; the complexity of maintaining two synchronized files might outweigh the latency gains.
*   **Feasibility:** High.

### Option 2: Structured Output Enforcement for `ask_gemini`
*   **Concept:** Integrate `Instructor` (or a lightweight Pydantic-based validator) into `_parse_gemini_json` to enforce strict schema validation on all LLM responses, moving away from loose JSON parsing.
*   **Critique:**
    *   *Pros:* Addresses the "missing link" for reliable agentic workflows; significantly reduces runtime errors caused by malformed LLM output.
    *   *Cons:* Requires updating existing prompt templates to include schema definitions.
*   **Feasibility:** Medium-High.

**Decision:** I will proceed with **Option 2**. It provides higher leverage for all future cycles by hardening the communication layer between Sam and the LLM, aligning with the "Structured Output Enforcement" market signal.

---

## Idea: Pydantic-Schema Enforcement for LLM Responses

## Why
Currently, `_parse_gemini_json` relies on regex-based extraction and basic `json.loads`. This is fragile. By enforcing Pydantic schemas, I ensure that every piece of data entering the system (e.g., patch operations, market trends, metrics) is strictly typed and validated before it touches the codebase. This is a foundational step toward more complex, multi-agent orchestration.

## Implementation Steps
1.  **Dependency:** Ensure `pydantic` is available in the environment.
2.  **Refactor `_parse_gemini_json`:** Update the function signature to accept a `Type[BaseModel]` and use `model_validate_json` (Pydantic v2) instead of `parse_obj`.
3.  **Define Schemas:** Create `bag/schemas.py` to house core data structures (e.g., `PatchOperation`, `MarketTrend`, `MetricUpdate`).
4.  **Update Call Sites:** Modify `_lint_fix_with_gemini` and `_behaviour_fix_with_gemini` to pass the `PatchOperation` schema to the parser.

## Risk
*   **Failure Mode:** The LLM may struggle to adhere to strict Pydantic schemas if the prompt is not sufficiently explicit, leading to a high rate of rejected responses.
*   **Mitigation:** Include the JSON schema definition directly in the prompt sent to Gemini to guide the output structure.
*   **Confidence Score:** 8/10.

---

### Self-Correction
I must ensure that the transition to Pydantic does not break existing logic that expects raw dictionaries. I will maintain backward compatibility by making the `schema` argument optional in `_parse_gemini_json`. I will also verify that `pydantic` is installed; if not, I will log a critical error rather than failing silently.