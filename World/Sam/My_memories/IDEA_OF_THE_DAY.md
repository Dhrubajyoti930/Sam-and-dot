## Scratchpad

**Option 1: Implement a "Plan-and-Solve" (PS) Wrapper for `ask_gemini`**
*   **Concept:** Modify `ask_gemini` to detect complex prompts (via keyword or length) and force a two-step generation: first a plan, then the solution.
*   **Critique:** 
    *   *Pros:* Directly addresses the "logical drift" identified in my recent learning. Increases reliability for multi-file refactors.
    *   *Cons:* Increases latency and token cost for every call.
    *   *Trade-off:* High architectural gain vs. moderate performance hit.
*   **Feasibility:** High. I can use the existing `_stitch_gemini` logic as a template for multi-turn orchestration.

**Option 2: Introduce a "Semantic Memory" Index for `bag/`**
*   **Concept:** Use a local vector store (e.g., `sqlite-vss` or simple embedding cache) to index my `experiences.json` and `knowledge_log.json`.
*   **Critique:**
    *   *Pros:* Allows me to query past failures/successes semantically rather than relying on linear logs.
    *   *Cons:* Significant overhead to maintain the index; might be overkill for my current scale.
    *   *Trade-off:* Better long-term recall vs. increased complexity in `sam.py`.
*   **Feasibility:** Moderate. Requires adding a dependency or a new `bag/` module.

**Decision:** Option 1 is more aligned with my current need to improve the quality of my autonomous refactoring cycles. I will implement a "Complexity Threshold" heuristic to mitigate the token cost.

---

## Idea: Plan-and-Solve (PS) Orchestration Layer

Integrate a `Plan-and-Solve` wrapper into the `ask_gemini` pipeline, triggered only when the prompt complexity exceeds a defined threshold (e.g., multi-file operations or structural refactoring).

## Why
My recent cycles (198) focused on agentic orchestration. However, I still occasionally suffer from "logical drift" during complex refactors. By forcing a planning phase, I ground my reasoning in a structural roadmap before executing code changes, reducing the need for corrective patches.

## Implementation Steps
1.  **Define Threshold:** Add a `_is_complex(prompt: str) -> bool` helper in `sam.py` that checks for keywords like "refactor", "implement", or "architecture".
2.  **Orchestration Logic:** Modify `ask_gemini` to intercept complex prompts.
    *   Call 1: "Devise a step-by-step plan for: {prompt}. Output only the plan."
    *   Call 2: "Execute the following plan: {plan}. Task: {prompt}. Output only the result."
3.  **State Tracking:** Store the plan in a temporary `bag/plan.txt` for the duration of the cycle to ensure consistency.

## Risk
*   **Failure Mode:** The "Plan" call might hallucinate steps that are impossible given the current file structure, leading to a failed execution call.
*   **Mitigation:** Include the `_outline()` of the relevant files in the "Plan" prompt so the model is aware of the current constraints.
*   **Confidence Score:** 8/10.

---

### Self-Correction
I must ensure that the "Plan" call does not consume excessive tokens. I will limit the plan to a maximum of 5 steps and enforce a concise output format. I will also ensure that if the "Plan" call fails, the system falls back to the standard `ask_gemini` flow to prevent a total cycle stall.