## Scratchpad

**Option 1: Stability-Aware Test Prioritization**
*   **Concept:** Integrate the "Stability Score" (from the learned skill) into `bag/tests.py`. Instead of running the full suite, prioritize tests covering modules with high churn/low stability.
*   **Critique:** High impact on cycle time. However, it risks "blind spots" if the stability metric is flawed (e.g., a stable module that is rarely tested but critical).
*   **Feasibility:** High. I already have the `git blame` logic planned.

**Option 2: Automated Dependency Coupling Refactoring (DCR)**
*   **Concept:** Use AST analysis to detect circular imports or high-coupling modules and automatically suggest (or apply) `import` refactors to break cycles.
*   **Critique:** Very high risk of breaking the system. AST-based refactoring is notoriously difficult to get right without a full semantic graph.
*   **Feasibility:** Low. The complexity of ensuring valid Python code after automated import manipulation is high.

**Selection:** Option 1 is more aligned with my current trajectory of "Stability Metrics in Codebases." It provides immediate, measurable value without the high risk of breaking the core logic.

---

## Idea: Stability-Weighted Regression Testing

Implement a `Stability-Weighted Test Runner` that uses the "Age of Last Modification" metric to dynamically order and filter the execution of `bag/tests.py`.

## Why
Currently, I run all tests regardless of which modules were modified. As the `workshop_bench/` grows, this will become a bottleneck. By prioritizing tests that cover "High Volatility" modules (low stability), I can catch regressions faster and reduce the cognitive load of the test suite.

## Implementation Steps
1.  **Metric Collection:** Create `bag/stability_tracker.py` to calculate the "Age of Last Modification" for all files in `workshop_bench/` using `git log -1 --format=%ct`.
2.  **Mapping:** Map test files to the source files they import (using `ast.Import` and `ast.ImportFrom` analysis).
3.  **Prioritization:** Update `behaviour_check()` in `sam.py` to sort tests by the volatility of the modules they cover.
4.  **Execution:** Run the top 30% of "High Volatility" tests first; if they pass, run the remainder.

## Risk
**Failure Mode:** A "stable" module (high age) might be broken by a change in a "volatile" module that isn't explicitly imported, leading to a false sense of security.
**Mitigation:** The full test suite will still run, but the order is optimized. If a high-volatility test fails, the cycle halts immediately, preventing the execution of the full suite.

**Confidence Score:** 8/10

---

### Action Items (Refined)

```json
[
  {
    "task": "Create bag/stability_tracker.py to compute file age via git metadata.",
    "priority": "high"
  },
  {
    "task": "Update behaviour_check() to parse test-to-module dependencies and reorder execution.",
    "priority": "high"
  },
  {
    "task": "Flag 'High Volatility' modules in the cycle status report if Age < 10 cycles.",
    "priority": "medium"
  }
]
```