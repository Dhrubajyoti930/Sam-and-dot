## Scratchpad

### Option 1: Implement a "Critic" Decorator for Tool Calls
*   **Concept:** Wrap tool-calling functions in a decorator that validates inputs/outputs against Pydantic schemas before and after execution.
*   **Critique:** 
    *   *Pros:* Directly addresses the "Structured Output" trend; enforces type safety at the boundary.
    *   *Cons:* Increases complexity of the `sam.py` core; requires migrating existing tool definitions to Pydantic models.
    *   *Feasibility:* High. I already have `resilience.py` for decorators; this is a logical extension.

### Option 2: State-Machine Transition Logger
*   **Concept:** Replace the current linear `run_cycle` with a formal state machine (e.g., `IDLE` -> `PLANNING` -> `EXECUTING` -> `CRITIQUE` -> `COMMIT`).
*   **Critique:**
    *   *Pros:* Improves observability and debugging; aligns with "Agentic Orchestration" patterns.
    *   *Cons:* Significant refactor of the main loop; potential for "state-lock" if transitions aren't handled perfectly.
    *   *Feasibility:* Moderate. Requires careful mapping of existing phases to states.

**Decision:** Option 1 is more aligned with my current goal of reducing hallucination and ensuring production-ready outputs. It provides immediate, measurable value without the systemic risk of a full state-machine rewrite.

---

## Idea: Schema-Enforced Tool Validation (The "Critic" Gate)

## Why
My current tool-calling logic relies on parsing raw JSON from Gemini. This is brittle. By integrating `pydantic` models as the source of truth for tool inputs and outputs, I can catch malformed data *before* it hits the execution layer, effectively creating a "Critic" gate that prevents invalid state transitions.

## Implementation Steps
1.  **Define Models:** Create a `schemas.py` (or integrate into `resilience.py`) defining Pydantic models for core tool inputs (e.g., `FileWrite`, `CommandExec`).
2.  **Create Decorator:** Implement `@validate_tool_call` which accepts a Pydantic model, validates `*args` and `**kwargs`, and returns a structured result.
3.  **Integrate:** Update `ask_gemini` (L251) to pass tool outputs through the validator before returning them to the execution loop.
4.  **Error Handling:** If validation fails, trigger a "Correction" prompt back to Gemini with the specific schema violation error.

## Risk
*   **Failure Mode:** The model might get stuck in a "validation loop" if the schema is too restrictive or the prompt doesn't clearly explain the error.
*   **Mitigation:** Implement a "max-retry" counter in the decorator. If validation fails > 2 times, log a hard failure and halt the cycle to prevent infinite loops.

**Confidence Score:** 9/10