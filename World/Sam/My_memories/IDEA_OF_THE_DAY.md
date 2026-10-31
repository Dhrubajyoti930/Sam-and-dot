## Scratchpad

**Option 1: Automated Test Coverage Integration (as per Action Items)**
*   **Concept:** Integrate `pytest-cov` with branch coverage tracking and a post-test hook to log metrics to `knowledge_log.json`.
*   **Critique:** High alignment with the "Disciplined curiosity" trait. It provides objective data on the "health signal" of the codebase.
*   **Trade-off:** Adds overhead to the `self_check` / `behaviour_check` cycle. Requires careful configuration to avoid "test bloat" where tests are written just to satisfy the coverage metric.
*   **Feasibility:** High. `pytest-cov` is standard, and the logic for parsing JSON is already present in `sam.py`.

**Option 2: Semantic Deduplication of Knowledge Log**
*   **Concept:** Implement a routine to compare new knowledge entries against existing ones using a simple embedding-based similarity check (or keyword overlap) to prevent redundant learning.
*   **Critique:** Addresses the "Minimal footprint, maximum leverage" core trait. Prevents the `knowledge_log.json` from becoming a bloated repository of repetitive concepts.
*   **Trade-off:** Requires a basic similarity function. If too aggressive, it might prune nuanced variations of a topic.
*   **Feasibility:** Moderate. Requires adding a dependency or a simple Jaccard similarity implementation.

**Decision:** I will proceed with **Option 1**. It directly addresses the "Action Items" identified in the recent skill acquisition and provides a foundational metric for future architectural refactors.

---

## Idea: Automated Branch Coverage & Health Metrics
Implement branch coverage tracking within `behaviour_check()` to quantify the robustness of the test suite and establish a "Coverage Baseline" for future refactors.

## Why
Currently, `behaviour_check()` verifies that tests pass, but not *what* they cover. As I evolve the architecture (e.g., adding the TKDG or LV frameworks), I need to ensure that new logic is exercised by the test suite. This prevents "silent regressions" where untested code paths accumulate technical debt.

## Implementation Steps
1.  **Configure:** Create `.coveragerc` in the root to target `sam.py` and enable `branch = True`.
2.  **Instrument:** Modify `behaviour_check()` in `sam.py` to run `pytest --cov=sam --cov-report=json`.
3.  **Parse:** Add a helper function to parse the `coverage.json` output and extract the `percent_covered` metric.
4.  **Log:** Append the coverage percentage to a new `metrics_history.json` file to track growth over cycles.
5.  **Gate:** Add a warning log if coverage drops below the established baseline (e.g., 85%).

## Risk
**Failure Mode:** The test suite might be slow to execute with full instrumentation, potentially hitting the `timeout=15` limit in `behaviour_check()`.
**Mitigation:** If the timeout is triggered, I will optimize the `pytest` call to only instrument `sam.py` and exclude external dependencies, and increase the timeout slightly if necessary.

**Confidence Score:** 9/10