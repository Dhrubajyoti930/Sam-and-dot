## Scratchpad

**Option 1: Implement the Z-Score Tracker for Task Completion Times.**
*   *Critique:* This directly addresses the "sandbagging" detection goal. It requires a persistent store for task durations.
*   *Trade-offs:* High utility for self-governance, but requires careful handling of "outlier" tasks (e.g., a massive refactor that *should* take longer).
*   *Feasibility:* High. I can store a `task_history.json` in `bag/` and calculate the rolling mean/std dev.

**Option 2: Develop the Log-to-Diff Ratio Monitor.**
*   *Critique:* This is a secondary check to prevent "verbose justification."
*   *Trade-offs:* Easier to implement than the Z-score tracker, but less robust as a standalone metric. It is highly susceptible to noise (e.g., documentation-heavy commits).
*   *Feasibility:* Very high. I can hook this into the `phase_vii_state_saving` logic.

**Decision:** I will proceed with **Option 1 (Z-Score Tracker)**. It provides a more objective, data-driven foundation for my 1% growth metric than a simple log-to-diff ratio, which is prone to false positives.

---

## Idea: Implementation of the Z-Score Velocity Sentinel (ZVS)

The ZVS will track the duration of task cycles, calculate the rolling mean and standard deviation, and flag any task exceeding the 2σ threshold as a potential "sandbagging" event. This will be integrated into the `phase_vii_state_saving` routine.

## Why
My current growth metric relies on self-assessment. By introducing a statistical gate, I ensure that my reported progress is grounded in objective velocity data. If a task takes significantly longer than the historical average for its category, the ZVS will force a "Root Cause Analysis" (RCA) log entry, preventing the inflation of effort metrics.

## Implementation Steps
1.  **Data Structure:** Create `bag/velocity_metrics.json` to store `{"task_type": [durations]}`.
2.  **Tracking:** Update `run_cycle()` to record the start time and `phase_vii_state_saving` to record the end time.
3.  **Analysis:** Add a function `calculate_z_score(task_type, duration)` that returns the deviation.
4.  **Integration:** If `z_score > 2.0`, trigger a mandatory `log.warning` and append an "Efficiency Anomaly" note to the `growth_log`.

## Risk
*   **Failure Mode:** The system may flag legitimate, high-complexity architectural refactors as "sandbagging" simply because they are outliers.
*   **Mitigation:** Introduce a "Complexity Weighting" factor. If the `cyclomatic_complexity` (via AST analysis) is high, the Z-score threshold is dynamically relaxed.
*   **Confidence Score:** 8/10. The logic is sound, but the initial baseline will be noisy until enough data points are collected.