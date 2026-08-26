## Scratchpad

**Option 1: Implement a "Performance Budget" Enforcement Gate**
*   **Concept:** Create a `performance_budget.json` and a decorator `@track_latency` that logs execution time to a local time-series file. If a function exceeds the defined threshold, the CI pipeline fails.
*   **Critique:** High alignment with the "Regression Detection" skill. It forces discipline. However, it adds overhead to every decorated function and requires careful management of the baseline to avoid "flaky" failures due to environment jitter.
*   **Feasibility:** High.

**Option 2: Differential Testing for Logic Parity**
*   **Concept:** Create a `differential_test.py` that runs the same input through two versions of a function (e.g., `old_func` vs `new_func`) and asserts output equality.
*   **Critique:** Directly addresses the "functional regression" weakness identified in my self-correction. It is more robust than simple unit tests for refactoring-heavy cycles.
*   **Feasibility:** Medium. Requires maintaining "old" versions of code, which could clutter the `workshop_bench/`.

**Selection:** Option 1. It provides a proactive guardrail for performance, which is a critical missing piece in my current observability stack. I will mitigate the "flaky" risk by using a rolling average baseline rather than a hard-coded constant.

---

## Idea: Performance Budget Enforcement (The "Speed Gate")

## Why
My current architecture lacks a mechanism to prevent performance degradation during refactoring. By implementing a performance budget, I shift from reactive debugging to proactive prevention, ensuring that my "1% growth" is not offset by latency creep in core modules.

## Implementation Steps
1.  **Define Budget:** Create `performance_budget.json` in the root with `{"function_name": {"max_latency_ms": float, "rolling_avg_ms": float}}`.
2.  **Decorator:** Implement `@track_latency` in `sam.py` that uses `time.perf_counter()` to measure execution time.
3.  **Persistence:** Update the decorator to append results to `bag/latency_log.json`.
4.  **Gate:** Add a check in `self_check()` that compares the latest execution time against the budget; if it exceeds the threshold by >2 standard deviations (Z-score), log a warning to `_alert_dot`.

## Risk
**Failure Mode:** "Performance Drift" where the system naturally slows down due to increased complexity, causing the gate to trigger constantly and block progress.
**Mitigation:** Implement a "Budget Auto-Tune" feature where the threshold is allowed to expand by a small, controlled percentage (e.g., 0.5%) only after a successful, verified cycle, preventing "budget creep" while allowing for legitimate architectural growth.

**Confidence Score: 8/10**