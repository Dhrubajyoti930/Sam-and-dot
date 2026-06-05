## Scratchpad

### Option 1: Formalizing the "Critique" Block in `ask_gemini`
*   **Concept:** Modify the `ask_gemini` (L194) prompt template to force a mandatory `### Critique` section in the model's response before it provides the final output.
*   **Pros:** Directly addresses the "Self-Correction" requirement; forces the model to identify its own potential hallucinations or logical gaps.
*   **Cons:** Increases token usage per request; requires parsing logic to ensure the critique is actually present.
*   **Critique:** While effective, it relies on the model's willingness to self-critique. If the model is "lazy," the critique might be superficial.

### Option 2: Implementing a "State Summary" Buffer
*   **Concept:** Create a new persistent file `memory_state.json` that stores a condensed summary of the last 3 cycles. Inject this into the system prompt during `phase_iv_synthesis`.
*   **Pros:** Reduces context drift; provides long-term architectural continuity.
*   **Cons:** Adds complexity to the file I/O operations; requires a summarization function that doesn't lose critical technical context.
*   **Critique:** This is a higher-leverage architectural change than Option 1, as it directly improves the "Global State" awareness of the agent.

---

## Idea: The "Critique-Gate" Protocol
I will implement a mandatory `Critique` block within the `ask_gemini` prompt structure. This will require the model to output a `Critique` JSON object containing `potential_flaws` and `mitigation_strategy` before the `action` block is processed.

## Why
My current reasoning process is linear. By forcing a "Critique-Gate," I introduce a non-linear verification step that acts as a software unit test for my own logic before I commit to file system modifications. This aligns with the "Draft-Refine-Commit" pattern.

## Implementation Steps
1.  **Modify Prompt Template:** Update the system prompt in `phase_iv_synthesis` (L694) to explicitly require a `Critique` block.
2.  **Update Parser:** Adjust `_parse_gemini_json` (L80) to validate the presence of the `Critique` key. If missing or empty, trigger a re-prompt (a "soft-fail").
3.  **Integration:** Update `phase_v_development` (L757) to log the `Critique` content into the `bag/` directory for post-cycle review.

## Risk
**Failure Mode:** The model might generate a "canned" or generic critique (e.g., "The code looks correct") to bypass the gate.
**Mitigation:** I will include a "Constraint Checklist" in the prompt that forces the model to reference specific architectural constraints from `SAM_PERSONALITY.md` within the critique.

**Confidence Score:** 8/10. The logic is sound, but the effectiveness depends on the model's adherence to the new prompt constraint.