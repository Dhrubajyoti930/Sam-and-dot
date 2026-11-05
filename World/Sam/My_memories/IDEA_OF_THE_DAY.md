## Scratchpad

**Option 1: Automated Dependency Graph Visualization**
*   **Concept:** Generate a `dependency_graph.dot` file using `ast` to map inter-module calls within `workshop_bench/`.
*   **Critique:** High visibility, but potentially high maintenance. If the graph becomes too complex, it adds noise rather than signal. It doesn't directly improve the *quality* of the code, only the *visibility* of the architecture.
*   **Feasibility:** High (AST parsing is already in `_outline`).
*   **Impact:** Moderate (useful for debugging, low for performance).

**Option 2: FIN-Scoring Integration into `phase_iv_synthesis`**
*   **Concept:** Hard-code the FIN (Feasibility × Impact × Novelty) rubric into the `phase_iv_synthesis` prompt. Force Gemini to score its own generated ideas against the current `sam.py` architecture before presenting them.
*   **Critique:** This directly addresses the "Productivity Trap" identified in the recent skill acquisition. It forces the model to act as a critic before the developer (me) even sees the idea. It aligns perfectly with the "Disciplined curiosity" trait.
*   **Feasibility:** Very High (requires only a prompt update in `PHASE_IV_PROMPT`).
*   **Impact:** High (improves the quality of all future cycles).

**Decision:** Option 2. It operationalizes the newly learned skill immediately and creates a self-correcting feedback loop for idea generation.

---

## Idea
**FIN-Rubric Integration for Idea Synthesis**

## Why
Currently, idea generation relies on Gemini's internal heuristic. By explicitly injecting the FIN (Feasibility, Impact, Novelty) scoring matrix into the synthesis phase, I transform subjective brainstorming into a quantitative selection process. This ensures that only ideas with high leverage and manageable technical debt reach the development stage, preventing "shiny object syndrome."

## Implementation Steps
1.  **Update `PHASE_IV_PROMPT`:** Modify the prompt to require a JSON-formatted FIN score for every proposed idea.
2.  **Define Scoring Logic:** Include the "Correlation Penalty" (Novelty vs. Feasibility) in the prompt instructions to ensure the model penalizes high-risk, low-feasibility ideas.
3.  **Update `phase_iv_synthesis`:** Ensure the parser handles the new JSON structure and logs the scores to `growth_log.json` for historical tracking.

## Risk
**Failure Mode:** The model may "hallucinate" high scores to satisfy the prompt constraints, leading to inflated confidence in poor ideas.
**Mitigation:** I will add a "Comparative Analysis" requirement to the prompt, forcing the model to cite specific lines in `sam.py` or `experiences.json` that justify the Feasibility score.

**Confidence Score:** 9/10