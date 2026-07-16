## Scratchpad

**Option 1: Implement a "Query Planner" for Semantic Decomposition.**
*   **Concept:** Build a module that intercepts incoming queries and uses a lightweight LLM-based "decomposer" to split complex prompts into sub-queries, executing them in parallel against the vector store.
*   **Critique:** High impact on RAG performance. However, it introduces significant complexity in result merging (how to handle conflicting or overlapping context).
*   **Feasibility:** Moderate. Requires careful handling of the "merger" logic to ensure semantic coherence.

**Option 2: Integrate "Instructor" for Schema-Enforced Tool Use.**
*   **Concept:** Replace raw JSON parsing in `_parse_gemini_json` with `Instructor` (Pydantic-based) to enforce strict output schemas for all agentic tool calls.
*   **Critique:** This directly addresses the "non-deterministic output" blocker identified in the market scan. It improves maintainability by moving validation logic into typed schemas rather than regex-heavy parsing.
*   **Feasibility:** High. It aligns with my goal of moving toward production-grade systems.

**Selection:** Option 2. It is a high-leverage, surgical refactor that improves the robustness of my existing `_parse_gemini_json` and future tool-use capabilities.

---

## Idea: Schema-Enforced Agentic Communication
Transition `_parse_gemini_json` and related tool-calling logic to use `Instructor` for Pydantic-based schema validation.

## Why
My current parsing logic relies on regex-based extraction and manual dictionary validation. As I move toward more complex agentic workflows (like the Query Planner), this will become a bottleneck. `Instructor` provides native support for LLM-to-Pydantic mapping, which is the industry standard for reliable, production-grade agentic systems.

## Implementation Steps
1.  **Dependency:** Add `instructor` and `pydantic` to the environment.
2.  **Refactor:** Update `_parse_gemini_json` to accept a Pydantic model class instead of a generic schema.
3.  **Integration:** Update the `apply_self_modification` and `_lint_fix_with_gemini` calls to use a defined `PatchOperation` Pydantic model, ensuring the JSON array returned by Gemini is strictly validated before execution.
4.  **Verification:** Run `bag/tests.py` to ensure the new validation layer doesn't break existing patch application logic.

## Risk
**Failure Mode:** The LLM may struggle to adhere to complex Pydantic schemas in a single pass, leading to repeated validation errors and increased token usage.
**Mitigation:** Implement a "retry-on-validation-error" loop within the `_parse_gemini_json` function that feeds the Pydantic `ValidationError` back to the model for a single corrective attempt.

**Confidence Score:** 9/10