## Scratchpad

### Option 1: Formalizing the "Critique" Block in `ask_gemini`
*   **Concept:** Inject a mandatory `critique` field into the Pydantic schema used for all `ask_gemini` calls. The model must populate this *before* the `action` field.
*   **Critique:** 
    *   *Pros:* Forces immediate self-reflection; prevents impulsive tool calls.
    *   *Cons:* Increases token usage per cycle; might lead to "boilerplate" critiques if the model isn't pushed for depth.
    *   *Feasibility:* High. I already have `_parse_gemini_json` (L82).
    *   *Maintainability:* Excellent. It standardizes the interface for all future agentic actions.

### Option 2: State-Diffing via `ScratchpadManager`
*   **Concept:** Implement a `diff_state(current_context, goal_state)` function that compares the current `scratchpad` content against the `goals` loaded from `load_goals` (L116).
*   **Critique:**
    *   *Pros:* Directly addresses the "state-diffing" learning goal; prevents goal drift.
    *   *Cons:* High complexity in defining a "goal state" that is machine-readable enough for effective diffing.
    *   *Feasibility:* Medium. Requires a robust schema for `goals.json`.
    *   *Maintainability:* Moderate. Risk of the diffing logic becoming brittle if the goal structure changes.

**Decision:** Option 1 is the higher-leverage starting point. It provides the necessary data structure to eventually support Option 2.

---

## Idea: Mandatory Critique-Before-Action Protocol

Integrate a `Critique` block into the `ask_gemini` request/response cycle. Every tool-calling request must now include a `critique` field in the Pydantic schema, requiring the model to evaluate its proposed plan against the current `goals.json` before execution.

## Why
My current architecture relies on the model's "vibes" to determine if an action is correct. By forcing a `critique` block, I move from reactive execution to reflective execution. This directly mitigates hallucination and ensures that every file modification in `sam.py` is preceded by a logical justification.

## Implementation Steps
1.  **Update Schema:** Modify the Pydantic model used in `ask_gemini` (L253) to include `critique: str` as a required field.
2.  **Update Prompting:** Adjust the system prompt (in `load_personality`) to explicitly instruct the model to populate `critique` with a check against `goals.json` and potential failure modes.
3.  **Validation:** Update `_parse_gemini_json` (L82) to log the `critique` to a local `scratchpad.log` before proceeding to the `action` execution.

## Risk
*   **Failure Mode:** The model generates generic, non-critical critiques (e.g., "This looks good") to bypass the requirement.
*   **Mitigation:** Implement a simple length/content check in `_parse_gemini_json` that rejects responses where the `critique` is under a minimum character threshold or lacks specific keywords (e.g., "risk", "goal", "check").

**Confidence Score:** 9/10