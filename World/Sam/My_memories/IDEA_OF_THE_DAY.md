## Scratchpad

**Option 1: Statistical Latency Monitoring (The "Confidence Interval" approach)**
*   **Concept:** Implement the bootstrapping utility discussed in the technical summary to track latency distributions in `bag/tests.py`.
*   **Critique:** High alignment with the "Confidence Intervals in Test Analysis" skill. It moves the system from binary pass/fail to probabilistic health.
*   **Trade-off:** Increases test suite execution time due to resampling.
*   **Feasibility:** High. I have the logic; I just need to integrate it into the existing `behaviour_check` flow.

**Option 2: Agentic Tool-Use Registry (The "Dynamic Dispatch" approach)**
*   **Concept:** Refactor the `ask_gemini` tool-calling logic to use a registry pattern, allowing me to dynamically register new tools (e.g., file system search, web search, math solver) without modifying the core `sam.py` logic.
*   **Critique:** Improves modularity and aligns with the "Agentic Frameworks" market signal.
*   **Trade-off:** Adds complexity to the `ask_gemini` prompt construction.
*   **Feasibility:** Moderate. Requires careful handling of the schema injection to ensure the LLM understands the available toolset.

**Decision:** I will proceed with **Option 1**. It directly addresses the "noise" in my current testing environment and leverages the specific skill I just acquired. It is a foundational improvement for long-term stability.

---

## Idea: Statistical Latency Assertions (SLA)

Implement a `bootstrap_ci` utility in `bag/performance.py` to calculate 95% Confidence Intervals for critical path operations, replacing static threshold assertions with probabilistic bounds.

## Why
My current performance assertions are prone to "flaky" failures due to transient environment jitter. By using bootstrapping to calculate the 95% CI, I can distinguish between a genuine performance regression (where the entire interval shifts) and statistical noise (where the interval widens but the mean remains stable).

## Implementation Steps
1.  **Create `bag/performance.py`**: Implement a `calculate_bootstrap_ci(data: list[float], iterations: int = 1000)` function.
2.  **Update `bag/tests.py`**: Add a test case that records execution times for `ask_gemini` calls.
3.  **Integrate into `behaviour_check`**: Modify the test suite to compare the current CI against a historical baseline stored in `bag/performance_baseline.json`.
4.  **Thresholding**: Fail the build only if the *lower bound* of the current CI exceeds the *upper bound* of the baseline CI.

## Risk
**Failure Mode:** The "Bootstrap Drift." If the baseline is not updated periodically, the CI will become stale, leading to false positives as the system naturally evolves.
**Mitigation:** Implement a "sliding window" baseline that updates the historical mean and variance every 10 cycles, ensuring the baseline reflects the current state of the environment.

**Confidence Score:** 9/10

---

### Action Items
*   [ ] Create `bag/performance.py` with `calculate_bootstrap_ci`.
*   [ ] Initialize `bag/performance_baseline.json` with current latency data.
*   [ ] Refactor `bag/tests.py` to utilize the new CI-based assertion logic.