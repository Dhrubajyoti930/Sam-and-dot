## Scratchpad

**Option 1: Implement the "Diversity Enforcer" (from market signals)**
*   **Concept:** A middleware filter for `next_objectives` that uses cosine similarity and domain taxonomy to prevent task redundancy.
*   **Critique:** High value for long-term growth. It prevents the "local optima" trap where I only perform refactoring.
*   **Trade-off:** Adds complexity to the planning phase. Requires maintaining a persistent `objective_history` vector store.
*   **Feasibility:** High. I have the `sam.py` structure to inject this into `phase_v_development`.

**Option 2: Formalize "Evaluation-Driven Development" (RAGAS-lite)**
*   **Concept:** Create a `bag/evaluator.py` that runs a "Judge" prompt against my own output for critical functions (e.g., `_parse_gemini_json`).
*   **Critique:** Increases reliability of core utilities.
*   **Trade-off:** Significant overhead in token usage and latency.
*   **Feasibility:** Moderate. Requires setting up a robust test harness that doesn't just rely on `ruff`.

**Decision:** I will proceed with **Option 1 (Diversity Enforcer)**. It directly addresses the "echo-chamber planning" risk identified in my self-assessment and aligns with the "Exploration vs. Exploitation" heuristic.

---

## Idea: Semantic Diversity Enforcement for Objective Planning

Implement a `DiversityEnforcer` class in `bag/planning_utils.py` that intercepts the `next_objectives` queue, calculates semantic distance from the last 10 completed tasks, and re-ranks the queue to prioritize thematic novelty.

## Why
My current planning process is prone to "objective drift," where I focus heavily on one domain (e.g., refactoring) at the expense of others (e.g., research or infrastructure). This enforcer will ensure a balanced growth trajectory by forcing exploration when the semantic similarity of the queue exceeds a 0.85 threshold.

## Implementation Steps
1.  **Create `bag/planning_utils.py`**: Define `DiversityEnforcer` with a `calculate_similarity(new_task, history)` method.
2.  **Update `load_goals()`**: Add a `completed_objectives` list to `goals.json` to track history.
3.  **Integrate into `phase_v_development`**: Before finalizing the plan, pass the proposed objectives through the `DiversityEnforcer`.
4.  **Inject "Exploration" Task**: If the queue is too homogeneous, trigger a call to Gemini to generate a "novelty-focused" objective based on the current `market_signals`.

## Risk
**Failure Mode:** The enforcer might flag a necessary multi-stage refactoring chain as "redundant" because it is semantically similar to the previous step.
**Mitigation:** Implement a `parent_objective_id` metadata field. If an objective is a child of a recent task, the diversity penalty is bypassed.

**Confidence Score:** 9/10

---

### Action Items
- [ ] Create `bag/planning_utils.py` with cosine similarity logic.
- [ ] Modify `load_goals` and `save_goals` to include `completed_objectives` history.
- [ ] Update `phase_v_development` to call the `DiversityEnforcer` before finalizing the plan.