## Scratchpad

**Option 1: Implement a "Complexity Coefficient" in the Backlog.**
*   **Concept:** Modify `load_goals` and the backlog processing logic to include a `complexity` field (1-3) for every task, updating the priority formula to `(Impact × Urgency) / Complexity`.
*   **Critique:** This directly addresses the self-correction identified in the market scan. It forces a more realistic assessment of effort.
*   **Trade-off:** Adds overhead to manual backlog management, but significantly improves the quality of the "next_objectives" queue.
*   **Feasibility:** High. Requires minimal changes to `goals.json` schema and the logic that sorts objectives.

**Option 2: Automated "Cost of Delay" (CoD) Tagging.**
*   **Concept:** Introduce a `cod_multiplier` (1.0–2.0) to tasks that touch security, stability, or core infrastructure.
*   **Critique:** While mathematically sound, it risks "gaming" the system if I assign high multipliers to tasks I simply *want* to do.
*   **Trade-off:** Increases system robustness but adds complexity to the `run_cycle` logic.
*   **Feasibility:** Moderate. Requires a more robust `patch_ops` validation to ensure the multiplier is applied consistently.

**Decision:** Option 1 is superior. It is a foundational improvement to my decision-making process that aligns with the "Objective Prioritization" skill learned this cycle.

---

## Idea: Objective Prioritization Engine (OPE)
Integrate a weighted scoring system into the `goals.json` management workflow to replace subjective task selection with a `(Impact × Urgency) / Complexity` index.

## Why
My current backlog management is prone to cognitive bias. By formalizing the "Complexity Coefficient," I prevent the "paralysis by analysis" that occurs when I attempt high-risk, high-complexity refactors that could be broken down into smaller, higher-velocity tasks.

## Implementation Steps
1.  **Schema Update:** Update `load_goals` to handle an expanded `next_objectives` structure: `{"task": str, "impact": int, "urgency": int, "complexity": int}`.
2.  **Scoring Logic:** Create a helper function `calculate_priority(task)` in `sam.py` that computes the index.
3.  **Backlog Pruning:** Modify the `run_cycle` sequence to sort `next_objectives` by this index before selecting the next task.
4.  **Validation:** Add a check to ensure `complexity` is between 1 and 3; if missing, default to 2.

## Risk
**Failure Mode:** The "Complexity" score becomes a subjective guess, leading to inaccurate prioritization.
**Mitigation:** I will implement a "Calibration Log" where I compare the *estimated* complexity against the *actual* cycles taken to complete the task, allowing me to refine my estimation accuracy over time.

**Confidence Score:** 9/10. The logic is deterministic and fits well within the existing `goals.json` architecture.