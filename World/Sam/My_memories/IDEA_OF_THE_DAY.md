## Scratchpad

**Option 1: Automated Complexity Variance Tracking**
*   **Concept:** Integrate a decorator or context manager to wrap `apply_patch_operations` and `ask_gemini` to measure wall-clock time vs. estimated complexity.
*   **Critique:** High utility for the "Complexity Variance" action item. However, it risks adding significant overhead to the `sam.py` core logic and might be brittle if Gemini's response time varies due to network latency rather than task complexity.
*   **Feasibility:** High.

**Option 2: Agentic "Self-Reflection" Loop (Post-Cycle)**
*   **Concept:** Before `phase_vii_state_saving`, add a `phase_vi_b_reflection` that analyzes the `GAR` (Goal Achievement Rate) and `WAR` (Weighted Achievement Rate) calculated in the current cycle.
*   **Critique:** This directly addresses the "gaming the metric" weakness identified in the self-correction. It forces an explicit justification for why a task was "Deferred" or "Abandoned," preventing hidden debt.
*   **Feasibility:** Moderate. Requires modifying the `run_cycle` flow and adding a new prompt template.

**Selection:** Option 2. It aligns with the "Disciplined curiosity" and "Honest self-assessment" traits by formalizing the accountability loop.

---

## Idea: Implementation of the "Reflective Achievement Audit" (RAA)

## Why
Currently, my GAR/WAR metrics are lagging indicators. By introducing a mandatory reflection phase, I transform them into active feedback loops. This prevents the accumulation of "hidden debt" by forcing a classification of non-completed tasks before the state is saved, ensuring my growth metrics remain grounded in reality.

## Implementation Steps
1.  **Modify `run_cycle`:** Insert `phase_vi_b_reflection` between `phase_vi_cognitive_evolution` and `phase_vii_state_saving`.
2.  **Create `phase_vi_b_reflection`:**
    *   Input: Current cycle's `next_objectives` and the status of each.
    *   Logic: If any task is not "Completed," require a reason code (Abandoned, Deferred, Failed).
    *   Output: A JSON summary of the "Complexity Variance" (Estimated vs. Actual effort) to be appended to `growth_log`.
3.  **Update `load_goals`:** Ensure the schema supports the new "reason code" metadata for tasks.

## Risk
**Failure Mode:** The reflection phase becomes a "rubber stamp" where I provide generic justifications to maintain a high GAR.
**Mitigation:** I will mandate that any "Deferred" or "Failed" task requires a specific reference to a dependency or a technical blocker identified in the `log`. If the justification is too vague, the `self_check` or a secondary validation prompt will flag it for manual review by Dot.

**Confidence Score:** 9/10