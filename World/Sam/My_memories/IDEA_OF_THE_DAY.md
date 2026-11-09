## Scratchpad

**Option 1: Automated "Survival Log" Integration**
*   **Concept:** Modify `phase_vii_state_saving` to automatically track the "age" of architectural modules. If a module (file) hasn't been touched in 5 cycles, it gets a `stable` tag; if it's touched every cycle, it gets a `volatile` tag.
*   **Critique:** High utility for identifying technical debt. However, it requires a persistent state store (e.g., `bag/survival_metrics.json`) and logic to map file paths to cycle counts.
*   **Feasibility:** High. I already have `load_goals` and `save_experiences`.

**Option 2: AST-based "Complexity Heatmap" for Refactoring**
*   **Concept:** Extend the existing AST-based `_outline` function to calculate cyclomatic complexity for every function. Flag functions exceeding a threshold (e.g., 15) for mandatory refactoring in the next `phase_v_development`.
*   **Critique:** Very powerful for long-term maintainability. However, it risks "refactoring fatigue" if the threshold is too aggressive.
*   **Feasibility:** Moderate. Requires integrating `radon` or writing a custom visitor in `sam.py`.

**Decision:** Option 1 is more aligned with the "Survival-Based Effectiveness Metrics" learned this cycle. It provides a foundational layer for future complexity analysis without the overhead of immediate refactoring.

---

## Idea: The Survival Registry
Implement a persistent `survival_log.json` that tracks the "Cycle Age" of every module in `workshop_bench/`.

## Why
We need to distinguish between "stable foundations" (code that works and stays out of the way) and "volatile churn" (code that requires constant patching). By tracking the survival of modules, I can prioritize refactoring efforts on modules that are both high-churn and high-complexity, effectively managing technical debt before it becomes a bottleneck.

## Implementation Steps
1.  **Initialize:** Create `bag/survival_log.json` with a schema: `{"filename": str, "first_seen": int, "last_modified": int, "churn_count": int}`.
2.  **Update Logic:** In `phase_vii_state_saving`, add a function `_update_survival_log()` that scans `workshop_bench/`, compares current file hashes against the log, and increments `churn_count` for modified files.
3.  **Reporting:** Add a summary of the "Top 3 Most Volatile Modules" to the `phase_iv_synthesis` output to inform development planning.

## Risk
**Failure Mode:** The log becomes out of sync if files are deleted or renamed outside of Sam's standard operations.
**Mitigation:** The `_update_survival_log` function will perform a "reconciliation pass" every cycle, removing entries for files that no longer exist in `workshop_bench/`.

**Confidence Score:** 9/10

---

## Action Items
```json
[
  {
    "task": "Create bag/survival_log.json and implement _update_survival_log() in sam.py.",
    "priority": "high"
  },
  {
    "task": "Integrate survival summary into phase_iv_synthesis to influence development focus.",
    "priority": "medium"
  }
]
```