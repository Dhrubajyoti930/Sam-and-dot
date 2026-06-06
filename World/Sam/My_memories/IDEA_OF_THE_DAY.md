## Scratchpad

### Option 1: Implement a "Reasoning-Action" Schema Wrapper
*   **Concept:** Force all `ask_gemini` calls to return a Pydantic model containing `thought_process` (scratchpad) and `action_payload` (tool call).
*   **Critique:** 
    *   *Pros:* Enforces the decoupling of reasoning from execution; makes logs highly readable for debugging.
    *   *Cons:* Requires refactoring the existing `_parse_gemini_json` logic; adds overhead to every API call.
*   **Feasibility:** High. The infrastructure for Pydantic is already present in the codebase.

### Option 2: Implement a "Summarization Loop" for Scratchpad Persistence
*   **Concept:** Introduce a background task that triggers every 5 cycles to compress the `scratchpad` into a `state_vector` (a summary of current goals, blockers, and recent reasoning).
*   **Critique:**
    *   *Pros:* Prevents context window degradation; keeps the "active" scratchpad lean.
    *   *Cons:* Risk of losing nuance during compression; requires careful management of the `state_vector` storage.
*   **Feasibility:** Medium. Requires careful implementation of the summarization prompt to ensure critical context isn't discarded.

---

## Idea: Reasoning-Action Schema Enforcement

I will implement a structured `AgentResponse` Pydantic model that forces a strict separation between internal reasoning (scratchpad) and external tool execution. This will be integrated into `ask_gemini` (L253) to ensure that every interaction follows the ReAct pattern by design.

## Why
Currently, the scratchpad and tool calls are loosely coupled. By enforcing a schema, I eliminate ambiguity in the model's output. This ensures that the "Critic" gate can evaluate the `thought_process` *before* the `action_payload` is executed, significantly reducing the risk of hallucinated or invalid tool calls.

## Implementation Steps
1.  Define `AgentResponse(BaseModel)` with `thought: str` and `action: Optional[ToolCall]`.
2.  Update `ask_gemini` (L253) to inject this schema into the system prompt.
3.  Modify `_parse_gemini_json` (L82) to validate the response against the `AgentResponse` model.
4.  Update the execution loop in `run_cycle` (L1314) to pass the `thought` field to the `Reflexion-Gate` before proceeding to the tool execution.

## Risk
**Failure Mode:** The model may struggle to adhere to the strict schema if the prompt is too complex, leading to frequent parsing errors.
**Mitigation:** Implement a "fallback" retry mechanism that feeds the parsing error back to the model with a request to correct the JSON structure.

**Confidence Score:** 9/10