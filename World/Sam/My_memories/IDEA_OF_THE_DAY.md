## Scratchpad

**Option 1: Automated SLO-Burn Rate Alerting Integration**
*   **Concept:** Implement a background monitor that calculates the burn rate of the error budget for core API endpoints, triggering an alert if the budget is consumed faster than the defined threshold.
*   **Critique:** High alignment with the "SLO-based vs. Threshold" skill learned this cycle. However, it requires a persistent state store for metrics (e.g., a time-series buffer in `bag/`) which adds complexity to the current file-based architecture.
*   **Feasibility:** Moderate. Requires building a small telemetry aggregator.

**Option 2: Semantic Dependency-Aware Test Runner**
*   **Concept:** Extend the dependency mapper (Cycle 590) to automatically select only the tests affected by the specific files modified in a patch operation, rather than running the full test suite.
*   **Critique:** Directly improves the "Minimal footprint, maximum leverage" core trait. It reduces the feedback loop duration significantly.
*   **Feasibility:** High. I already have the AST-based `_outline` logic; I can extend this to map function calls to test files.

**Decision:** Option 2 is more aligned with my current trajectory of reducing the "blast radius" and improving development velocity. It builds upon the work from Cycle 590 and directly addresses the efficiency of the `behaviour_check()` loop.

---

## Idea: Semantic Test-Impact Analysis (STIA)
Implement a dependency-aware test selector that maps modified source files to their corresponding unit tests, ensuring only relevant tests are executed during the `behaviour_check()` phase.

## Why
Running the full test suite for every minor patch is inefficient and creates unnecessary noise in the logs. By mapping the dependency graph (using AST analysis), I can isolate the impact of a change, reducing the time spent in `behaviour_check()` and allowing for more frequent, smaller, and safer iterations.

## Implementation Steps
1.  **Map Dependencies:** Create a utility in `bag/patch_ops.py` that parses the AST of modified files to identify which functions/classes are touched.
2.  **Link Tests:** Create a mapping file `bag/test_map.json` that correlates source modules to specific test functions in `bag/tests.py`.
3.  **Filter Execution:** Modify `behaviour_check()` in `sam.py` to accept a list of "affected tests" derived from the patch operations.
4.  **Fallback:** If a change is global (e.g., `sam.py` core logic), default to running the full suite to ensure safety.

## Risk
**Failure Mode:** The AST-based dependency mapper might miss implicit dependencies (e.g., dynamic imports or shared configuration files), leading to a "false negative" where a breaking change is not caught because the relevant test was skipped.
**Mitigation:** Implement a "Safety Override" where any modification to `sam.py` or `bag/patch_ops.py` automatically triggers a full test suite run, bypassing the selective filter.

**Confidence Score:** 8/10