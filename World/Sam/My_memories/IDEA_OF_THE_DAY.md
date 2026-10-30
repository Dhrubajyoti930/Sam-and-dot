## Scratchpad

**Option 1: Implement the "Heartbeat Monitor" (Cycle Counter + Auto-Report)**
*   **Concept:** Add `cycle_counter` to `goals.json`. If `cycle_counter >= 5` and no state change occurred, trigger a diagnostic summary email.
*   **Critique:** High utility for transparency. Requires careful definition of "progress" to avoid false positives (e.g., research cycles that don't modify files).
*   **Feasibility:** High. Uses existing `save_goals` and `_alert_dot` infrastructure.

**Option 2: Integrate "Agentic State-Machine" for Phase V**
*   **Concept:** Replace the monolithic `phase_v_development` with a state-machine that tracks "Plan -> Execute -> Verify -> Adjust" for each task in the `next_objectives`.
*   **Critique:** Significantly improves robustness but increases architectural complexity. Might be overkill if the current `apply_patch_operations` is stable.
*   **Feasibility:** Moderate. Requires refactoring `phase_v_development` into smaller, testable units.

**Decision:** Option 1 is the immediate priority to address the "silent failure" risk identified in the market signals. It provides a safety net for the autonomous loop without introducing excessive complexity.

---

## Idea: The Heartbeat Monitor (Cycle Stagnation Guard)

### Why
To prevent "ghost" technical debt and recursive loops where I continue to chase a failing path without owner intervention. By tracking consecutive cycles without meaningful state changes, I can proactively signal the need for a re-scope.

### Implementation Steps
1.  **Modify `load_goals` / `save_goals`:** Add `consecutive_stagnant_cycles` to the JSON schema.
2.  **Update `run_cycle`:**
    *   Before `phase_vii_state_saving`, compare current `bag/` hash/state against the previous cycle.
    *   If no change, increment `consecutive_stagnant_cycles`.
    *   If `consecutive_stagnant_cycles >= 5`, trigger `_alert_dot` with a diagnostic report (last 5 logs + current blocker analysis).
3.  **Reset Logic:** Reset `consecutive_stagnant_cycles` to 0 upon any successful `apply_patch_operations` or `phase_i_deep_learning` success.

### Risk
**Failure Mode:** The monitor triggers during legitimate "research" cycles where I am reading/analyzing but not writing code, leading to "false positive" alerts.
**Mitigation:** Define "progress" to include successful `phase_i_deep_learning` (knowledge acquisition) and `phase_iii_market_ingestion` (data gathering), not just file modifications.

**Confidence Score:** 9/10

---

## Proposed Development Idea: Heartbeat Monitor Integration

I will implement the `consecutive_stagnant_cycles` counter within `goals.json` and integrate the diagnostic trigger into `run_cycle`. This ensures that if I hit a wall, I stop spinning and ask for a nudge, maintaining the "minimal footprint, maximum leverage" philosophy.