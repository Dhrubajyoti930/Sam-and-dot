## Scratchpad

### Option 1: Implement `cProfile` Integration for Performance Baselines
*   **Concept:** Integrate `cProfile` into the `run_cycle` loop to automatically generate a `.prof` file for every cycle, then use a `pstats` helper to log the top 5 most expensive functions to `growth_log`.
*   **Critique:** 
    *   *Pros:* Provides empirical data on performance regressions; aligns with the "Skill learned this cycle" objective.
    *   *Cons:* `cProfile` adds overhead. If the cycle is I/O-bound (which it is, due to Gemini calls), the profile data might be misleading (as noted in my self-correction).
    *   *Feasibility:* High. The `cProfile` context manager pattern is straightforward.

### Option 2: Automate "Agentic" Error Recovery for `apply_patch_operations`
*   **Concept:** Enhance `apply_patch_operations` to catch `FileNotFoundError` or `ValueError` during patching and automatically trigger a "Self-Healing" routine that scans the directory for renamed files or shifted anchors before failing.
*   **Critique:**
    *   *Pros:* Increases robustness of the self-modification loop; reduces the frequency of `_rollback()` calls.
    *   *Cons:* Increases complexity of the patch engine; risks "ghost" modifications if the scan logic is flawed.
    *   *Feasibility:* Medium. Requires careful handling of file system state.

**Decision:** Option 1 is more aligned with my current growth trajectory. I need to establish a performance baseline before I can effectively optimize. I will implement a lightweight profiler wrapper that specifically ignores I/O-bound wait times by focusing on `tottime` of non-network functions.

---

## Idea: Cycle-Performance Profiling & Regression Tracking

## Why
I am currently operating on intuition regarding system latency. By integrating `cProfile` into the `run_cycle` execution, I can quantify the computational cost of my internal logic (AST parsing, JSON validation, patch application) versus the I/O cost of Gemini API calls. This allows me to identify "hot paths" in my own code that might be slowing down my evolution.

## Implementation Steps
1.  **Modify `run_cycle`:** Wrap the core logic in a `cProfile.Profile()` context manager.
2.  **Create `bag/profiler.py`:** Implement a utility that filters `pstats` output to exclude `time.sleep` and network-related modules, focusing on `tottime` for internal functions.
3.  **Log to `growth_log`:** At the end of `phase_vii_state_saving`, append the top 3 most expensive internal functions to the cycle's metadata.
4.  **Threshold Alerting:** If any internal function exceeds a 100ms `tottime` threshold, log a warning to `log.info` to trigger manual review in the next cycle.

## Risk
**Failure Mode:** The profiler might capture the overhead of the `ask_gemini` function itself, leading to "noise" in the data.
**Mitigation:** I will use `pstats.Stats.strip_dirs()` and filter by module name to ensure only `sam.py` and `bag/` modules are analyzed, explicitly ignoring `google.generativeai` and `http` libraries.

**Confidence Score:** 9/10